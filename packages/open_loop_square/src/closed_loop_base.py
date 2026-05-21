#!/usr/bin/env python3

import rospy
from duckietown_msgs.msg import Twist2DStamped
from duckietown_msgs.msg import FSMState
from duckietown_msgs.msg import WheelEncoderStamped


class ClosedLoopBase:
    def __init__(self, demo_name):
        rospy.init_node(demo_name, anonymous=True)

        self.cmd_msg = Twist2DStamped()
        self.is_running = False

        self.left_ticks = None
        self.right_ticks = None
        self.start_left_ticks = 0
        self.start_right_ticks = 0

        vehicle_name = rospy.get_namespace().strip("/")

        self.pub = rospy.Publisher(
            f'/{vehicle_name}/car_cmd_switch_node/cmd',
            Twist2DStamped,
            queue_size=1
        )

        self.sub = rospy.Subscriber(
            f'/{vehicle_name}/fsm_node/mode',
            FSMState,
            self.fsm_callback,
            queue_size=1
        )

        self.left_encoder_sub = rospy.Subscriber(
            f'/{vehicle_name}/left_wheel_encoder_driver_node/tick',
            WheelEncoderStamped,
            self.left_encoder_callback,
            queue_size=1
        )

        self.right_encoder_sub = rospy.Subscriber(
            f'/{vehicle_name}/right_wheel_encoder_driver_node/tick',
            WheelEncoderStamped,
            self.right_encoder_callback,
            queue_size=1
        )

    def left_encoder_callback(self, msg):
        self.left_ticks = msg.data

    def right_encoder_callback(self, msg):
        self.right_ticks = msg.data

    # Start movement only when Lane Following mode is selected
    def fsm_callback(self, msg):
        rospy.loginfo("State: %s", msg.state)

        if msg.state == "NORMAL_JOYSTICK_CONTROL":
            self.stop_robot()

        elif msg.state == "LANE_FOLLOWING" and not self.is_running:
            self.is_running = True
            rospy.sleep(1)
            self.move_robot()
            self.is_running = False

    def stop_robot(self):
        self.cmd_msg.header.stamp = rospy.Time.now()
        self.cmd_msg.v = 0.0
        self.cmd_msg.omega = 0.0
        self.pub.publish(self.cmd_msg)

    def publish_cmd(self, v, omega):
        self.cmd_msg.header.stamp = rospy.Time.now()
        self.cmd_msg.v = v
        self.cmd_msg.omega = omega
        self.pub.publish(self.cmd_msg)

    def wait_for_encoder_ticks(self):
        rate = rospy.Rate(10)
        while not rospy.is_shutdown() and (self.left_ticks is None or self.right_ticks is None):
            rospy.loginfo("Waiting for encoder ticks...")
            rate.sleep()

    def reset_encoder_start(self):
        self.wait_for_encoder_ticks()
        self.start_left_ticks = self.left_ticks
        self.start_right_ticks = self.right_ticks
        rospy.loginfo("Start left ticks: %s", self.start_left_ticks)
        rospy.loginfo("Start right ticks: %s", self.start_right_ticks)

    def average_tick_change(self):
        if self.left_ticks is None or self.right_ticks is None:
            return 0

        left_change = abs(self.left_ticks - self.start_left_ticks)
        right_change = abs(self.right_ticks - self.start_right_ticks)
        return (left_change + right_change) / 2.0

    def move_straight(self, target_ticks, speed):
        self.reset_encoder_start()
        rate = rospy.Rate(20)

        rospy.loginfo("Moving straight. Target ticks: %s Speed: %s", target_ticks, speed)

        while not rospy.is_shutdown() and self.average_tick_change() < target_ticks:
            self.publish_cmd(speed, 0.0)
            rate.sleep()

        final_ticks = self.average_tick_change()
        self.stop_robot()
        rospy.sleep(0.3)

        rospy.loginfo("Straight complete. Final ticks: %s", final_ticks)

    def rotate_in_place(self, target_ticks, omega):
        self.reset_encoder_start()
        rate = rospy.Rate(20)

        rospy.loginfo("Rotating. Target ticks: %s Omega: %s", target_ticks, omega)

        while not rospy.is_shutdown() and self.average_tick_change() < target_ticks:
            self.publish_cmd(0.0, omega)
            rate.sleep()

        final_ticks = self.average_tick_change()
        self.stop_robot()
        rospy.sleep(0.3)

        rospy.loginfo("Rotation complete. Final ticks: %s", final_ticks)

    def move_robot(self):
        pass

    def run(self):
        rospy.spin()
