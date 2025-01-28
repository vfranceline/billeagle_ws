import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Twist, TransformStamped
from nav_msgs.msg import Odometry
from sensor_msgs.msg import JointState
from tf_transformations import quaternion_from_euler
from tf2_ros import TransformBroadcaster
from std_msgs.msg import Float64MultiArray
# import numpy as np
from threading import Lock
from math import sin, cos, sqrt


class MecanumDriveNode(Node):
    def __init__(self):
        super().__init__("mecanum_drive")
        self._cmd_vel_sub = self.create_subscription(Twist, "/cmd_vel", self.cmd_vel_callback, 10)
        self._odom_pub = self.create_publisher(Odometry, "/odom", 10)
        self._joint_state_pub = self.create_publisher(JointState, "joint_states", 10)

        self.tf_broadcaster = TransformBroadcaster(self)

        self.wheel_separation = 0.064
        self.wheel_diameter = 0.098
        
        self.update_rate = 100.0

        self.odom_frame = "odom"
        self.base_frame = "base_link"

        self.linear_x = 0.0
        self.angular_z = 0.0
        self.pose_x = 0.0
        self.pose_y = 0.0
        self.theta = 0.0

        self.wheel_speeds = [0.0, 0.0, 0.0, 0.0] # [frente-esquerda, frente-direita, traseira-esquerda, traseira-direita]
        
        self.timer = self.create_timer(1.0/self.update_rate, self.update)

        self.lock = Lock()

    def cmd_vel_callback(self, msg: Twist):
        with self.lock:
            self.linear_x = msg.linear.x
            self.angular_z = msg.angular.z

            self.wheel_speeds[0] = self.linear_x + self.angular_z * (self.wheel_separation / 2)  # Front Left
            self.wheel_speeds[1] = self.linear_x - self.angular_z * (self.wheel_separation / 2)  # Front Right
            self.wheel_speeds[2] = self.linear_x - self.angular_z * (self.wheel_separation / 2)  # Rear Left
            self.wheel_speeds[3] = self.linear_x + self.angular_z * (self.wheel_separation / 2)  # Rear Right
    
    def update(self): #att odom
        dt = 1.0/self.update_rate

        with self.lock:
            delta_x = (self.wheel_speeds[0] + self.wheel_speeds[1] + self.wheel_speeds[2] + self.wheel_speeds[3]) / 4 * cos(self.theta) * dt
            delta_y = (self.wheel_speeds[0] + self.wheel_speeds[1] + self.wheel_speeds[2] + self.wheel_speeds[3]) / 4 * sin(self.theta) * dt
            delta_theta = (self.wheel_speeds[1] - self.wheel_speeds[0] + self.wheel_speeds[3] - self.wheel_speeds[2]) / (self.wheel_separation * 2) * dt
            
            self.pose_x += delta_x
            self.pose_y += delta_y
            self.theta += delta_theta

        self.publish_odom(delta_x, delta_y, delta_theta, dt)

        self.publish_joint_state()

    def publish_odom(self, dx, dy, d_theta, dt):
        odom_msg = Odometry()
        odom_msg.header.stamp = self.get_clock().now().to_msg()
        odom_msg.header.frame_id = self.odom_frame
        odom_msg.child_frame_id = self.base_frame
        
        # Atualizando pose e orientação
        odom_msg.pose.pose.position.x = self.pose_x
        odom_msg.pose.pose.position.y = self.pose_y
        quat = quaternion_from_euler(0, 0, self.theta)
        odom_msg.pose.pose.orientation.x = quat[0]
        odom_msg.pose.pose.orientation.y = quat[1]
        odom_msg.pose.pose.orientation.z = quat[2]
        odom_msg.pose.pose.orientation.w = quat[3]
        
        # Atualizando velocidades
        odom_msg.twist.twist.linear.x = dx / dt
        odom_msg.twist.twist.linear.y = dy / dt
        odom_msg.twist.twist.angular.z = d_theta / dt

        self._odom_pub.publish(odom_msg)

        self.publish_tf()

    def publish_tf(self):
        # Cria e publica a transformação de odom para base_link
        t = TransformStamped()
        t.header.stamp = self.get_clock().now().to_msg()
        t.header.frame_id = self.odom_frame
        t.child_frame_id = self.base_frame

        # Posição e orientação com base na odometria
        t.transform.translation.x = self.pose_x
        t.transform.translation.y = self.pose_y
        t.transform.translation.z = 0.0
        quat = quaternion_from_euler(0, 0, self.theta)
        t.transform.rotation.x = quat[0]
        t.transform.rotation.y = quat[1]
        t.transform.rotation.z = quat[2]
        t.transform.rotation.w = quat[3]

        # Publica a transformação
        self.tf_broadcaster.sendTransform(t)

    def publish_joint_state(self):
        # Publicação dos estados das juntas
        joint_state_msg = JointState()
        joint_state_msg.header.stamp = self.get_clock().now().to_msg()
        joint_state_msg.name = ["wheel1_joint", "wheel2_joint", "wheel3_joint", "wheel4_joint"]
        joint_state_msg.position = [self.wheel_speeds[0], self.wheel_speeds[1], self.wheel_speeds[2], self.wheel_speeds[3]]  # Posições simplificadas
        self._joint_state_pub.publish(joint_state_msg)

def main(args=None):
    rclpy.init(args=args)
    mecanum_drive_node = MecanumDriveNode()
    rclpy.spin(mecanum_drive_node)
    mecanum_drive_node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()