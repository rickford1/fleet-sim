import os
import tempfile

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource


def params_for(params_file, namespace):
    """Fill in <robot_namespace> in nav2_params.yaml ('' here: single robot)."""
    with open(params_file, 'r') as f:
        text = f.read().replace('<robot_namespace>', f'/{namespace}' if namespace else '')
    out = tempfile.NamedTemporaryFile(
        'w', suffix='.yaml', prefix=f'nav2_params_{namespace or "single"}_', delete=False)
    out.write(text)
    out.close()
    return out.name


def generate_launch_description():
    bringup_pkg = get_package_share_directory('nav2_bringup')
    nav_pkg = get_package_share_directory('fleet_navigation')

    map_file = os.path.join(nav_pkg, 'maps', 'fleet_world_map.yaml')
    params_file = params_for(os.path.join(nav_pkg, 'config', 'nav2_params.yaml'), '')

    bringup = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(bringup_pkg, 'launch', 'bringup_launch.py')
        ),
        launch_arguments={
            'map': map_file,
            'params_file': params_file,
            'use_sim_time': 'true',
        }.items(),
    )

    return LaunchDescription([bringup])
