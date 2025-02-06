import rclpy
from rclpy.node import Node
from std_msgs.msg import String

class TrainingFinishedPublisher(Node):

    def __init__(self):
        super().__init__('training_finished_publisher')
        self.publisher_ = self.create_publisher(String, 'traning_finished', 10)
        self.timer = self.create_timer(1.0, self.timer_callback)
        self.get_logger().info('Training finished publisher node has been started.')

    def timer_callback(self):
        msg = String()
        msg.data = 'round180'
        self.publisher_.publish(msg)
        self.get_logger().info(f'Publishing: "{msg.data}"')

def main(args=None):
    rclpy.init(args=args)
    training_finished_publisher = TrainingFinishedPublisher()
    rclpy.spin(training_finished_publisher)
    training_finished_publisher.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()