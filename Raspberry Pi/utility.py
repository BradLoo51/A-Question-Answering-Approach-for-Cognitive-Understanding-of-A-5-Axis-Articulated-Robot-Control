from visual_kinematics.RobotSerial import *
import numpy as np
from math import pi

def convertMinMax(value, leftMin, leftMax, rightMin, rightMax):
    # Figure out how 'wide' each range is
    leftSpan = leftMax - leftMin
    rightSpan = rightMax - rightMin

    # Convert the left range into a 0-1 range (float)
    valueScaled = float(value - leftMin) / float(leftSpan)

    # Convert the 0-1 range into a value in the right range.
    return (rightMin + (valueScaled * rightSpan))

def mapAngle(theta, theta6):
    theta1 = round(convertMinMax(theta[0], -1.571, 1.571, 0, 180), 0)
    theta2 = round(convertMinMax(theta[1], 0, 3.142, 10, 180), 0)
    theta3 = round(convertMinMax(theta[2], -2.793, 0, 160, 0), 0)
    theta4 = round(convertMinMax(theta[3], -1.571, 1.571, 0, 180), 0)
    theta5 = round(convertMinMax(theta[4], 0, 3.142, 0, 180), 0)

    return np.array([theta1, theta2, theta3, theta4, theta5, theta6])

def checkAngle(theta):
    if theta[0] > 1.571 or theta[0] < -1.571:
        print("Angle 1 Out of Reach")
    if theta[1] > 3.142 or theta[1] < 0:
        print("Angle 2 Out of Reach")
    if theta[2] > 0 or theta[2] < -3.142:
        print("Angle 3 Out of Reach")
    if theta[3] > 1.571 or theta[3] < -1.571:
        print("Angle 4 Out of Reach")
    if theta[4] > 3.142 or theta[4] < 0:
        print("Angle 5 Out of Reach")

def servoWrite(params, ser):
    degree = ""
    for angle in params:
        degree += str(angle) + ","

    ser.write(degree.encode('utf-8'))

def invKinematics(x, y):
    coords = np.array([x, y], dtype=np.float64)
    reshaped_coord = np.reshape(coords, (2, 1))
    xyz = np.row_stack((reshaped_coord, 0))
    abc = np.array([0. , 3.142, -0.4 * pi]) # Rotate ([z-axis, y-axis, x-axis]) of end effector
    end = Frame.from_euler_3(abc, xyz)

    return end


