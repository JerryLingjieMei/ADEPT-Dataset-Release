'''
run single simlation and save motion (and preview video)
'''

import time
import pybullet_data

import argparse
import json

import imageio
from easydict import EasyDict
import pybullet as p

import os
from phys_sim.camera import Camera
from phys_sim.objects import ObjectManager
from phys_sim.convert_pattern import *
from utils.io import read_serialized, write_serialized, clr_dir

parser = argparse.ArgumentParser()
parser.add_argument('--config_file', default='config/demo_config.json', type=str,
                    help='path to object configuration file')
parser.add_argument('--output_dir', default='phys_sim/output/demo', type=str,
                    help='output directory')
parser.add_argument('--obj_dir', default='phys_sim/data', type=str,
                    help='directory to object files')
parser.add_argument('--img_name_prefix', default='demo', type=str,
                    help='image filename prefix')
parser.add_argument('--sim_time', default=5.0, type=float,
                    help='total simulation time in seconds')
parser.add_argument('--timestep', default=0.01, type=float,
                    help='simulation time step')
parser.add_argument('--preview', default=0, type=int,
                    help='save rendered video from pybullet')
parser.add_argument('--preview_fps', default=25, type=int,
                    help='preview video frame per second')


def main(config):
    sim = config.sim
    if not os.path.exists(sim.output_dir):
        os.makedirs(sim.output_dir)
    if sim.preview and not os.path.exists(os.path.join(sim.output_dir, 'imgs')):
        os.makedirs(os.path.join(sim.output_dir, 'imgs'))
    if sim.preview:
        clr_dir(os.path.join(sim.output_dir, 'imgs'))

    physicsClient = p.connect(p.DIRECT)
    p.setAdditionalSearchPath(pybullet_data.getDataPath())
    p.setGravity(0, 0, -1)
    p.setTimeStep(sim.timestep)
    p.setPhysicsEngineParameter(contactBreakingThreshold=.0002)

    preview_every = int((1 / sim.preview_fps) // sim.timestep)
    num_steps = int(sim.sim_time / sim.timestep)

    # # add plane
    # plane_id = p.loadURDF("plane.urdf")
    # p.changeDynamics(plane_id, -1, restitution=0)

    # set up objects
    om = ObjectManager(config, sim.obj_dir, num_steps)

    # set up camera
    if sim.preview:
        cam_params = {
            'target_pos': [-1.5, 0, 0],
            'pitch': -20.0,
            'yaw': 90,
            'roll': 0,
            'cam_dist': 7.2,
            'width': 480,
            'height': 320,
            'up_axis': 2,
            'near_plane': 0.01,
            'far_plane': 100,
            'fov': 32
        }
        camera = Camera(**cam_params)
    else:
        camera = None

    # run simulation

    motion = []
    valid = True
    if sim.step_pattern is None:
        step_pattern = np.ones(num_steps)
    else:
        step_pattern = convert_step_patterns(sim.step_pattern)

    for i in range(num_steps):
        if om.has_collision():
            valid = False
        for obj_id in om.object_ids:
            om.set_object_motion(obj_id, i)
        for link_id in range(om.num_link):
            om.set_occluder_motion(link_id, i)

        object_motions = []
        occluder_motions = []
        desk_motions = []
        if om.has_collision():
            valid = False
        for obj_id in om.object_ids:
            object_motions.append(om.get_object_motion(obj_id))
        for link_id in range(om.num_link):
            occluder_motions.append(om.get_occluder_motion(link_id))
        for desk_id in om.desk_ids:
            desk_motions.append(om.get_desk_motion(desk_id))
        if i % preview_every == 0 and sim.preview:
            img = camera.take_pic()
            save_path = os.path.join(sim.output_dir, 'imgs',
                                     '%s_%06.2fs.png' % (sim.img_name_prefix, i * sim.timestep))
            print('| saving to %s' % save_path)
            imageio.imsave(save_path, img)
        motion.append(dict(objects=object_motions, occluders=occluder_motions, desks=desk_motions))
        if om.has_collision():
            valid = False
        if step_pattern[i]:
            p.stepSimulation()

    save_path = os.path.join(sim.output_dir, "motion.json")
    output_file = {
        'timestep': sim.timestep,
        'motion': motion
    }
    print('| saving motion file to %s' % save_path)
    write_serialized(output_file, save_path)

    p.disconnect()
    print('| finish')
    if not valid:
        print("Collision detected!")
    return valid


if __name__ == '__main__':
    args = parser.parse_args()
    config = read_serialized(args.config_file)
    config.sim = EasyDict(vars(args))
    main(config)
