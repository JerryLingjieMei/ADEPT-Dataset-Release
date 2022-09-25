import bpy
import mathutils
import math
from collections.abc import Iterable
import numpy as np


def deg2rad(degs):
    """Convert degree iterables to radian iterables"""
    if isinstance(degs, Iterable):
        rads = []
        for a in degs:
            rads.append(a * math.pi / 180)
    else:
        rads = degs * math.pi / 180
    return rads


def reverse_xyz(t):
    """Point an 3d vector to the opposite direction"""
    return [-t[0], -t[1], -t[2]]


def reverse_euler(t):
    """Point a xyz euler to the opposite direction"""
    return [-t[2], -t[1], -t[0]]


def convert_euler(bullet_euler):
    """
    input blender rad angles and convert to bullet rad coordinates
    """
    return list(mathutils.Euler(bullet_euler, "ZYX"))


def convert_inverse_euler(blender_euler):
    """
    input rad euler angles and convert to blender rad coordinates
    """
    return list(mathutils.Euler(blender_euler, "ZYX"))


def get_retrospective_location(location, velocity, time):
    """Calculate the original location and velocity based on the one at time t"""
    return [l - v * time for l, v in zip(location, velocity)]


def get_prospective_location(location, velocity, time):
    """Calculate the final location and velocity based on the one at time 0"""
    return [l + v * time for l, v in zip(location, velocity)]


def get_speed(start, end, time):
    return (end - start) / time


def random_spherical_point():
    vec = np.random.randn(3)
    vec /= np.linalg.norm(vec)
    return vec.tolist()
