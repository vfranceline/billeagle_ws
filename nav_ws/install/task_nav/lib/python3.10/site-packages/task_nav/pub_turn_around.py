#!/usr/bin/env python3
import rclpy
from rclpy.node import Node
from std_msgs.msg import String
import time

class VelocityPublisher(Node):
    def __init__(self):
        super().__init__('turn_around')

        # Cria o publisher no tópico /turned_around
        self.publisher_fin_round = self.create_publisher(String, 'turned_around', 10)

        # Cria um timer para chamar publish_velocity após 5 segundos
        self.timer = self.create_timer(5.0, self.publish_velocity)
        self.get_logger().info('Aguardando 5 segundos...')
        for i in range(5):
            print(5-i)
            time.sleep(1)

    def publish_velocity(self):
        fin_msg = String()
        fin_msg.data = 'finalizado'
        self.publisher_fin_round.publish(fin_msg)
        self.get_logger().info('Publicando a mensagem de finalização de giro.')

        # Cancela o timer e destrói o nó após a publicação
        self.timer.cancel()
        self.destroy_node()

def main(args=None):
    rclpy.init(args=args)
    node = VelocityPublisher()

    try:
        rclpy.spin(node)  # Mantém o nó rodando até que seja interrompido
    except KeyboardInterrupt:
        node.get_logger().info("Node interrompido. Encerrando...")
    finally:
        node.destroy_node()
        rclpy.shutdown()

if __name__ == '__main__':
    main()
