#!/usr/bin/env python

import roslib; roslib.load_manifest('aries')
import rospy, math
from  lib_robotis import USB2Dynamixel_Device, Robotis_Servo
from math import *
from std_msgs.msg import Float32, String
from aries.srv import LidarPivotAngle, LidarPivotAngleResponse, LidarPivotAngleRequest

'''
This module is responsible for interfacing with lidar pivot motor.
'''
INITIAL_ANGLE = 0   # Angle servo initializes to
DYNAMIXEL_ID = 1    # ID for dynamixel servo

class lidar_pivot_controller(object):

    def __init__(self):
        '''
        lidar pivot controller constructor
        '''
        # Creates the ROS node.
        rospy.init_node("lidar_pivot_controller")

        # Load relevant parameters from ROS parameter server
        dyn_port = rospy.get_param("ports/dynamixel", "/dev/ttyUSB1")
        dyn_baud = rospy.get_param("baudrates/dynamixel_baud", 1000000)

         # Load LIDAR Pivot stuff
        self.PIVOT_LAYDOWN = rospy.get_param("dynamixel_settings/laying_angle", 20)
        self.PIVOT_STAND = rospy.get_param("dyanmixel_settings/standing_angle", 0)
        self.PIVOT_MAX = rospy.get_param("dyanimxel_settings/top_limit", 25)
        self.PIVOT_MIN = rospy.get_param("dynamixel_settings/bottom_limit", -1)

        self.target_angle = self.PIVOT_LAYDOWN

        # Target angle in radians
        self.move_request = False
        dyn_id = rospy.get_param("dynamixel_settings/id", DYNAMIXEL_ID)
        CMDS_TOPIC = rospy.get_param("topics/lidar_pivot_cmds", "lidar_pivot_control")
        TARGET_ANGLE_TOPIC = rospy.get_param("topics/lidar_pivot_target_angles", "lidar_pivot_target_angles")
        POS_SERV = rospy.get_param("services/lidar_pivot_position", "get_lidar_pivot_position")
        
        # Attempting to connect to dynamixel
        self.dyn = None
        self.servo = None
        print("Attempting to connect to dynamixel on port: " + str(dyn_port))
        while not rospy.is_shutdown():
            good_conn = False  # Set if successful connection to dynamixel
            try:
                self.dyn = USB2Dynamixel_Device(dev_name = dyn_port, baudrate = dyn_baud)
            except:
                print("Failed to connect to dynamixel. Will continue trying.")
            else:
                good_conn = True
            if not good_conn:
                # above connection failed, try again.
                rospy.sleep(3)
                continue
            # Above connection succeeded, try to create servo object
            try:
                self.servo = Robotis_Servo(self.dyn, dyn_id)
            except:
                print("Failed to create servo object.  Will continue trying.")
                rospy.sleep(3)
            else:
                # everything was successful
                break
            

        # Servo Motor Setup
        self.dyn = USB2Dynamixel_Device(dev_name = dyn_port, baudrate = dyn_baud)
        self.servo = Robotis_Servo(self.dyn, dyn_id)

        # Inits the LIDAR pivot controller Subscriber
        rospy.Subscriber(TARGET_ANGLE_TOPIC, Float32, self.angle_callback)
        rospy.Subscriber(CMDS_TOPIC, String, self.cmds_callback)

        # Initialize service that gets the current angle of the lidar
        self.get_angle_service = rospy.Service(POS_SERV, LidarPivotAngle, self.handle_get_lidar_pivot_position)

        # Send servo to default position
        self.servo.move_angle(self.target_angle)
        self.current_angle = self.servo.read_angle()

    def angle_callback(self, angle):
        '''
        lidar_pivot_angle topic callback function
        '''
        self.target_angle = angle.data
        self.move_request = True

    def cmds_callback(self, data):
        '''
        '''
        cmd = data.data
        if cmd == "STAND":
            self.move_request = True
            self.target_angle = math.radians(self.PIVOT_STAND)
        elif cmd == "LAY-DOWN":
            self.move_request = True
            self.target_angle = math.radians(self.PIVOT_LAYDOWN)

    def handle_get_lidar_pivot_position(self, req):
        '''
        get_lidar_pivot_position Service handler.
        '''
        response = LidarPivotAngleResponse(self.servo.read_angle())
        return response

    def run(self):
        # #Runs while shut down message is not recieved.
        rate = rospy.Rate(10)
        while not rospy.is_shutdown():

            # Sends command to move Dynamixel to absolute position.
            if self.move_request: 
                self.move_request = False
                if math.degrees(self.target_angle) <= self.PIVOT_MAX and math.degrees(self.target_angle) >= self.PIVOT_MIN:
                    self.servo.move_angle(self.target_angle)
            rate.sleep()    # Keeps ROS from crashing

if __name__ == "__main__":
    controller = lidar_pivot_controller()
    controller.run()
