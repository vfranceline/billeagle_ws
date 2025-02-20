#!/usr/bin/env python3
import rclpy
import time
from rclpy.node import Node
from geometry_msgs.msg import Twist
from bill_interfaces.srv import ExecuteSpin


class NavigationNode(Node): 
    def __init__(self):
        super().__init__("navigation") 
        self._executeSpinService=self.create_service(ExecuteSpin,"execute_spin",self.callback_execute_spin) 
        self.pub_cmd_vel = self.create_publisher(Twist, '/cmd_vel', 10)
        self.get_logger().info("Navigation Node has started")

    def callback_execute_spin(self, request, response):
        angle=request.angle
        response.done=self.execute_spin(angle)     
        return response
    
    def execute_spin(self, angle):
        # TO-DO
        # colque aqui seu código para girar o robô do angulo informado
        self.get_logger().info("Iniciando rotação de 180 graus")
        
        twist_msg = Twist()
        twist_msg.linear.y = -0.7 #velocidade para fazer o giro
        
        duration = 4.4  # Tempo em segundos para a rotação
        start_time = self.get_clock().now()
        rate = 0.1  # Intervalo de publicação (10 Hz)

        #publicar a mensagem continuamente pela tempo informado
        while (self.get_clock().now() - start_time).nanoseconds / 1e9 < duration:
            self.cmd_vel_pub.publish(twist_msg)
            time.sleep(rate)
        
        # Envia mensagem de parada (comando zero)
        twist_msg.linear.y = 0.0
        self.cmd_vel_pub.publish(twist_msg)
        self.get_logger().info("Rotação concluída")
        return True



def main(args=None):
    rclpy.init(args=args)
    node = NavigationNode()
    rclpy.spin(node)
    rclpy.shutdown()