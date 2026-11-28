import os

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node
from launch_ros.descriptions import ParameterFile
from nav2_common.launch import RewrittenYaml


def generate_launch_description():
    pkg_share = get_package_share_directory('fleet_localization')
    ekf_params_file = os.path.join(pkg_share, 'config', 'ekf.yaml')

    use_sim_time = LaunchConfiguration('use_sim_time')
    namespace = LaunchConfiguration('namespace')

    # A plain "ekf_filter_node: {ros__parameters: ...}" yaml only matches a node
    # with that exact relative name - it does NOT match once the node is pushed
    # into a namespace (e.g. /robot2/ekf_filter_node). RewrittenYaml nests the
    # whole file under the namespace at launch time ({robot2: {ekf_filter_node:
    # ...}}) so it matches correctly; when namespace is empty (single-robot) it
    # leaves the file alone. Same trick nav2_bringup's own launch files use.
    configured_params = ParameterFile(
        RewrittenYaml(
            source_file=ekf_params_file,
            root_key=namespace,
            param_rewrites={},
            convert_types=True,
        ),
        allow_substs=True,
    )

    return LaunchDescription([
        DeclareLaunchArgument(
            'use_sim_time',
            default_value='true',
            description='Use simulation (Gazebo) clock if true',
        ),
        DeclareLaunchArgument(
            'namespace',
            default_value='',
            description='Namespace for this robot (e.g. robot1) when spawning more than one',
        ),
        Node(
            package='robot_localization',
            executable='ekf_node',
            name='ekf_filter_node',
            namespace=namespace,
            output='screen',
            parameters=[
                configured_params,
                {'use_sim_time': use_sim_time},
            ],
            remappings=[
                ('/tf', 'tf'),
                ('/tf_static', 'tf_static'),
                # Fused output replaces the raw wheel odom as THE /odom topic, so
                # nothing downstream (Nav2, etc.) needs to know fusion is happening.
                ('odometry/filtered', 'odom'),
            ],
        ),
    ])
