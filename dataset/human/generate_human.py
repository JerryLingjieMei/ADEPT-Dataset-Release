import os

from easydict import EasyDict

from multiprocessing import Pool
from dataset.human.build_occluders import get_occluders
from dataset.human.build_objects import get_objects

from dataset.make_all import generate
from utils.io import write_serialized, catch_abort
from utils.constants import HUMAN_CONFIG_FOLDER, HUMAN_SIM_OUTPUT_FOLDER, HUMAN_RENDER_OUTPUT_FOLDER, \
    HUMAN_VIDEO_OUTPUT_FOLDER
from utils.misc import random_distinct_colors, get_host_id, BlenderArgumentParser
from utils.shape_net import SHAPE_NET_CATEGORY, SHAPE_CATEGORY


def parse_args():
    parser = BlenderArgumentParser(description='')
    parser.add_argument('--start', help='image index to start', type=int)
    parser.add_argument('--end', help='image index to end', type=int, default=int(1e8))
    parser.add_argument("--stride", help="image index stride", type=int, default=1)
    parser.add_argument("--requires_valid", type=int, default=0)
    parser.add_argument("--preview", type=int, default=0)
    return parser.parse_args()


_sim_time = {
    "disappear": 7.,
    "disappear_fixed": 9.5,
    "overturn": 4.5,
    "discontinuous": 11.,
    "block": 7.,
    "delay": 8.5
}


def get_sim_pattern(case, i):
    sim_time = _sim_time[case]
    if case == "overturn" and i >= 2:
        sim_time = 8.5
    if case == "block":
        step_pattern = [(0, 200), (1, 500)]
        return dict(sim_time=sim_time, step_pattern=step_pattern)
    return dict(sim_time=sim_time)


def generate_config(case, shape):
    scenes = []
    colors = random_distinct_colors(5)
    materials = ["rubber"] * 5
    case_occluders = get_occluders(case, colors, materials)
    case_objects = get_objects(case, shape, colors, materials)
    for i, (occluders, objects) in enumerate(zip(case_occluders, case_objects)):
        case_name = "human_{}_{}_{:01d}".format(case, shape, i)
        sim_pattern = get_sim_pattern(case, i)
        sim = dict(output_dir=os.path.join(HUMAN_SIM_OUTPUT_FOLDER, case_name), **sim_pattern)
        rendering = dict(motion_file=os.path.join(HUMAN_SIM_OUTPUT_FOLDER, case_name, "motion.json"),
                         output_dir=os.path.join(HUMAN_RENDER_OUTPUT_FOLDER, case_name))
        video = dict(frame_dir=os.path.join(HUMAN_RENDER_OUTPUT_FOLDER, case_name),
                     output_dir=os.path.join(HUMAN_VIDEO_OUTPUT_FOLDER, case_name),
                     save_ogv=1)
        scene = dict(case_name=case_name, objects=objects, occluders=occluders,
                     sim=sim, rendering=rendering, video=video)
        scenes.append(scene)
    return scenes


if __name__ == '__main__':
    args = parse_args()
    catch_abort()
    if args.start is None:
        args.start = get_host_id() % args.stride

    cases = ["disappear", "disappear_fixed", "overturn", "discontinuous", "block", "delay"]
    shapes = list(SHAPE_CATEGORY.keys()) + list(SHAPE_NET_CATEGORY.keys())
    worker_args = []
    case_configs = []
    for case in cases:
        for shape in shapes:
            case_config = generate_config(case, shape)
            case_configs.extend(case_config)

    case_configs = case_configs[args.start:args.end:args.stride]

    for config in case_configs:
        worker_args.append((EasyDict(config), args))
        write_serialized(config, os.path.join(HUMAN_CONFIG_FOLDER, config["case_name"] + ".yaml"))

    with Pool(5) as p:
        p.starmap(generate, worker_args)
