#!/usr/bin/env python3
import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Twist
from std_msgs.msg import String 

class VelocityPublisher(Node):
    def __init__(self):
        super().__init__('turn_around')

        self.publisher_ = self.create_publisher(Twist, '/cmd_vel', 10)
        self.subscription = self.create_subscription(String, 'training_finished', self.listener_callback, 10)

        self.velocity_msg = Twist()
        self.velocity_msg.angular.z = 0.0

        self.elapsed_time = 0.0  
        self.duration = 1.0  # Tempo de rotação
        self.is_rotating = False

        self.timer = None  # Timer para publicar a velocidade
        self.countdown_timer = None  # Timer para a contagem regressiva
        self.countdown_value = 10  # Tempo de espera antes da rotação

    def listener_callback(self, msg):
        if msg.data == 'round180' and not self.is_rotating:
            self.is_rotating = True
            self.get_logger().info('Recebido comando "round180"')
            self.get_logger().info('Aguardando 10 segundos...')
            
            # Inicia a contagem regressiva usando um timer ROS2
            self.countdown_timer = self.create_timer(1.0, self.countdown)

    def countdown(self):
        if self.countdown_value > 0:
            self.get_logger().info(f'Contagem regressiva: {self.countdown_value}')
            self.countdown_value -= 1
        else:
            self.get_logger().info('Iniciando rotação de 180 graus.')
            self.countdown_timer.cancel()  # Cancela o timer da contagem regressiva

            # Configura a velocidade angular para girar
            self.velocity_msg.angular.z = 1.0

            # Cria um timer para publicar a velocidade
            self.timer = self.create_timer(0.1, self.publish_velocity)

    def publish_velocity(self):
        if self.elapsed_time < self.duration:
            self.publisher_.publish(self.velocity_msg)
            self.elapsed_time += 0.1
        else:
            self.velocity_msg.angular.z = 0.0  # Para a rotação
            self.publisher_.publish(self.velocity_msg)
            self.get_logger().info('Parando o robô.')
            
            self.timer.cancel()  # Para o timer
            self.is_rotating = False  # Permite futuras ativações

def main(args=None):
    rclpy.init(args=args)
    node = VelocityPublisher()
    rclpy.spin(node)

if __name__ == '__main__':
    main()
