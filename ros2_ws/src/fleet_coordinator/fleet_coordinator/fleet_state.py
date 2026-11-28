"""Fleet state: tracks every robot's pose and shares it with the others.

For each robot in robots.yaml, this node reads its map->base_link transform
(AMCL's map->odom plus the EKF's odom->base_link) from that robot's own TF
topic (/robotN/tf), and publishes the *other* robots' footprints as a
PointCloud2 on /robotN/fleet_obstacles. Each robot's Nav2 costmaps take that
cloud as an obstacle source, so robots avoid each other based on known
positions instead of having to detect each other with lidar.

This is the first piece of the central coordinator; the scheduler will build
on the same per-robot pose tracking.
"""
import math
import os

import rclpy
import yaml
from ament_index_python.packages import get_package_share_directory
from rclpy.duration import Duration
from rclpy.node import Node
from rclpy.qos import DurabilityPolicy, QoSProfile
from rclpy.time import Time
from sensor_msgs.msg import PointCloud2
from sensor_msgs_py import point_cloud2
from std_msgs.msg import Header
from tf2_msgs.msg import TFMessage
from tf2_ros import Buffer, TransformException


class FleetState(Node):

    def __init__(self):
        super().__init__('fleet_state')

        default_robots = os.path.join(
            get_package_share_directory('fleet_bringup'), 'config', 'robots.yaml')
        robots_file = self.declare_parameter('robots_file', default_robots).value
        # Covers the other robot's chassis (half-diagonal 0.25 m) plus a margin.
        self.footprint_radius = self.declare_parameter('footprint_radius', 0.30).value
        self.point_spacing = self.declare_parameter('point_spacing', 0.05).value
        # Points sit at the lidar's scan height, so normal lidar raytracing clears a
        # robot's old spot from the costmap once it has moved on.
        self.point_height = self.declare_parameter('point_height', 0.29).value
        # Ignore a robot whose pose is older than this (e.g. its stack went down).
        self.max_pose_age = self.declare_parameter('max_pose_age', 1.0).value
        rate = self.declare_parameter('publish_rate', 10.0).value

        with open(robots_file, 'r') as f:
            self.robot_names = [r['name'] for r in yaml.safe_load(f)['robots']]

        static_qos = QoSProfile(depth=100, durability=DurabilityPolicy.TRANSIENT_LOCAL)

        # Each robot has its own TF topic, and a stock TransformListener only listens
        # on /tf, so keep one buffer per robot and feed it from that robot's topics.
        self.buffers = {}
        self.obstacle_pubs = {}
        for name in self.robot_names:
            buf = Buffer(cache_time=Duration(seconds=5.0))
            self.buffers[name] = buf
            self.create_subscription(
                TFMessage, f'/{name}/tf',
                lambda msg, b=buf: self._on_tf(msg, b, static=False), 100)
            self.create_subscription(
                TFMessage, f'/{name}/tf_static',
                lambda msg, b=buf: self._on_tf(msg, b, static=True), static_qos)
            self.obstacle_pubs[name] = self.create_publisher(
                PointCloud2, f'/{name}/fleet_obstacles', 10)

        self._disc = self._make_disc()
        self.create_timer(1.0 / rate, self._publish)
        self.get_logger().info(f'Tracking robots: {", ".join(self.robot_names)}')

    def _on_tf(self, msg, buf, static):
        for t in msg.transforms:
            if static:
                buf.set_transform_static(t, 'fleet_state')
            else:
                buf.set_transform(t, 'fleet_state')

    def _make_disc(self):
        """Filled disc of (dx, dy) offsets covering one robot's footprint."""
        r, step = self.footprint_radius, self.point_spacing
        n = int(r / step)
        return [(i * step, j * step)
                for i in range(-n, n + 1) for j in range(-n, n + 1)
                if math.hypot(i * step, j * step) <= r]

    def _robot_xy(self, name, now):
        try:
            t = self.buffers[name].lookup_transform('map', 'base_link', Time())
        except TransformException:
            return None  # not localized yet (no 2D Pose Estimate) or no TF yet
        age = (now - Time.from_msg(t.header.stamp)).nanoseconds * 1e-9
        if age > self.max_pose_age:
            return None
        return t.transform.translation.x, t.transform.translation.y

    def _publish(self):
        now = self.get_clock().now()
        poses = {name: self._robot_xy(name, now) for name in self.robot_names}
        header = Header(stamp=now.to_msg(), frame_id='map')
        z = self.point_height

        for name in self.robot_names:
            points = []
            for other, xy in poses.items():
                if other == name or xy is None:
                    continue  # never mark a robot's own footprint in its own costmap
                points.extend((xy[0] + dx, xy[1] + dy, z) for dx, dy in self._disc)
            self.obstacle_pubs[name].publish(point_cloud2.create_cloud_xyz32(header, points))


def main(args=None):
    rclpy.init(args=args)
    node = FleetState()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.try_shutdown()


if __name__ == '__main__':
    main()
