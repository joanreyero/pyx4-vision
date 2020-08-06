#!/usr/bin/env python2
from __future__ import division
import numpy as np

class MatchedFilter():
    def __init__(self, cam_w, cam_h, fov, fov_type='fov',
                 orientation=[0.0, 0.0, 0.0],
                 axis=[1.0, 0.0, 0.0]):
        self.orientation = orientation
        self.axis = axis
        self.cam_w = cam_w
        self.cam_h = cam_h
        if fov_type in ['K', 'intrinsic_matrix']:
            self.fovx, self.fovy = MatchedFilter._get_fov(fov, cam_w, cam_h)
        else:
            self.fovx, self.fovy = fov[0], fov[1]
        self.matched_filter = self.generate_filter(orientation, axis)

    @staticmethod
    def _get_fov(K, cam_w, cam_h):
        
        def compute_fov(d, f):
            return np.arctan(d / (2 * f))

        K_flat = np.array(K).flatten()
        return (compute_fov(cam_w, float(K_flat[0])),
                compute_fov(cam_h, float(K_flat[4])))

    def _get_anticipated_viewing_directions(self, orientation):
        vertical_views = (((np.arange(self.cam_h, dtype=float) -
                            self.cam_h / 2.0) / float(self.cam_h)) *
                          self.fovy)
        horizontal_views = (((np.arange(self.cam_w, dtype=float) -
                              self.cam_w / 2.0) / float(self.cam_w)) *
                            self.fovx)
        D = -np.ones([self.cam_h, self.cam_w, 3])
        D[:, :, 0], D[:, :, 1] = np.meshgrid(np.tan(horizontal_views),
                                             np.tan(vertical_views))
        
        return self._rotate_viewing_directions(D, orientation)

    def _rotate_viewing_directions(self, D, orientation):
        yaw, pitch, roll = orientation
        rot_mat = self._rotation_matrix_from_rpy_degs(yaw, pitch, roll)
        for ii in range(self.cam_h):
            for jj in range(self.cam_w):
                D[ii, jj, :] = np.matmul(D[ii, jj, :], rot_mat)
        return D

    def _rotation_matrix_from_rpy_degs(self, yaw, pitch, roll):
        """
        In camera coordinates
          x - pitch
          y - roll
          z yaw
        """
        rx = np.deg2rad(pitch)
        ry = np.deg2rad(roll)
        rz = np.deg2rad(yaw)

        Rx = np.array([[1, 0, 0], [0, np.cos(rx), -np.sin(rx)],
                       [0, np.sin(rx), np.cos(rx)]])
        Ry = np.array([[np.cos(ry), 0, np.sin(ry)], [0, 1, 0],
                       [-np.sin(ry), 0, np.cos(ry)]])
        Rz = np.array([[np.cos(rz), -np.sin(rz), 0],
                       [np.sin(rz), np.cos(rz), 0], [0, 0, 1]])

        rot_mat = np.matmul(Rx, Rz)
        return rot_mat
            
    def generate_filter(self, orientation, axis):
        D = self._get_anticipated_viewing_directions(orientation)
        print(D.shape)
        sin_theta = np.linalg.norm(D[:, :, 0:2], axis=2) + 1e-14
        print(sin_theta.shape)
        mag_temp = np.linalg.norm(D, axis=2)
        D /= np.expand_dims(mag_temp, axis=2)
        mf = -np.cross(np.cross(D, axis), D)[:, :, 0:2]
        return mf

    def plot(self):
        """
        Plot the matched filters that have been generated by this class
        :return:
        """
        import matplotlib.pyplot as plt
        Y = ((np.arange(self.cam_h, dtype=float) - self.cam_h / 2.0))
             #/ float(
            #self.cam_h)) * self.fovy
        X = ((np.arange(self.cam_w, dtype=float) - self.cam_w / 2.0)) #/ float(
            #self.cam_w)) * self.fovx
        U = self.matched_filter[:, :, 0]
        V = self.matched_filter[:, :, 1]

        plt.quiver(X, Y, U, V)
        plt.show()

        
if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(description='Create matched filters')
    parser.add_argument('--width', type=int, default=640,
                        help="""Camera's width
                        Default: 300""")
    parser.add_argument('--height', type=int, default=360,
                        help="""Camera's height
                        Default: 300""")
    parser.add_argument('-f','--fov', nargs='+',
                        default=[205.46963709898583, 0.0, 320.5,
                                 0.0, 205.46963709898583, 180.5,
                                 0.0, 0.0, 1.0],
                        help="""The x and y fov or intrinsic matrix,
                        either flattened or as a matrix.
                        Default:
                        [205.46963709898583, 0.0, 320.5,
                         0.0, 205.46963709898583, 180.5,
                         0.0, 0.0, 1.0]""")
    parser.add_argument('-t', '--fov_type', default='K',
                        help="""Type of fov given.
                        Either 'fov' if fovx and fovy are given,
                        or 'K' if the intrinsic matrix is given.
                        Default: K""")
    parser.add_argument('-o', '--orientation', nargs='+', default=[0.0, 0.0, 0.0],
                        help="""Orientation of the camera.
                        Default [0.0, 0.0, 0.0]""")
    parser.add_argument('-a', '--axis', nargs='+', default=[1.0, 0.0, 0.0],
                        help="""Prefered axis of orientation
                        Default: [1.0, 0.0, 0.0]""")
    args = parser.parse_args()
    mf = MatchedFilter(args.width, args.height,
                       args.fov, args.fov_type,
                       args.orientation, args.axis)
    mf.plot()

    


