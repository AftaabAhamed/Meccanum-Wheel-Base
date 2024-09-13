import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Vector3, Quaternion, Twist
import numpy as np 

L1 = 0.5
L2 = 0.5
SCALE_FACTOR = 1024

class MinimalPublisher(Node):
    def __init__(self):
        super().__init__('robot_1')
        self.publisher_ = self.create_publisher(Quaternion,"/motor_vel",1)
        
        self.subscriber_ = self.create_subscription(Twist,"/cmd_vel", self.subscriber_callback,10)
        timer_period = 0.05  # seconds
        self.timer = self.create_timer(timer_period, self.timer_callback)
        self.vel = np.zeros((4,))

    def timer_callback(self):
        msg = Quaternion()
        msg.y, msg.x, msg.w, msg.z = self.vel
        self.publisher_.publish(msg)


    def subscriber_callback(self,msg :Twist):
        # print("JOY", self.joy_val)
        vx = msg.linear.x
        vy = msg.linear.y
        w =  -msg.angular.z

        trans_matrix = np.array([[1, -1, -(L1 + L2)],
                                [1, 1, (L1 + L2)],
                                [1, 1, -(L1 + L2)],
                                [1, -1,  (L1 + L2)]])
        vel_matrix = np.array([vx, vy, w]).T
        # vel_matrixLj
        self.vel = SCALE_FACTOR * np.matmul(trans_matrix, vel_matrix)

def main(args=None):
    rclpy.init(args=args)

    minimal_publisher = MinimalPublisher()

    rclpy.spin(minimal_publisher)

    # Destroy the node explicitly
    # (optional - otherwise it will be done automatically
    # when the garbage collector destroys the node object)
    minimal_publisher.destroy_node()
    rclpy.shutdown()



if __name__ == '__main__':
    main()