import numpy as np

from utils.geometry import deg2rad


def convert_step_patterns(step_segments):
    """Convert step patterns from lists of start-end-steps to one single array"""
    return np.concatenate(list(np.full((step,), val) for val, step in step_segments))


def convert_rot_patterns(rot_segments):
    """Convert rotation patterns from lists of start-end-steps to one single array"""
    return np.concatenate(
        list(np.linspace(start=deg2rad(start), stop=deg2rad(stop), num=num) for start, stop, num in rot_segments))


def convert_trans_patterns(trans_segments):
    """Convert translation patterns from lists of start-end-steps to one single array"""
    return np.concatenate(
        list(np.linspace(start=start, stop=stop, num=num) for start, stop, num in trans_segments))
