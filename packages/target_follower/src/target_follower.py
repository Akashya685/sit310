#!/usr/bin/env python3

import rospy
from duckietown_msgs.msg import Twist2DStamped
from duckietown_msgs.msg import FSMState
from duckietown_msgs.msg import AprilTagDetectionArray

class Target_Follower:
    def __init__(self):
        
        #Initialize ROS node
        rospy.init_node('target_follower_node', anonymous=True)

        # When shutdown signal is received, we run clean_shutdown function
        rospy.on_shutdown(self.clean_shutdown)
        
        ###### Init Pub/Subs. REMEMBER TO REPLACE "akandb" WITH YOUR ROBOT'S NAME #####
        self.cmd_vel_pub = rospy.Publisher('car_cmd_switch_node/cmd', Twist2DStamped, queue_size=1)
        rospy.Subscriber('apriltag_detector_node/detections', AprilTagDetectionArray, self.tag_callback, queue_size=1)
        ################################################################

        self.seek_omega = 0.10
        self.look_omega = 0.15
        self.center_tolerance = 0.25

        rospy.spin() # Spin forever but listen to message callbacks

    # Apriltag Detection Callback
    def tag_callback(self, msg):
        self.move_robot(msg.detections)
 
    # Stop Robot before node has shut down. This ensures the robot keep moving with the latest velocity command
    def clean_shutdown(self):
        rospy.loginfo("System shutting down. Stopping robot...")
        self.stop_robot()

    # Sends zero velocity to stop the robot
    def stop_robot(self):
        cmd_msg = Twist2DStamped()
        cmd_msg.header.stamp = rospy.Time.now()
        cmd_msg.v = 0.0
        cmd_msg.omega = 0.0
        self.cmd_vel_pub.publish(cmd_msg)

    def move_robot(self, detections):

        #### YOUR CODE GOES HERE ####

        cmd_msg = Twist2DStamped()
        cmd_msg.header.stamp = rospy.Time.now()
        cmd_msg.v = 0.0

        if len(detections) == 0:
            rospy.loginfo("No tag detected")
            cmd_msg.omega = self.seek_omega
            self.cmd_vel_pub.publish(cmd_msg)
            return

        x = detections[0].transform.translation.x
        y = detections[0].transform.translation.y
        z = detections[0].transform.translation.z

        rospy.loginfo("x,y,z: %f %f %f", x, y, z)

        if abs(x) < self.center_tolerance:
            cmd_msg.omega = 0.0
        elif x > 0:
            cmd_msg.omega = -self.look_omega
        else:
            cmd_msg.omega = self.look_omega

        self.cmd_vel_pub.publish(cmd_msg)

        #############################

if __name__ == '__main__':
    try:
        target_follower = Target_Follower()
    except rospy.ROSInterruptException:
        pass
