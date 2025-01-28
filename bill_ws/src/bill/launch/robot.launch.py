import os
from launch_ros.actions import Node
from launch_ros.actions import LifecycleNode
from launch import LaunchDescription
from launch.conditions import IfCondition
from ament_index_python.packages import get_package_share_directory
from launch.substitutions import LaunchConfiguration, PythonExpression
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.actions import IncludeLaunchDescription, DeclareLaunchArgument, GroupAction
import launch_ros.actions


def generate_launch_description():
    
    # Package name
    package_name='bill' 

    # Set use_sim_time to false
    use_sim_time = 'false'

    # Launch configurations
    rviz = LaunchConfiguration('rviz')
    slam = LaunchConfiguration('slam')
    nav = LaunchConfiguration('nav') 

    # Launch Arguments        
    declare_rviz = DeclareLaunchArgument(
        name='rviz', default_value='True',
        description='Opens rviz if set to True')
    
    declare_slam = DeclareLaunchArgument(
        name='slam', default_value='True',
        description='Activates simultaneous localization and mapping')
    
    declare_nav = DeclareLaunchArgument(
        name='nav', default_value='True',
        description='Activates the navigation stack')
     
    # Launch Robot State Publisher
    urdf_path = os.path.join(get_package_share_directory(package_name),'description','robot.urdf.xacro')
    rsp = IncludeLaunchDescription(
                PythonLaunchDescriptionSource([os.path.join(
                    get_package_share_directory(package_name),'launch','rsp.launch.py'
                )]), launch_arguments={'use_sim_time': use_sim_time, 'urdf': urdf_path}.items()
    )

    # Launch Twist Mux
    twist_mux_params = os.path.join(get_package_share_directory(package_name),'config','twist_mux_params.yaml')
    twist_mux = Node(
            package="twist_mux",
            executable="twist_mux",
            parameters=[twist_mux_params, {'use_sim_time': False}],
            remappings=[('/cmd_vel_out','/cmd_vel')]
    )
 
    # Launch Rviz with diff bot rviz file
    rviz_config_file = os.path.join(get_package_share_directory(package_name), 'rviz', 'bot.rviz')
    rviz2 = GroupAction(
        condition=IfCondition(rviz),
        actions=[Node(
                    package='rviz2',
                    executable='rviz2',
                    arguments=['-d', rviz_config_file],
                    output='screen',
                    remappings=[('/map', 'map'),
                                ('/tf', 'tf'),
                                ('/tf_static', 'tf_static'),
                                ('/goal_pose', 'goal_pose'),
                                ('/clicked_point', 'clicked_point'),
                                ('/initialpose', 'initialpose')])]
    )

    # Launch Simultaneous Localization and Mapping
    slam_node = GroupAction(
        condition=IfCondition(slam),
        actions=[IncludeLaunchDescription(
                    PythonLaunchDescriptionSource([os.path.join(
                        get_package_share_directory(package_name),'launch','slam.launch.py'
                    )]), launch_arguments={'use_sim_time': use_sim_time}.items())]
    )

    # Launch the navigation stack
    nav_params = os.path.join(get_package_share_directory(package_name), 'config', 'nav_params.yaml')
    nav_node = GroupAction(
        condition=IfCondition(nav),
        actions=[IncludeLaunchDescription(
                    PythonLaunchDescriptionSource([os.path.join(
                        get_package_share_directory(package_name),'launch','nav.launch.py'
                    )]), launch_arguments={'use_sim_time': use_sim_time, 'params_file': nav_params}.items())]
    )

    static_tf_odom = launch_ros.actions.Node(
        package='tf2_ros',
        executable='static_transform_publisher',
        name='static_transform_publisher',
        output='screen',
        arguments=['0.0', '0.0', '0.0', '0', '0', '0', 'base_link', 'odom'],
    )

    tf2_node = Node(package='tf2_ros',
                    executable='static_transform_publisher',
                    name='static_tf_pub_laser',
                    arguments=['0', '0', '0.02','0', '0', '0', '1','base_link','laser_link'],
    )

    robot_localization = launch_ros.actions.Node(
        package='robot_localization',
        executable='ekf_node',
        name='ekf_filter_node',
        output='screen',
        parameters=[os.path.join(get_package_share_directory('bill'), 'config', 'ekf.yaml')],
    )

    joint_state_publisher = Node(
        package="joint_state_publisher",
        executable="joint_state_publisher",
        name="joint_state_publisher",
        parameters=[{'use_gui': False}],
        output="screen",
    )

    # Launch mecanum_drive_controller
    mecanum_drive_controller = Node(
        package='controller_manager',
        executable='spawner',
        name='mecanum_drive_controller',
        arguments=['mecanum_drive_controller'],
        output='screen'
    )

    controller_manager = Node(
        package="controller_manager",
        executable="ros2_control_node",
        parameters=[os.path.join(get_package_share_directory(package_name), 'config', 'diff_drive_controller.yaml')],
        output="screen",
    )

    load_diff_drive_controller = Node(
        package="controller_manager",
        executable="spawner",
        arguments=["diff_drive_controller"],
        output="screen",
    )

    # Launch them all!
    return LaunchDescription([
        # Declare launch arguments
        declare_rviz,
        declare_slam,
        declare_nav,

        # Launch the nodes
        rviz2,
        rsp,
        joint_state_publisher,
        # static_tf_odom,
        # tf2_node,
        robot_localization,  
        twist_mux,
        mecanum_drive_controller,  # Adicionando o controlador aqui
        # controller_manager,
        # load_diff_drive_controller
        # slam_node,
        # nav_node,
    ])
