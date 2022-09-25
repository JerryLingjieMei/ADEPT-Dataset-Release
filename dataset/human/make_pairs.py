import argparse
import os
import random

from utils.constants import VIDEO_OUTPUT_FOLDER, HUMAN_VIDEO_OUTPUT_FOLDER
from utils.io import read_serialized, write_serialized, mkdir, clr_dir
from utils.shape_net import SHAPE_CATEGORY

CASE_PAIRS = {
    "create": [("disappear", 2),
               ("disappear", 0),
               ("disappear", 3),
               ("disappear", 4)],
    "vanish": [("disappear_fixed", 1),
               ("disappear_fixed", 0),
               ("disappear_fixed", 3),
               ("disappear_fixed", 4)],
    "short-overturn": [("overturn", 0),
                       ("overturn", 1)],
    "long-overturn": [("overturn", 3),
                      ("overturn", 2)],
    "visible-discontinuous": [("discontinuous", 2),
                              ("discontinuous", 3),
                              ("discontinuous", 5),
                              ("discontinuous", 4)],
    "invisible-discontinuous": [("discontinuous", 1),
                                ("discontinuous", 0),
                                ("discontinuous", 5),
                                ("discontinuous", 4)],
    "delay": [("delay", 1),
              ("delay", 0)],
    "block": [("block", 1),
              ("block", 0)]
}

SHAPE_CATS = ["geometric", "real-life", "in-class", "out-class"]


def get_shapes_from_cat(shape_cat):
    if shape_cat == "geometric":
        big_shapes = ["cube", "sphere", "cone", "cylinder"]
    elif shape_cat == "real-life":
        big_shapes = [x for x in SHAPE_CATEGORY if x not in ["cube", "sphere", "cone", "cylinder"]]
    elif shape_cat == "in-class":
        big_shapes = ["{:04d}".format(x) for x in range(55) if x % 5 != 0]
    else:
        big_shapes = ["{:04d}".format(x) for x in range(55) if x % 5 == 0]
    return big_shapes


_suffices = [".mp4", ".ogv"]


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--overwrite", type=int, default=0)
    return parser.parse_args()


if __name__ == '__main__':
    args = parse_args()
    new_human_folder = mkdir(os.path.join(VIDEO_OUTPUT_FOLDER, "human_new_2"))
    clr_dir(new_human_folder)
    file_map = dict(origin=[], destination=[])
    experiment_id = 0
    for shape_cat in SHAPE_CATS:
        big_shapes = get_shapes_from_cat(shape_cat)
        for violation, pairs in CASE_PAIRS.items():
            shapes = random.sample(big_shapes, k=2)
            for shape in shapes:
                case, index = pairs[0]
                origin = "human_{}_{}_{}".format(case, shape, index)
                destination = "{:03d}_surprise_human_{}_{}_{}".format(experiment_id, case, shape, index)
                print(origin, destination)
                experiment_id += 1

                for i, (case, index) in enumerate(pairs[1:], 1):
                    origin = "human_{}_{}_{}".format(case, shape, index)
                    destination = "{:03d}_control_human_{}_{}_{}".format(experiment_id, case, shape, index)
                    file_map["origin"].append(origin)
                    file_map["destination"].append(destination)
                    experiment_id += 1

    if args.overwrite:
        write_serialized(file_map, "dataset/human/pairs.json")
    else:
        file_map = read_serialized("dataset/human/pairs.json")

    for origin, destination in zip(file_map["origin"], file_map["destination"]):
        for suffix in _suffices:
            os.system("cp {} {}".format(
                os.path.join(HUMAN_VIDEO_OUTPUT_FOLDER, "{}{}".format(origin, suffix))
                , os.path.join(new_human_folder, "{}{}".format(destination, suffix))))
