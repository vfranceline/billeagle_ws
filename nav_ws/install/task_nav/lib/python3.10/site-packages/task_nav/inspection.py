import rclpy
from rclpy.node import Node
from nav2_msgs.action import NavigateToPose
from geometry_msgs.msg import PoseStamped
from rclpy.action import ActionClient
from rclpy.task import Future
from std_msgs.msg import String

class InspectionNode(Node):
    def __init__(self):
        super().__init__('inspection')

        self._action_client = ActionClient(self, NavigateToPose, 'navigate_to_pose')

        self.__goal_done_future = Future()

        # subscriber da msg publicada pela voz
        self._inspection_completed_sub = self.create_subscription(String, 'cmd_voz', self.inspection_completed_callback, 10)

        self.inspection_completed = False

    def send_goal(self, pose: PoseStamped):
        goal_msg = NavigateToPose.Goal()

        goal_msg.pose = pose

        self._action_client.wait_for_server()

        # manda o objetivo
        self._send_goal_future = self._action_client.send_goal_async(goal_msg)
        self._send_goal_future.add_done_callback(self.goal_response_callback)

    def goal_response_callback(self, future):
        goal_handle = future.result()

        if not goal_handle.accepted:
            self.get_logger().info('GOAL REJECTED :(')
            return

        self.get_logger().info('GOAL ACCEPTED')

        self._get_result_future = goal_handle.get_result_async()
        self._get_result_future.add_done_callback(self._get_result_future_callback)
    
    def get_result_future_callback(self, future):
        result = future.result().result
        self.get_logger().info(f'NAVIGATION RESULT: {result}')

        self.__goal_done_future.set_result(True)

    def inspection_completed_callback(self, msg):
        if msg.data == 'inspection completed':
            self.get_logger().info(f'Inspeção concluida: {msg.data}')
            self.get_logger().info('Saindo da arena')
            self.inspection_completed = True

def main(args=None):
    rclpy.init(args=args)

    navigation_client = InspectionNode()

    inspection_pose = PoseStamped()
    inspection_pose.header.frame_id = 'map'
    inspection_pose.pose.position.x = 0.0
    inspection_pose.pose.position.y = 0.0
    inspection_pose.pose.position.z = 0.0
    inspection_pose.pose.orientation.x = 0.0
    inspection_pose.pose.orientation.y = 0.0
    inspection_pose.pose.orientation.z = 0.0
    inspection_pose.pose.orientation.w = 0.0

    navigation_client.send_goal(inspection_pose)

    rclpy.spin_until_future_complete(navigation_client, navigation_client.__goal_done_future)

    while not navigation_client.inspection_completed:
        rclpy.spin_once(navigation_client)

    exit_pose = PoseStamped()
    exit_pose.header.frame_id = 'map'
    exit_pose.pose.position.x = 0.0 
    exit_pose.pose.position.y = 0.0
    exit_pose.pose.position.z = 0.0
    exit_pose.pose.orientation.x = 0.0
    exit_pose.pose.orientation.y = 0.0
    exit_pose.pose.orientation.z = 0.0
    exit_pose.pose.orientation.w = 0.0

    navigation_client.send_goal(exit_pose)

    rclpy.spin_until_future_complete(navigation_client, navigation_client.__goal_done_future)

    navigation_client.get_logger().info("NAVIGATION GOAL HAS BEEN PROCESSES. SHUTTING DOWN...")
    rclpy.shutdown()

if __name__ == '__main__':
    main()