#!/usr/bin/env python3

import rospy
from duckietown_msgs.msg import Twist2DStamped
from duckietown_msgs.msg import FSMState


class Drive_Square:
    def __init__(self):
        self.cmd_msg = Twist2DStamped()
        self.is_running = False

        rospy.init_node('drive_square_node', anonymous=True)

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

    def run(self):
        rospy.spin()

    def move_robot(self):
        forward_speed = 0.30
        turn_speed = 2.6

        # Move forward about 1 meter
        forward_time = 3.3

        # Turn left about 90 degrees
        turn_time = 1.18

        print("RUNNING 1 METER SQUARE CODE")

        rate = rospy.Rate(10)

        
        for i in range(4):

            start_time = rospy.Time.now()
            while (rospy.Time.now() - start_time).to_sec() < forward_time:
                self.cmd_msg.header.stamp = rospy.Time.now()
                self.cmd_msg.v = forward_speed
                self.cmd_msg.omega = 0.0
                self.pub.publish(self.cmd_msg)
                rate.sleep()

            self.stop_robot()
            rospy.sleep(0.3)

            start_time = rospy.Time.now()
            while (rospy.Time.now() - start_time).to_sec() < turn_time:
                self.cmd_msg.header.stamp = rospy.Time.now()
                self.cmd_msg.v = 0.0
                self.cmd_msg.omega = turn_speed
                self.pub.publish(self.cmd_msg)
                rate.sleep()

            self.stop_robot()
            rospy.sleep(0.3)

        self.stop_robot()
        rospy.loginfo("Square complete")


if __name__ == '__main__':
    try:
        duckiebot_movement = Drive_Square()
        duckiebot_movement.run()
    except rospy.ROSInterruptException:
        pass
