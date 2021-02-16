import numpy as np
from camera import Camera
import rospy
from collections import namedtuple
from matchedFilters import MatchedFilter
from avoidance_functions import get_activation



class TunnelCenteringBehaviour(object):

    def __init__(self, camera, num_filters=5, dual=False):
        self.flow = None
        self.num_filters = num_filters
        self.cam = camera
        self.dual = dual

    def crop_flow(self, flow, crop=0.5):
        # The height of each flow will be the same as the width
        height = flow.shape[1] / (self.num_filters)
            
        if crop:
            amount = int(crop * flow.shape[0] / 2)
            flow = flow[amount:-amount, :, :]

        if self.num_filters == 1:
            return [flow,]
        
        return np.array_split(flow, self.num_filters, axis=1)

    def get_matched_filters(self, flows):
        # Needed for the MF functions
        height, width, _ = flows[0].shape
        # FOV of a single filter
        original_fov = self.cam.fovx_deg
        fov = int(original_fov / self.num_filters)
        
        filter_angles = [-45, -15, 15, 45]
        #filter_angles = [-48, -24, 0, 24, 48]

        if self.dual:
            offset = 10
            return [(MatchedFilter(
                flow.shape[1], flow.shape[0], (fov, fov), 
                orientation=[0, 0, offset],
                axis=[0, 0, filter_angles[i]]
                ).matched_filter, 
                     MatchedFilter(
                flow.shape[1], flow.shape[0], (fov, fov), 
                orientation=[0, 0, -offset],
                axis=[0, 0, filter_angles[i]]
                ).matched_filter)
                     for i, flow in enumerate(flows)]

        return [MatchedFilter(
            flow.shape[1], flow.shape[0], (fov, fov), 
            axis=[0, 0, filter_angles[i]]
            ).matched_filter for i, flow in enumerate(flows)]

    def step(self, flow):
        flows = self.crop_flow(flow, crop=False)
        matched_filters = self.get_matched_filters(flows)
        if self.dual:
            activations = [np.mean([
                get_activation(flow, matched_filters[i][0]),
                get_activation(flow, matched_filters[i][1])
                ]) for i, flow in enumerate(flows)]
    
        else:
            activations = [get_activation(flow, matched_filters[i]) 
                        for i, flow in enumerate(flows)]

        return activations
        