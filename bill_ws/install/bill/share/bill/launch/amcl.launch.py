from launch import LaunchDescription
from launch_ros.actions import Node

def generate_launch_description():
    return LaunchDescription([
        Node(
            package='nav2_map_server',
            executable='map_server',
            name='map_server',
            parameters=[{'yaml_filename': '/home/bill8/billeagle_ws/bill_ws/src/bill/maps/finalmente_save.yaml'}]
        ),
        Node(
            package='nav2_amcl',
            executable='amcl',
            name='amcl',
            parameters=['/home/bill8/billeagle_ws/bill_ws/src/bill/config/amcl.yaml']
        ),
        # Include your robot_state_publisher node here
    ])
