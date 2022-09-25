import os
from collections import defaultdict

from .io import mkdir

TYPES = {
    'cube': 'Cube',
    'sphere': 'Sphere',
    'cylinder': 'Cylinder',
    "cone": "Cone"
}

TYPES = defaultdict(lambda: "Sphere", **TYPES)

SHAPES = {
    'Cube': 'cube',
    'Occluder': 'cube',
    'Sphere': 'sphere',
    'Cylinder': 'cylinder',
    "Cone": "cone"
}

SHAPES = defaultdict(lambda: "sphere", **SHAPES)

SIMPLE_COLORS = {
    # "gray": [87, 87, 87],
    "red": [173, 35, 35],
    "blue": [42, 75, 215],
    "green": [29, 105, 20],
    "brown": [129, 74, 25],
    "purple": [129, 38, 192],
    "cyan": [41, 208, 208],
    "yellow": [255, 238, 51]
}

COLORS = {"{}-{}".format(x, y):
              [(x_c + y_c) / 2 for x_c, y_c in zip(x_cs, y_cs)]
          for x, x_cs in SIMPLE_COLORS.items() for y, y_cs in SIMPLE_COLORS.items()}
COLORS.update(SIMPLE_COLORS)

eps = .0001

CONTENT_FOLDER = os.getcwd()
CONFIG_FOLDER = mkdir(os.path.join(CONTENT_FOLDER, "config"))
SIM_OUTPUT_FOLDER = mkdir(os.path.join(CONTENT_FOLDER, "phys_sim", "output"))
RENDER_OUTPUT_FOLDER = mkdir(os.path.join(CONTENT_FOLDER, "render", "output"))
VIDEO_OUTPUT_FOLDER = mkdir(os.path.join(CONTENT_FOLDER, "output"))

MASK_AREA_THRESHOLD = 50

OCCLUDER_HALF_WIDTH = .04
prefix = "human_new"
HUMAN_CONFIG_FOLDER = mkdir(os.path.join(CONFIG_FOLDER, prefix))
HUMAN_SIM_OUTPUT_FOLDER = mkdir(os.path.join(SIM_OUTPUT_FOLDER, prefix))
HUMAN_RENDER_OUTPUT_FOLDER = mkdir(os.path.join(RENDER_OUTPUT_FOLDER, prefix))
HUMAN_VIDEO_OUTPUT_FOLDER = mkdir(os.path.join(VIDEO_OUTPUT_FOLDER, prefix))
