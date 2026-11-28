import os

import yaml
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource


def generate_launch_description():
    bringup_dir = get_package_share_directory('nav2_bringup')
    nav_pkg = get_package_share_directory('fleet_navigation')
    fleet_pkg = get_package_share_directory('fleet_bringup')

    map_file = os.path.join(nav_pkg, 'maps', 'fleet_world_map.yaml')
    params_file = os.path.join(nav_pkg, 'config', 'nav2_params.yaml')

    robots_file = os.path.join(fleet_pkg, 'config', 'robots.yaml')
    with open(robots_file, 'r') as f:
        robots = yaml.safe_load(f)['robots']

    # One full Nav2 stack (map_server, AMCL, planner, controller, bt_navigator...)
    # per robot, each pushed into its own namespace, all pointed at the same shared
    # map - matching the robots.yaml roster that multi_robot_sim.launch.py spawns.
    actions = []
    for robot in robots:
        name = robot['name']
        actions.append(
            IncludeLaunchDescription(
                PythonLaunchDescriptionSource(
                    os.path.join(bringup_dir, 'launch', 'bringup_launch.py')
                ),
                launch_arguments={
                    'namespace': name,
                    'use_namespace': 'True',
                    'map': map_file,
                    'params_file': params_file,
                    'use_sim_time': 'true',
                }.items(),
            )
        )

    return LaunchDescription(actions)
