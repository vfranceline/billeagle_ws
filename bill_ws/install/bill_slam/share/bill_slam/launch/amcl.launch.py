from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.substitutions import LaunchConfiguration, PathJoinSubstitution
from launch_ros.actions import Node
from launch_ros.substitutions import FindPackageShare


def generate_launch_description():
    use_sim_time = LaunchConfiguration("use_sim_time")
    amcl_params_file = LaunchConfiguration("amcl_params_file")
    map_file = LaunchConfiguration("map_file")
    slam_params_file = LaunchConfiguration('slam_params_file')
    use_sim_time = LaunchConfiguration('use_sim_time')
    saved_map_path = LaunchConfiguration('saved_map_path')

    use_sim_time_arg = DeclareLaunchArgument(
        "use_sim_time", default_value="false", description="Use simulation/Gazebo clock"
    )

    map_file_arg = DeclareLaunchArgument(
        "map_file",
        default_value=PathJoinSubstitution([FindPackageShare("bill_slam"), "mapas", "mapa_athome_save.yaml"]),
        description="Full path to the yaml map file",
    )

    amcl_params_file_arg = DeclareLaunchArgument(
        "amcl_params_file",
        default_value=PathJoinSubstitution(
            [FindPackageShare("bill_slam"), "config", "amcl.config.yaml"]
        ),
        description="Full path to the ROS2 parameters file to use for the amcl node",
    )

    map_server_node = Node(
        package="nav2_map_server",
        executable="map_server",
        name="map_server",
        parameters=[{"use_sim_time": use_sim_time, "yaml_filename": map_file}],
    )

    amcl_node = Node(
        package="nav2_amcl",
        executable="amcl",
        name="amcl",
        parameters=[amcl_params_file, {"use_sim_time": use_sim_time}],
    )

    nav_manager = Node(
        package="nav2_lifecycle_manager",
        executable="lifecycle_manager",
        name="nav_manager",
        parameters=[
            {"use_sim_time": use_sim_time},
            {"autostart": True},
            {"node_names": ["map_server", "amcl"]},
        ],
    )
    
    slam_params_file_arg = DeclareLaunchArgument(
        'slam_params_file',
        default_value=PathJoinSubstitution(
            [FindPackageShare("bill_slam"), 'config', 'slam_toolbox_params.yaml']
        ),
        description='Full path to the ROS2 parameters file to use for the slam_toolbox node',
    )
    
    
    
    default_map_path = PathJoinSubstitution(
        [FindPackageShare("bill_slam"), 'mapas', 'mapa_athome_serial']
    )
    
    # saved_map_path_arg = DeclareLaunchArgument(     
    #     'saved_map_path',
    #     default_value=default_map_path,
    #     description='Path to the saved map'
    # )
    slam_node_saved_map = Node(
        package='slam_toolbox',
        executable='async_slam_toolbox_node',
        name='slam',
        parameters=[slam_params_file, {'use_sim_time': use_sim_time, 'map_file_name': default_map_path}],
    )

    return LaunchDescription(
        [
            use_sim_time_arg,
            amcl_params_file_arg,
            map_file_arg,
            slam_params_file_arg,
            map_server_node,
            amcl_node,
            nav_manager,
            slam_node_saved_map,
            # saved_map_path_arg
        ]
    )