import cv2
# import torch
import yolov5
import rclpy
from geometry_msgs.msg import Twist
from rclpy.node import Node

L1 = 0.02
L2 = 0.03
X_MAX = 640
Y_MAX = 480

# device_use = torch.device("cpu")
# model = torch.hub.load('/home/e-yantra/.cache/torch/hub/ultralytics_yolov5_master', 'custom', path='/home/evoprime/Athena/PROJ/RIG/sip_ws/src/locomotion/locomotion/yolov5n.pt', source='local')  
# model = torch.hub.load('~/.cache/torch/hub/ultralytics_yolov5_master', 'custom', path='~/asc/asc_ws/src/locomotion/locomotion/yolov5n.pt', source='local')  
model  = yolov5.load("yolov5l.pt")
# model = torch.hub.load('ultralytics/yolov5', 'yolov5n',force_reload=True)
# model = torch.load('yolov5n-seg.pt')
model.max_det= 1
model.conf = .30
model.classes = [0]
print("hey!!!!!")

class MinimalPublisher(Node):
    def __init__(self):
        super().__init__('yolo_detect')
        self.publisher_ = self.create_publisher(Twist,"/cmd_vel",1)
        self.vx = 0
        self.vy = 0
        self.w = 0
        self.vidcam = cv2.VideoCapture("https://192.168.122.56:8080/video")#"https://192.168.122.56:8080/video
        

    def detect(self):
        msg = Twist()
        while (self.vidcam.isOpened()):
            
            ret, frame = self.vidcam.read()
            if ret:
                
                results = model(frame, size=X_MAX)
                coords = results.pred[0][:, :4]
                # results.show()
                # print(coords.cpu().detach().numpy())

                try:
                    coords = coords.cpu().detach().numpy()
                    x,y,w,h = coords[0]
                    x = (x + w)//2
                    # y = (y + h)//2

                except:
                    msg.linear.x = 0.0
                    msg.linear.y = 0.0
                    self.publisher_.publish(msg)
                    continue

                # self.w = (X_MAX/2 - x)
                # self.vy =(Y_MAX/2 - y)

                # print(x, y)
                cv2.imshow('frame',results.render()[0]) 
                if cv2.waitKey(1) & 0xFF == ord('q'):
                    break



                if x < 640/3:
                    self.y = -0.8
                    print("left")
                elif x > 2*640/3:
                    print("right")
                    self.y = 0.8

                else:
                    self.y = 0.0
                    print("center")
                
                if y < 480/3:
                    self.x = -0.8
                elif x > 480/3:
                    self.x = 0.8
                else:
                    self.x = 0.0

            else:
                break
            msg.linear.y = self.y
            msg.linear.x = self.x
            self.publisher_.publish(msg)

def main(args=None):
    rclpy.init(args=args)
    minimal_publisher = MinimalPublisher()
    minimal_publisher.detect()
    minimal_publisher.destroy_node()
    rclpy.shutdown()



if __name__ == '__main__':
    main()





