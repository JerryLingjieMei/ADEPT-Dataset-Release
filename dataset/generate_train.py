from multiprocessing import Pool, cpu_count
import os
import random

import numpy as np
from easydict import EasyDict

from dataset.make_all import generate
from utils.geometry import random_spherical_point, get_prospective_location
from utils.io import mkdir, write_serialized, catch_abort
from utils.constants import CONFIG_FOLDER, SIM_OUTPUT_FOLDER, RENDER_OUTPUT_FOLDER, VIDEO_OUTPUT_FOLDER, \
    OCCLUDER_HALF_WIDTH
from utils.misc import rand, random_distinct_colors, repeat_scale, get_host_id, BlenderArgumentParser
from utils.shape_net import SHAPE_DIMENSIONS, random_shape_net

train_prefix = "train"
TRAIN_CONFIG_FOLDER = mkdir(os.path.join(CONFIG_FOLDER, train_prefix))
TRAIN_SIM_OUTPUT_FOLDER = mkdir(os.path.join(SIM_OUTPUT_FOLDER, train_prefix))
TRAIN_RENDER_OUTPUT_FOLDER = mkdir(os.path.join(RENDER_OUTPUT_FOLDER, train_prefix))
TRAIN_VIDEO_OUTPUT_FOLDER = mkdir(os.path.join(VIDEO_OUTPUT_FOLDER, train_prefix))


def parse_args():
    parser = BlenderArgumentParser(description='')
    parser.add_argument('--start', help='image index to start', type=int, default=0)
    parser.add_argument('--start_index', help='image index to start', type=int)
    parser.add_argument('--end', help='image index to end', type=int, required=True)
    parser.add_argument("--stride", help="image index stride", type=int, default=1)
    parser.add_argument("--requires_valid", type=int, default=1)
    parser.add_argument("--preview", type=int, default=0)
    parser.add_argument("--is_single_image", type=int, default=0)
    return parser.parse_args()


def get_occluders(colors, materials):
    occluders = []
    occluder_rand = rand(0, 1)
    init_pos = (rand(-.5, .5), rand(-1., 1.), 0)

    half_width = rand(.5, 1.5)
    half_height = rand(.5, 1.)

    scale = (OCCLUDER_HALF_WIDTH, half_width, half_height)

    init_orn = (0, 0, rand(-20, 20))
    if occluder_rand < .85:
        # rotating occluder
        joint_rand = rand(0, 1)
        joint_t = np.random.randint(10, 25)
        if joint_rand < 1 / 6:
            joint_pattern = [(90, 90, joint_t), (90, 0, 250 - joint_t),
                             (0, 90, 250 - joint_t), (90, 90, joint_t)]
        elif joint_rand < 1 / 3:
            joint_pattern = [(90, 90, joint_t), (90, 0, 250 - joint_t),
                             (0, -90, 250 - joint_t), (-90, -90, joint_t)]
        elif joint_rand < .5:
            joint_pattern = [(-90, -90, joint_t), (-90, 0, 250 - joint_t),
                             (0, 90, 250 - joint_t), (90, 90, joint_t)]
        elif joint_rand < 2 / 3:
            joint_pattern = [(-90, -90, joint_t), (-90, 0, 250 - joint_t),
                             (0, -90, 250 - joint_t), (-90, -90, joint_t)]
        elif joint_rand < 5 / 6:
            joint_pattern = [(0, 0, joint_t), (0, 90, 250 - joint_t),
                             (90, 0, 250 - joint_t), (0, 0, joint_t)]
        else:
            joint_pattern = [(0, 0, joint_t), (0, -90, 250 - joint_t),
                             (-90, 0, 250 - joint_t), (0, 0, joint_t)]
        occluder = dict(shape="cube", color=colors.pop(), joint="revolute",
                        material=materials.pop(),
                        init_pos=init_pos, init_orn=init_orn,
                        scale=scale, joint_pattern=joint_pattern)
        occluders.append(occluder)
    elif occluder_rand < .9:
        # sliding occluder
        joint_rand = rand(0, 1)
        if joint_rand < .25:
            joint_pattern = [(rand(.6, 1.2), 0, 250), (0, rand(.6, 1.2), 250)]
        elif joint_rand < .5:
            joint_pattern = [(rand(.6, 1.2), 0, 250), (0, rand(-1.2, -.6), 250)]
        elif joint_rand < .75:
            joint_pattern = [(rand(-1.2, -.6), 0, 250), (0, rand(.6, 1.2), 250)]
        else:
            joint_pattern = [(rand(-1.2, -.6), 0, 250), (0, rand(-1.2, -.6), 250)]
        occluder = dict(shape="cube", color=colors.pop(), joint="prismatic",
                        material=materials.pop(),
                        init_pos=init_pos, init_orn=init_orn,
                        scale=scale, joint_pattern=joint_pattern)
        occluders.append(occluder)
    return occluders


def get_objects(colors, materials):
    objects = []
    n_objects = np.random.randint(2, 3)
    for obj_id in range(n_objects):
        side_rand = rand(0, 1)
        size = rand(.2, .4)
        while True:
            cat_id = np.random.randint(55)
            if cat_id % 5 != 0:
                break
        shape = random_shape_net(cat_id, True)
        pos_z = SHAPE_DIMENSIONS[shape][2] * size
        scale = repeat_scale(size)
        orn_z = rand(-180, 180)

        if side_rand < .4:
            init_pos = (rand(-2.5, .5), rand(-4, -2), pos_z)
            init_v = (rand(-.6, .6), rand(.5, 1.5), 0)
        elif side_rand < .8:
            init_pos = (rand(-2.5, .5), rand(2, 4), pos_z)
            init_v = (rand(-.6, .6), rand(-1.5, -.5), 0)
        else:
            init_pos = (rand(-1.5, 0), rand(-.8, .8), pos_z)
            init_v = (rand(-.6, .6), rand(-1.5, 1.5), 0)

        color = colors.pop()

        backward_rand = rand(0, 1)
        if backward_rand < .4:
            backward_time = np.random.randint(200, 300)
            material = materials.pop()
            mid_pos = get_prospective_location(init_pos, init_v, backward_time / 100)
            object_orginal = dict(shape=shape, color=color,
                                  material=material, init_pos=init_pos, init_orn=(0, 0, orn_z),
                                  scale=scale, init_v=init_v, disappear_time=backward_time)
            object_stop = dict(shape=shape, color=color,
                               material=material, init_pos=mid_pos, init_orn=(0, 0, orn_z),
                               scale=scale, init_v=[0, 0, 0], appear_time=backward_time,
                               disappear_time=backward_time + 50)
            object_backward = dict(shape=shape, color=color,
                                   material=material, init_pos=mid_pos, init_orn=(0, 0, orn_z),
                                   scale=scale, init_v=[-x for x in init_v], appear_time=backward_time + 50)
            for o in [object_orginal, object_stop, object_backward]:
                objects.append(o)
            continue
        object = dict(shape=shape, color=color,
                      material=materials.pop(), init_pos=init_pos, init_orn=(0, 0, orn_z),
                      scale=scale, init_v=init_v)
        objects.append(object)
    return objects


def generate_config(case_name, args):
    np.random.seed()
    random.seed()
    colors = random_distinct_colors(7)
    materials = ["rubber"] * 7
    objects = get_objects(colors, materials)
    occluders = get_occluders(colors, materials)
    if args.is_single_image:
        sim = dict(output_dir=os.path.join(TRAIN_SIM_OUTPUT_FOLDER, case_name), sim_time=0.01)
    else:
        sim = dict(output_dir=os.path.join(TRAIN_SIM_OUTPUT_FOLDER, case_name), sim_time=5.)
    rendering = dict(motion_file=os.path.join(TRAIN_SIM_OUTPUT_FOLDER, case_name, "motion.json"),
                     output_dir=os.path.join(TRAIN_RENDER_OUTPUT_FOLDER, case_name))
    video = dict(frame_dir=os.path.join(TRAIN_RENDER_OUTPUT_FOLDER, case_name),
                 output_dir=os.path.join(TRAIN_VIDEO_OUTPUT_FOLDER, case_name))
    scene = dict(case_name=case_name, objects=objects, occluders=occluders,
                 sim=sim, rendering=rendering, video=video)
    write_serialized(scene, os.path.join(TRAIN_CONFIG_FOLDER, case_name + ".yaml"))
    return scene


def main(case_id, args):
    while True:
        config = generate_config("train_{:05d}".format(case_id), args)
        valid = generate(EasyDict(config), args)
        if valid:
            break


if __name__ == '__main__':
    args = parse_args()
    catch_abort()
    worker_args = []
    if args.start_index is None:
        args.start_index = args.start + get_host_id() % args.stride
    for i in range(args.start_index, args.end, args.stride):
        worker_args.append((i, args))

    # with Pool(2) as p:
    #     p.starmap(main, worker_args)

    for worker_arg in worker_args:
        generate(*worker_arg)
