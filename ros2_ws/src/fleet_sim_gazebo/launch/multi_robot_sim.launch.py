import os

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch_ros.actions import Node

# Each entry becomes a separate robot, namespaced by its 'name' (e.g. topics
# under /robot1/..., /robot2/...). Add or remove entries to change fleet size.
ROBOTS = [
    {'name': 'robot1', 'x': '-1.5', 'y': '0.0'},
    {'name': 'robot2', 'x': '1.5', 'y': '0.0'},
]


def generate_launch_description():
    gazebo_pkg = get_package_share_directory('gazebo_ros')
    sim_pkg = get_package_share_directory('fleet_sim_gazebo')
    description_pkg = get_package_share_directory('fleet_robot_description')
    localization_pkg = get_package_share_directory('fleet_localization')

    world_file = os.path.join(sim_pkg, 'worlds', 'fleet_world.world')

    gazebo = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(gazebo_pkg, 'launch', 'gazebo.launch.py')
        ),
        launch_arguments={'world': world_file}.items(),
    )

    actions = [gazebo]

    for robot in ROBOTS:
        name = robot['name']

        robot_state_publisher = IncludeLaunchDescription(
            PythonLaunchDescriptionSource(
                os.path.join(description_pkg, 'launch', 'robot_state_publisher.launch.py')
            ),
            launch_arguments={
                'use_sim_time': 'true',
                'namespace': name,
            }.items(),
        )

        spawn_robot = Node(
            package='gazebo_ros',
            executable='spawn_entity.py',
            namespace=name,
            arguments=[
                '-topic', 'robot_description',
                '-entity', name,
                '-x', robot['x'],
                '-y', robot['y'],
                '-z', '0.05',
            ],
            output='screen',
        )

        ekf = IncludeLaunchDescription(
            PythonLaunchDescriptionSource(
                os.path.join(localization_pkg, 'launch', 'ekf.launch.py')
            ),
            launch_arguments={
                'use_sim_time': 'true',
                'namespace': name,
            }.items(),
        )

        actions.append(robot_state_publisher)
        actions.append(spawn_robot)
        actions.append(ekf)

    return LaunchDescription(actions)
