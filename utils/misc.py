import hashlib
import random
import socket
import sys
import argparse
from typing import Iterable

import numpy as np

from utils.constants import SIMPLE_COLORS


class BlenderArgumentParser(argparse.ArgumentParser):
    @staticmethod
    def _get_real_args():
        """
        Given the sys.argv as a list of strings, this method returns the
        sublist right after the '--' element (if present, otherwise returns
        an empty list).
        """
        if "--" in sys.argv:
            idx = sys.argv.index("--")
            return sys.argv[idx + 1:]
        else:
            return sys.argv[1:]

    def parse_args(self, **kwargs):
        """
        This method is expected to behave identically as in the superclass,
        except that the sys.argv list will be pre-processed using
        _get_argv_after_doubledash before. See the docstring of the class for
        usage examples and details.
        """
        return super(BlenderArgumentParser, self).parse_args(args=BlenderArgumentParser._get_real_args())


def rand(low, high):
    """A random float from low to high"""
    return np.random.uniform(low, high)


def random_material(num):
    """Generate random materials"""
    materials = ["rubber"] * num
    if len(materials) == 1:
        return materials[0]
    return materials


def random_distinct_colors(num):
    """Generate random distinct materials"""
    colors = random.sample(list(SIMPLE_COLORS.keys()), num)
    if len(colors) == 1:
        return colors[0]
    return colors


def repeat_scale(scale):
    """Promote a scalar scale to a list"""
    if isinstance(scale, Iterable):
        return scale
    else:
        return scale, scale, scale


def get_host_id():
    x = socket.gethostname()[-2:]
    try:
        return int(x) - 1
    except:
        return 0


def md5_hash(x):
    if isinstance(x, (tuple, list)):
        m = hashlib.md5()
        for s in x:
            assert isinstance(s, (int, str))
            m.update(str(s).encode('utf-8'))
        return m
    elif isinstance(x, (int, str)):
        x = str(x).encode('utf-8')
        return hashlib.md5(x)
    else:
        raise ValueError(f'util.md5_hash doesnt currently support type({type(x)}')


def int_hash(x, max=int(1e7)):
    md5 = int(md5_hash(x).hexdigest(), 16)
    h = abs(md5) % max
    return h
