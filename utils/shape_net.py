import re
import os
import numpy as np
from utils.io import read_serialized, mkdir
from utils.constants import CONTENT_FOLDER

"""
_shape_net_names = ['airplane', 'ashcan', 'bag', 'basket', 'bathtub', 'bed', 'bench', 'bicycle', 'birdhouse',
                    'bookshelf', 'bottle', 'bowl', 'bus', 'cabinet', 'camera', 'can', 'cap', 'car', 'chair',
                    'computer_keyboard', 'dishwasher', 'display', 'earphone', 'faucet', 'file', 'guitar', 'helmet',
                    'jar', 'knife', 'lamp', 'laptop', 'loudspeaker', 'mailbox', 'microphone', 'microwave', 'motorbike',
                    'mug', 'piano', 'pillow', 'pistol', 'pot', 'printer', 'remote', 'rifle', 'rocket', 'skateboard',
                    'sofa', 'stove', 'table', 'telephone', 'tower', 'train', 'vessel', 'washer', 'wine_bottle']
"""

_shape_net_names_sample = ['airplane', 'ashcan', 'bag', 'basket', 'bathtub', 'bed', 'bench', 'bicycle', 'birdhouse',
                    'bookshelf', 'bottle', 'bowl', 'bus', 'cabinet', 'camera', 'can', 'cap']

SIM_SHAPE_FOLDER = mkdir(os.path.join(CONTENT_FOLDER, "phys_sim", "data", "shapes"))
RENDER_SHAPE_FOLDER = mkdir(os.path.join(CONTENT_FOLDER, "render", "data", "shapes"))

SIM_SHAPE_NET_FOLDER = mkdir(os.path.join(CONTENT_FOLDER, "phys_sim", "data", "additional_shapes"))
RENDER_SHAPE_NET_FOLDER = mkdir(os.path.join(CONTENT_FOLDER, "render", "data", "additional_shapes"))

if len(os.listdir(SIM_SHAPE_NET_FOLDER)) > 0:
    SHAPE_NET_CATEGORY = {"{:04d}".format(i): name for i, name in enumerate(_shape_net_names_sample)}
    SHAPE_NET_NUMS = {"{:04d}".format(i): len(os.listdir(os.path.join(SIM_SHAPE_NET_FOLDER, "{:04d}".format(i))))
                      for i in range(len(_shape_net_names_sample))}
    SHAPE_NET_CATEGORY_INVERSE = {v: k for k, v in SHAPE_NET_CATEGORY.items()}

if os.path.exists(os.path.join(SIM_SHAPE_NET_FOLDER, "all_dimensions.json")):
    _shape_net_dimensions = read_serialized(os.path.join(SIM_SHAPE_NET_FOLDER, "all_dimensions.json"))
else:
    _shape_net_dimensions = dict()

if os.path.exists(os.path.join(SIM_SHAPE_NET_FOLDER, "categories_to_rotate.json")):
    _rotate_index = read_serialized(os.path.join(SIM_SHAPE_NET_FOLDER, "categories_to_rotate.json"))
    ROTATE_SHAPE_CATEGORY = {k: k for k, v in _rotate_index.items() if v > 0}
else:
    ROTATE_SHAPE_CATEGORY = dict()

if os.path.exists(os.path.join(SIM_SHAPE_FOLDER, "all_dimensions.json")):
    _shape_dimensions = read_serialized(os.path.join(SIM_SHAPE_FOLDER, "all_dimensions.json"))
    SHAPE_CATEGORY = {k: k for k in _shape_dimensions.keys()}
else:
    _shape_dimensions = dict()
SHAPE_DIMENSIONS = {**_shape_dimensions, **_shape_net_dimensions}
print(SHAPE_DIMENSIONS)

def random_shape_net(cat_id, is_train):
    cat_id = int(cat_id)
    if is_train:
        assert cat_id % 5 != 0
        shape_id = np.random.choice([x for x in range(SHAPE_NET_NUMS["{:04d}".format(cat_id)]) if x % 5 != 0])
    else:
        if cat_id % 5 == 0:
            shape_id = np.random.randint(0, SHAPE_NET_NUMS["{:04d}".format(cat_id)])
        else:
            shape_id = np.random.choice([x for x in range(SHAPE_NET_NUMS["{:04d}".format(cat_id)]) if x % 5 == 0])
    return "{:04d}{:06d}".format(cat_id, shape_id)


def get_random_shape(shape):
    if shape in SHAPE_NET_CATEGORY:
        return random_shape_net(shape, False)
    else:
        return shape


def get_shape_blend(name):
    return os.path.join(RENDER_SHAPE_NET_FOLDER, name[:4], "{}.blend".format(name[4:]), "Object", name)
