#!/usr/bin/env python3
import rospy
from closed_loop_base import ClosedLoopBase


class ClosedLoopSquare(ClosedLoopBase):
    def move_robot(self):
        straight_ticks = 200
        rotation_ticks = 50

        forward_speed = 0.30
        turn_speed = 1.0

        print("RUNNING CLOSED LOOP SQUARE CODE")

        for i in range(4):

            # Move forward about 1 meter
            self.move_straight(straight_ticks, forward_speed)

            # Turn left about 90 degrees
            self.rotate_in_place(rotation_ticks, turn_speed)

        self.stop_robot()
        rospy.loginfo("Square complete")


if __name__ == '__main__':
    try:
        duckiebot_movement = ClosedLoopSquare('closed_loop_square_node')
        duckiebot_movement.run()
    except rospy.ROSInterruptException:
        pass
