import time
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

        # action client for navigation
        self._action_client = ActionClient(self, NavigateToPose, 'navigate_to_pose')
        self.__goal_done_future = Future()

        self._status_pub = self.create_publisher(String, '/status', 10)

    # sending navigation goal (pose)
    def send_goal(self, pose: PoseStamped):
        self.__goal_done_future = Future() #reset future
        goal_msg = NavigateToPose.Goal()
        goal_msg.pose = pose

        self.get_logger().info("Waiting for the action server...") 
        self._action_client.wait_for_server()
        self.get_logger().info("Action server available. Sending goal...")

        self._send_goal_future = self._action_client.send_goal_async(goal_msg)
        self._send_goal_future.add_done_callback(self.goal_response_callback)

    # called when the server responds to the goal
    def goal_response_callback(self, future):
        goal_handle = future.result()
        if not goal_handle.accepted:
            self.get_logger().info('Goal rejected')
            return

        self.get_logger().info('Goal accepted')
        self._get_result_future = goal_handle.get_result_async()
        self._get_result_future.add_done_callback(self._get_result_future_callback)
    
    # called when the result of navigation is received
    def get_result_future_callback(self, future):
        result = future.result().result
        self.get_logger().info(f'Navigation result: {result}')
        self.__goal_done_future.set_result(True)

def main(args=None):
    rclpy.init(args=args)
    node = InspectionNode()

    # set inspection pose
    inspection_pose = PoseStamped()
    inspection_pose.header.frame_id = 'map'
    inspection_pose.pose.position.x = 0.0
    inspection_pose.pose.position.y = 0.0
    inspection_pose.pose.position.z = 0.0
    inspection_pose.pose.orientation.x = 0.0
    inspection_pose.pose.orientation.y = 0.0
    inspection_pose.pose.orientation.z = 0.0
    inspection_pose.pose.orientation.w = 0.0

    node.get_logger().info("Waiting 10 seconds before going to inspection.")
    for i in range(10):
        print(10-i)
        time.sleep(1)

    node._status_pub.publish(String(data="Heading to inspection point"))
    node.get_logger().info("Published status: Heading to inspection point")

    node.get_logger().info("Sending bill to inspection point")
    node.send_goal(inspection_pose)
    rclpy.spin_until_future_complete(node, node.__goal_done_future)
    node.get_logger().info("Arrived at inspection point")

    node._status_pub.publish(String(data="Arrived at inspection point"))
    node.get_logger().info("Published status: Arrived at inspection point")

    node.get_logger().info("Waiting 30 seconds at inspection point.")
    for i in range(30):
        print(30-i)
        time.sleep(1)

    node._status_pub.publish(String(data="Leaving inspection point"))
    node.get_logger().info("Published status: Leaving inspection point")

    exit_pose = PoseStamped()
    exit_pose.header.frame_id = 'map'
    exit_pose.pose.position.x = 0.0 
    exit_pose.pose.position.y = 0.0
    exit_pose.pose.position.z = 0.0
    exit_pose.pose.orientation.x = 0.0
    exit_pose.pose.orientation.y = 0.0
    exit_pose.pose.orientation.z = 0.0
    exit_pose.pose.orientation.w = 0.0

    node.get_logger().info("Sending bill to exit point")
    node.send_goal(exit_pose)
    rclpy.spin_until_future_complete(node, node.__goal_done_future)
    node.get_logger().info("Arrived at exit point. Shutting down.")

    rclpy.shutdown()

if __name__ == '__main__':
    main()
