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
        rospy.Subscriber(
            f'/{vehicle_name}/fsm_node/mode',
            FSMState,
            self.fsm_callback,
            queue_size=1
        )

    # robot only moves when lane following is selected on the duckiebot joystick app
    def fsm_callback(self, msg):
        rospy.loginfo("State: %s", msg.state)

        if msg.state == "NORMAL_JOYSTICK_CONTROL":
            self.stop_robot()

        elif msg.state == "LANE_FOLLOWING" and not self.is_running:
            self.is_running = True
            rospy.sleep(1)
            self.move_robot()
            self.is_running = False

    # Sends zero velocities to stop the robot
    def stop_robot(self):
        self.cmd_msg.header.stamp = rospy.Time.now()
        self.cmd_msg.v = 0.0
        self.cmd_msg.omega = 0.0
        self.pub.publish(self.cmd_msg)

    # Spin forever but listen to message callbacks
    def run(self):
        rospy.spin()

    # Robot drives in a square and then stops
    def move_robot(self):
        forward_speed = 0.35
        turn_speed = 3.0

        forward_time = 2.3
        turn_time = 1.05

        rospy.loginfo("Starting square...")

        for i in range(4):
            # move forward
            self.cmd_msg.header.stamp = rospy.Time.now()
            self.cmd_msg.v = forward_speed
            self.cmd_msg.omega = 0.0
            self.pub.publish(self.cmd_msg)
            rospy.loginfo("Forward %d", i + 1)
            rospy.sleep(forward_time)

            # stop briefly
            self.stop_robot()
            rospy.sleep(0.2)

            # turn in place
            self.cmd_msg.header.stamp = rospy.Time.now()
            self.cmd_msg.v = 0.0
            self.cmd_msg.omega = turn_speed
            self.pub.publish(self.cmd_msg)
            rospy.loginfo("Turn %d", i + 1)
            rospy.sleep(turn_time)

            # stop briefly
            self.stop_robot()
            rospy.sleep(0.2)

        self.stop_robot()
        rospy.loginfo("Square complete")


if __name__ == '__main__':
    try:
        duckiebot_movement = Drive_Square()
        duckiebot_movement.run()
    except rospy.ROSInterruptException:
        pass
