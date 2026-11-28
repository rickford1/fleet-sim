import os

import yaml
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch_ros.actions import Node


def generate_launch_description():
    gazebo_pkg = get_package_share_directory('gazebo_ros')
    sim_pkg = get_package_share_directory('fleet_sim_gazebo')
    description_pkg = get_package_share_directory('fleet_robot_description')
    localization_pkg = get_package_share_directory('fleet_localization')
    bringup_pkg = get_package_share_directory('fleet_bringup')

    world_file = os.path.join(sim_pkg, 'worlds', 'fleet_world.world')

    robots_file = os.path.join(bringup_pkg, 'config', 'robots.yaml')
    with open(robots_file, 'r') as f:
        robots = yaml.safe_load(f)['robots']

    gazebo = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(gazebo_pkg, 'launch', 'gazebo.launch.py')
        ),
        launch_arguments={'world': world_file}.items(),
    )

    actions = [gazebo]

    for robot in robots:
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
                '-x', str(robot['x']),
                '-y', str(robot['y']),
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
