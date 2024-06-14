from ultralytics import YOLO
import cv2
import math
import numpy as np
from utility import *
from visual_kinematics.RobotSerial import *
import serial
import socket
import time
from threading import *

# (RASA Actions.py <-> Raspberry Pi) Communication
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
s.bind(('', 5000))

# (Raspberry Pi -> Arduino UNO) Communication
ser = serial.Serial('/dev/ttyUSB0', 115200, timeout=1.0)
time.sleep(3)
ser.reset_input_buffer()
print('Serial OK')

np.set_printoptions(precision=3, suppress=True)

# DH Parameters with length in centimeter (cm)
dh_params = np.array([[8., 0., 0.5 * pi, 0.5 * pi],
                    [0., 10.4, 0. , 0.],
                    [0., 12.6, 0., 0.],
                    [0., 0., 0.5 * pi, 0.5 * pi],
                    [16.5, 0., 0., pi]])

# Load the Robotic Arm Frame with its D-H Parameter
robot = RobotSerial(dh_params)

# Load the Yolov8 Model
model = YOLO("yolov8.onnx", task='detect')

cap = cv2.VideoCapture(0)
cap.set(3, 640)
cap.set(4, 480)

class client(Thread):
    def __init__(self, socket, address):
        Thread.__init__(self)
        self.sock = socket
        self.addr = address
        self.start()
        self.action = None
        self.object = None
        self.index = None
        self.work = False # Decide whether the robotic arm should perform an action
        
    def run(self):
        toCupTheta = np.array([-0.9, 0.8, -1.384, 0.7, 1.571]) # Towards to cup for placing
        devToCupTheta = np.array([-0.6, 1.4, -1., 1.2, 1.571]) # Retract backwards after placing object
        endTheta = np.array([0., 3.142, -2.973, -0.76, 1.571]) # Ending Position == Arduino Default Position
        nextActionTheta = np.array([0., 2.3, -2.3, 0., 1.571]) # Position for continuing next action

        # Initial Configuration to allow IK to find the desired new configuration
        initialTheta = np.array([0., 1., -2., 1., 1.5])
        robot.forward(initialTheta)
        
        className = ['blackcurrant', 'cup', 'orange', 'strawberry']
        
        while True:
            try:
                msg = self.sock.recv(1024).decode()
                self.action, self.object = msg.split()
                self.work = True
                r = "Receive"
                self.sock.send(r.encode())
            except BrokenPipeError:
                print("Broken Communication")
                break
            except BlockingIOError:
                pass
            
            # Open-CV
            success, img = cap.read()

            # Frame Transformation
            tl = (32, 98)
            bl = (30, 317)
            tr = (625, 89)
            br = (637, 313)

            cv2.circle(img, tl, 5, (0, 0, 255), -1)
            cv2.circle(img, bl, 5, (0, 0, 255), -1)
            cv2.circle(img, tr, 5, (0, 0, 255), -1)
            cv2.circle(img, br, 5, (0, 0, 255), -1)

            pts1 = np.float32([tl, bl, tr, br])
            pts2 = np.float32([(0, 0), (0, 330), (640, 0), (640, 330)])

            matrix = cv2.getPerspectiveTransform(pts1, pts2)
            transformed_frame = cv2.warpPerspective(img, matrix, (640, 330))
            
            # Object Detection from Yolov8 Model
            results = model(transformed_frame, stream=True)

            if self.work == True:
                self.index = className.index(self.object)

            for r in results:
                boxes = r.boxes
                
                # Check whether the object exist in the frame
                if self.work == True and self.index not in boxes.cls:
                    self.work = False
                    self.action = None
                    self.object = None
                    self.index = None
                    convTheta = mapAngle(endTheta, 180)
                    servoWrite(convTheta, ser)
                    ser.read()
                    time.sleep(3)
                
                for box in boxes:

                    if self.work == True:
                        if self.index == int(box.cls[0]) and int(box.conf[0]) >= 0.9:
                            # Finding the coordinates of the objects
                            x1, y1, x2, y2 = box.xyxy[0]
                            midX = (x1 + x2) / 2
                            midY = (y1 + y2) / 2
                            realX = convertMinMax(midX, 0, 640, -18.3, 18.3)
                            realY = convertMinMax(midY, 0, 330, 35, 22)
                            
                            # Adjustment
                            x = np.absolute(realX)
                            devY = convertMinMax(x, 0, 18.3, 0, 1.3)
            
                            # Inverse Kinematics
                            end = invKinematics(realX, realY - devY)
                            robot.inverse(end)
                            theta = np.array(robot.axis_values)
                            
                            # Determining the theta6 based on the objects
                            if int(box.cls[0]) == 1:
                                theta6 = 160
                            else:
                                theta6 = 175
                            
                            # Move the arm slightly behind the object
                            devTheta = theta - np.array([0., -0.3, 0.3, 0, 0])
                            convTheta = mapAngle(devTheta, 130)
                            servoWrite(convTheta, ser)
                            ser.read()
                            time.sleep(3)
                            # Move forward towards the object
                            convTheta = mapAngle(theta, 130)
                            servoWrite(convTheta, ser)
                            ser.read()
                            time.sleep(2)
                            # Close Gripper
                            convTheta = mapAngle(theta, theta6)
                            servoWrite(convTheta, ser)
                            ser.read()
                            time.sleep(2)
                            # Move towards the 'end plate'
                            convTheta = mapAngle(toCupTheta, theta6)
                            servoWrite(convTheta, ser)
                            ser.read()
                            time.sleep(2)
                            # Open Gripper
                            convTheta = mapAngle(toCupTheta, 130)
                            servoWrite(convTheta, ser)
                            ser.read()
                            time.sleep(2)
                            # Re-adjust and Move Backwards
                            convTheta = mapAngle(devToCupTheta, 130)
                            servoWrite(convTheta, ser)
                            ser.read()
                            time.sleep(1)
                            # Re-adjust for Next Action
                            convTheta = mapAngle(nextActionTheta, 180)
                            servoWrite(convTheta, ser)
                            ser.read()
                            time.sleep(2)
                            
                            # Return the configuration back to the Intiial Configuration
                            robot.forward(initialTheta)
                            
                            if self.action != 'SortCandy':
                                self.work = False
                                self.action = None
                                self.object = None
                                self.index = None
                                convTheta = mapAngle(endTheta, 180)
                                servoWrite(convTheta, ser)
                                ser.read()
                                time.sleep(3)
                                
                            break
                        
                        else:
                            pass
            
s.listen(5)
print('Server is now running.')

while True:
    clientsocket, address = s.accept()
    clientsocket.setblocking(0)
    client(clientsocket, address)