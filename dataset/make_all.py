import os

import dataset.make_video as make_video
import phys_sim.run_sim as run_sim
import render.run_render as run_render
from utils.constants import CONTENT_FOLDER


def update_sim(config, args):
    sim = config.sim
    if "output_dir" not in sim:
        raise KeyError("output_dir not specified")
    sim.obj_dir = os.path.join(CONTENT_FOLDER, "phys_sim/data")
    sim.img_name_prefix = config.case_name
    if "sim_time" not in sim:
        raise KeyError("sim_time not specified")
    sim.timestep = .01
    if "step_pattern" not in sim:
        sim.step_pattern = None
    sim.preview = args.preview
    sim.preview_fps = 25


def update_render(config):
    rendering = config.rendering
    if "motion_file" not in rendering:
        raise KeyError("motion_file not specified")
    if "output_dir" not in rendering:
        raise KeyError("output_dir not specified")
    rendering.image_prefix = config.case_name
    rendering.data_dir = 'render/data'
    rendering.base_scene_blendfile = 'render/data/base_scene.blend'
    rendering.material_dir = 'render/data/materials'
    rendering.shape_dir = 'render/data/shapes'
    # scene settings
    rendering.width = 480
    rendering.height = 320
    if "camera_rho" not in rendering:
        rendering.camera_rho = 7.2
    if "camera_theta" not in rendering:
        rendering.camera_theta = 20
    rendering.camera_phi = 0
    if "camera_look_at" not in rendering:
        rendering.camera_look_at = (-1.5, 0, 0)
    if "back_wall" not in rendering:
        rendering.back_wall = 1
    rendering.key_light_jitter = 1
    rendering.back_light_jitter = 1
    rendering.fill_light_jitter = 1
    # video settings
    rendering.fps = 25
    # render settings
    rendering.use_gpu = False
    rendering.render_num_samples = 128
    rendering.render_min_bounces = 4
    rendering.render_max_bounces = 8
    rendering.render_tile_size = 16
    rendering.render_tile_size_gpu = 160
    if "intro_time" not in rendering:
        rendering.intro_time = 0.


def update_video(config):
    video = config.video
    if "frame_dir" not in video:
        raise KeyError("frame_dir not specified")
    if "output_dir" not in video:
        video.output_dir = video.frame_dir
    video.fps = 25
    video.n_videos = 100
    video.starting_idx = 0
    if "save_gif" not in video:
        video.save_gif = 0
    if "save_ogv" not in video:
        video.save_ogv = 0


def generate(config, args):
    """Generate video from config"""
    update_sim(config, args)
    update_render(config)
    update_video(config)
    valid = run_sim.main(config)
    if not valid and args.requires_valid:
        return False
    run_render.main(config)
    make_video.make_mp4(config)
    return True


def only_make_video(config, args):
    """Generate video from config"""
    update_video(config)
    make_video.make_mp4(config)


def only_make_sim(config, args):
    """Generate video from config"""
    update_sim(config, args)
    valid = run_sim.main(config)
    if not valid and args.requires_valid:
        return False
    return True
