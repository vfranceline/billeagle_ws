import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Twist, TransformStamped
from nav_msgs.msg import Odometry
from sensor_msgs.msg import JointState
from tf_transformations import quaternion_from_euler
from tf2_ros import TransformBroadcaster
from math import sin, cos
from threading import Lock

class MecanumDriveNode(Node):
    def __init__(self):
        super().__init__("mecanum_drive")
        # self._cmd_vel_sub = self.create_subscription(Twist, "/cmd_vel", self.cmd_vel_callback, 10)
        # self._odom_pub = self.create_publisher(Odometry, "/odom", 10)
        self._joint_state_pub = self.create_publisher(JointState, "joint_states", 10)

        self.tf_broadcaster = TransformBroadcaster(self)

        # Parâmetros geométricos do robô (ajuste conforme seu robô)
        self.L = 0.15  # Distância entre os eixos (dianteiro e traseiro)
        self.W = 0.15  # Distância lateral entre rodas
        self.wheel_diameter = 0.098  # Diâmetro da roda (se necessário para conversão de velocidades)

        self.update_rate = 100.0  # Hz

        self.odom_frame = "odom"
        self.base_frame = "base_link"

        # Variáveis de controle e odometria
        self.linear_x = 0.0
        self.linear_y = 0.0
        self.angular_z = 0.0

        self.pose_x = 0.0
        self.pose_y = 0.0
        self.theta = 0.0

        # Velocidades individuais das rodas [FL, FR, RL, RR]
        self.wheel_speeds = [0.0, 0.0, 0.0, 0.0]

        self.timer = self.create_timer(1.0 / self.update_rate, self.update)
        self.lock = Lock()

    def cmd_vel_callback(self, msg: Twist):
        with self.lock:
            # Recebe os comandos do /cmd_vel
            self.linear_x = msg.linear.x
            self.linear_y = msg.linear.y
            self.angular_z = msg.angular.z

            # Cinemática inversa para rodas mecanum
            # Fórmulas comuns (sujeitas a ajustes conforme a montagem):
            #
            #   v_FL = vₓ - v_y - (L+W)*ω
            #   v_FR = vₓ + v_y + (L+W)*ω
            #   v_RL = vₓ + v_y - (L+W)*ω
            #   v_RR = vₓ - v_y + (L+W)*ω
            #
            # Se o seu robô apresenta comportamento invertido (por exemplo, comando lateral gera rotação),
            # experimente trocar os sinais de v_y e/ou ω.
            sum_LW = self.L + self.W
            self.wheel_speeds[0] = self.linear_x - self.linear_y - sum_LW * self.angular_z  # Front Left
            self.wheel_speeds[1] = self.linear_x + self.linear_y + sum_LW * self.angular_z  # Front Right
            self.wheel_speeds[2] = self.linear_x + self.linear_y - sum_LW * self.angular_z  # Rear Left
            self.wheel_speeds[3] = self.linear_x - self.linear_y + sum_LW * self.angular_z  # Rear Right

    def update(self):
        dt = 1.0 / self.update_rate

        with self.lock:
            # Integra os comandos para atualizar a pose do robô
            vx = self.linear_x
            vy = self.linear_y
            omega = self.angular_z

            # Converte as velocidades do frame do robô para o frame global (odom)
            delta_x = (vx * cos(self.theta) - vy * sin(self.theta)) * dt
            delta_y = (vx * sin(self.theta) + vy * cos(self.theta)) * dt
            delta_theta = omega * dt

            self.pose_x += delta_x
            self.pose_y += delta_y
            self.theta += delta_theta

        self.publish_odom(delta_x, delta_y, delta_theta, dt)
        self.publish_joint_state()

    def publish_odom(self, dx, dy, d_theta, dt):
        # odom_msg = Odometry()
        # odom_msg.header.stamp = self.get_clock().now().to_msg()
        # odom_msg.header.frame_id = self.odom_frame
        # odom_msg.child_frame_id = self.base_frame

        # odom_msg.pose.pose.position.x = self.pose_x
        # odom_msg.pose.pose.position.y = self.pose_y
        # odom_msg.pose.pose.position.z = 0.0
        # quat = quaternion_from_euler(0, 0, self.theta)
        # odom_msg.pose.pose.orientation.x = quat[0]
        # odom_msg.pose.pose.orientation.y = quat[1]
        # odom_msg.pose.pose.orientation.z = quat[2]
        # odom_msg.pose.pose.orientation.w = quat[3]

        # odom_msg.twist.twist.linear.x = dx / dt
        # odom_msg.twist.twist.linear.y = dy / dt
        # odom_msg.twist.twist.angular.z = d_theta / dt

        # self._odom_pub.publish(odom_msg)
        self.publish_tf()

    def publish_tf(self):
        t = TransformStamped()
        t.header.stamp = self.get_clock().now().to_msg()
        t.header.frame_id = self.odom_frame
        t.child_frame_id = self.base_frame

        t.transform.translation.x = self.pose_x
        t.transform.translation.y = self.pose_y
        t.transform.translation.z = 0.0
        quat = quaternion_from_euler(0, 0, self.theta)
        t.transform.rotation.x = quat[0]
        t.transform.rotation.y = quat[1]
        t.transform.rotation.z = quat[2]
        t.transform.rotation.w = quat[3]

        self.tf_broadcaster.sendTransform(t)

    def publish_joint_state(self):
        joint_state_msg = JointState()
        joint_state_msg.header.stamp = self.get_clock().now().to_msg()
        joint_state_msg.name = ["front_left_wheel_joint", "front_right_wheel_joint", "rear_left_wheel_joint", "rear_right_wheel_joint"]
        # Publica as velocidades das rodas (essas podem ser usadas para simulação ou controle)
        joint_state_msg.position = self.wheel_speeds
        self._joint_state_pub.publish(joint_state_msg)

def main(args=None):
    rclpy.init(args=args)
    node = MecanumDriveNode()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()
