#!/usr/bin/env python3

#Python Libs
import sys, time

#numpy
import numpy as np

#OpenCV
import cv2
from cv_bridge import CvBridge

#ROS Libraries
import rospy
import roslib

#ROS Message Types
from sensor_msgs.msg import CompressedImage

class Lane_Detector:
    def __init__(self):
        self.cv_bridge = CvBridge()

        #### REMEMBER TO CHANGE THE TOPIC NAME! #####        
        self.image_sub = rospy.Subscriber('/mybotdan/camera_node/image/compressed', CompressedImage, self.image_callback, queue_size=1)
        #############################################

        rospy.init_node("my_lane_detector")

    def output_lines(self, original_image, lines, color):
        output = np.copy(original_image)

        if lines is not None:
            for line in lines:
                x1, y1, x2, y2 = line[0]
                cv2.line(output, (x1, y1), (x2, y2), color, 3, cv2.LINE_AA)
                cv2.circle(output, (x1, y1), 3, (0, 255, 0), -1)
                cv2.circle(output, (x2, y2), 3, (0, 0, 255), -1)

        return output

    def image_callback(self,msg):
        rospy.loginfo("image_callback")


        # Convert to opencv image 
        img = self.cv_bridge.compressed_imgmsg_to_cv2(msg, "bgr8")
        
        #### YOUR CODE GOES HERE ####

        img = cv2.flip(img, 0)

        height, width, channels = img.shape
        cropped_img = img[int(height * 0.45):height, 0:width]

        hsv_img = cv2.cvtColor(cropped_img, cv2.COLOR_BGR2HSV)

        lower_white = np.array([0, 0, 180])
        upper_white = np.array([180, 70, 255])
        white_mask = cv2.inRange(hsv_img, lower_white, upper_white)
        white_filtered = cv2.bitwise_and(cropped_img, cropped_img, mask=white_mask)

        lower_yellow = np.array([15, 80, 80])
        upper_yellow = np.array([40, 255, 255])
        yellow_mask = cv2.inRange(hsv_img, lower_yellow, upper_yellow)
        yellow_filtered = cv2.bitwise_and(cropped_img, cropped_img, mask=yellow_mask)

        gray_cropped = cv2.cvtColor(cropped_img, cv2.COLOR_BGR2GRAY)
        canny_edges = cv2.Canny(gray_cropped, 80, 160)

        white_edges = cv2.Canny(white_mask, 80, 160)
        yellow_edges = cv2.Canny(yellow_mask, 80, 160)

        white_lines = cv2.HoughLinesP(
            white_edges,
            rho=1,
            theta=np.pi / 180,
            threshold=25,
            minLineLength=20,
            maxLineGap=15
        )

        yellow_lines = cv2.HoughLinesP(
            yellow_edges,
            rho=1,
            theta=np.pi / 180,
            threshold=25,
            minLineLength=20,
            maxLineGap=15
        )

        hough_output = self.output_lines(cropped_img, white_lines, (255, 0, 0))
        hough_output = self.output_lines(hough_output, yellow_lines, (0, 0, 255))

        cv2.imshow('white_filtered_image', white_filtered)
        cv2.imshow('yellow_filtered_image', yellow_filtered)
        cv2.imshow('canny_edges', canny_edges)
        cv2.imshow('hough_lines_output', hough_output)

        #############################

        cv2.waitKey(1)

    def run(self):
    	rospy.spin() # Spin forever but listen to message callbacks

if __name__ == "__main__":
    try:
        lane_detector_instance = Lane_Detector()
        lane_detector_instance.run()
    except rospy.ROSInterruptException:
        pass
