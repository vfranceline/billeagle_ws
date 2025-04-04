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
import launch.actions


def generate_launch_description():
    
    # Package name
    package_name='bill_description' 

    # Launch configurations
    use_sim_time = LaunchConfiguration('use_sim_time')
    rviz = LaunchConfiguration('rviz')

    # Launch Arguments
    declare_use_sim_time = DeclareLaunchArgument(
        name='use_sim_time', default_value='false',
        description='Use simulation (Gazebo) clock if true')
            
    declare_rviz = DeclareLaunchArgument(
        name='rviz', default_value='True',
        description='Opens rviz if set to True')
         
    # Launch Robot State Publisher
    urdf_path = os.path.join(get_package_share_directory(package_name),'description','robot.urdf.xacro')
    rsp = IncludeLaunchDescription(
                PythonLaunchDescriptionSource([os.path.join(
                    get_package_share_directory(package_name),'launch','rsp.launch.py'
                )]), launch_arguments={'use_sim_time': use_sim_time, 'urdf': urdf_path}.items()
    )

    joint_state_publisher = Node(
        package="joint_state_publisher",
        executable="joint_state_publisher",
        name="joint_state_publisher",
        parameters=[{'use_gui': False}],
        output="screen",
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

    tf2_node = Node(package='tf2_ros',
                    executable='static_transform_publisher',
                    name='static_tf_pub_laser',
                    arguments=['0', '0', '0.02','0', '0', '0', '1','base_link','laser_link'],
    )

    # # Launch mecanum_drive_controller
    # mecanum_drive_controller = Node(
    #     package='controller_manager',
    #     executable='spawner',
    #     name='mecanum_drive_controller',
    #     arguments=['mecanum_drive_controller'],
    #     output='screen'
    # )

    # controller_manager = Node(
    #     package="controller_manager",
    #     executable="ros2_control_node",
    #     parameters=[os.path.join(get_package_share_directory(package_name), 'config', 'mecanum_drive_controller.yaml')],
    #     output="screen",
    # )

    # Launch them all!
    return LaunchDescription([
        # Declare launch arguments
        declare_use_sim_time,
        declare_rviz,
        

        # Launch the nodes
        rviz2,
        rsp,
        joint_state_publisher,
        tf2_node, 
        twist_mux,
        mecanum_drive_controller,
        controller_manager,
       
    ])
