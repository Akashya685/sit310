#!/usr/bin/env python3

import rospy
from closed_loop_base import ClosedLoopBase


class RotateSlow(ClosedLoopBase):
    def move_robot(self):
        self.rotate_in_place(80, 2.0)
        self.stop_robot()


if __name__ == '__main__':
    try:
        duckiebot_movement = RotateSlow('closed_loop_rotate_slow_node')
        duckiebot_movement.run()
    except rospy.ROSInterruptException:
        pass
