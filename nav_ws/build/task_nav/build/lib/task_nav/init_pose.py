#!/usr/bin/env python3

import rclpy
from rclpy.node import Node
from geometry_msgs.msg import PoseWithCovarianceStamped
from nav_msgs.msg import Odometry

# Node initialization
class InitialPoseNode(Node):
    def __init__(self):
        super().__init__('init_pose')
        self.publisher_ = self.create_publisher(PoseWithCovarianceStamped, '/initialpose', 1)

        # Subscription to the /odom topic
        self.odom_subscriber = self.create_subscription(Odometry, '/odom', self.odom_callback, 10)

        # Construct the message but leave fields to be populated in the callback
        self.init_msg = PoseWithCovarianceStamped()
        self.init_msg.header.frame_id = 'map'

        # Boolean to check if we received the odometry message
        self.odom_received = False

    def odom_callback(self, msg):
        self.get_logger().info("Odometry received, setting initial pose")
        # Set the initial pose based on the odometry data
        self.init_msg.pose.pose.position.x = msg.pose.pose.position.x
        self.init_msg.pose.pose.position.y = msg.pose.pose.position.y
        self.init_msg.pose.pose.orientation.x = msg.pose.pose.orientation.x
        self.init_msg.pose.pose.orientation.y = msg.pose.pose.orientation.y
        self.init_msg.pose.pose.orientation.z = msg.pose.pose.orientation.z
        self.init_msg.pose.pose.orientation.w = msg.pose.pose.orientation.w

        # Publish the initial pose
        self.publisher_.publish(self.init_msg)
        self.get_logger().info("Initial pose has been set")
        
        # Odometry has been processed
        self.odom_received = True

def main(args=None):
    rclpy.init(args=args)
    node = InitialPoseNode()

    # Spin the node to keep receiving callbacks
    rclpy.spin(node)

    rclpy.shutdown()

if __name__ == '__main__':
    main()
