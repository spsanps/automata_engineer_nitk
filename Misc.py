__author__ = 'sanps'

import math

import numpy as np
import cv2

mag = lambda x: math.sqrt(sum([math.pow(i, 2) for i in x]))  # Magnitude of vector
distance = lambda a, b: mag(a - b)


def map_to_cell(p):  # Debugging/testing left
    p = p / 2.4384 * 8 - np.array((0.5, 0.5))
    rounded = np.vectorize(round)(p)
    return tuple(rounded.astype(int))


def map_to_meters(p):
    return (np.array(p) + np.array((0.5, 0.5))) / 8 * 2.4384

#def map_to_meters_from_pic(p):
    #raise NotImplementedError

def center_of_contour(contour):
    M = cv2.moments(contour)
    cx, cy = int(M['m10'] / M['m00']), int(M['m01'] / M['m00'])
    return np.array((cx, cy))


def angle_of(vector):
    x, y = vector
    if x == 0: return np.deg2rad(90)
    if x < 0: return math.pi + np.arctan(y / x)
    return np.arctan(y / x)
