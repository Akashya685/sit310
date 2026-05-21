#!/usr/bin/env python3

import rospy
from closed_loop_base import ClosedLoopBase


class StraightSlow(ClosedLoopBase):
    def move_robot(self):
        self.move_straight(135, 0.25)
        self.stop_robot()


if __name__ == '__main__':
    try:
        duckiebot_movement = StraightSlow('closed_loop_straight_slow_node')
        duckiebot_movement.run()
    except rospy.ROSInterruptException:
        pass
