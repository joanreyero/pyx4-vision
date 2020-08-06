#!/usr/bin/env python2
from __future__ import division
from pyx4_base.pyx4_base import *
from pyx4_base.mission_states import *

NODE_NAME = 'vision'


class Vision(Pyx4_base):

    def __init__(self):
        instructions = Vision.get_flight_instructions()
        super(Vision, self).__init__(instructions)

    @staticmethod
    def get_flight_instructions():
        return {0: Arming_state(tiemout=90),
                1: Take_off_state(to_altitude_tgt=3.0),
                2: Waypoint_state(state_label='to_object',
                                  waypoint_type='vel',
                                  xy_type='vel',
                                  x_setpoint=3.0,
                                  y_setpoint=0.0,
                                  z_type='pos',
                                  z_setpoint=3.0,
                                  yaw_type='vel',
                                  yaw_setpoint=0.0,
                                  coordinate_frame='1',
                                  timeout=30)}
    

if __name__ == '__main__':
    rospy.init_node(NODE_NAME, anonymous=True, log_level=rospy.DEBUG)
    vision = Vision()
    vision.run()
    
