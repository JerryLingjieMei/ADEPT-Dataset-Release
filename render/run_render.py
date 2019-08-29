import argparse
import os
import json

from imageio import imread
from PIL import Image

from render.intro import render_intro
from render.render_utils import *
from render.objects import ObjectManager
from render.ground import add_ground
from render.camera import set_camera

from utils.io import mkdir, clr_dir, write_serialized
from utils.geometry import convert_euler, convert_inverse_euler


def main(config):
    # main script
    rendering = config.rendering
    mkdir(rendering.output_dir)
    mkdir(os.path.join(rendering.output_dir, 'imgs'))
    mkdir(os.path.join(rendering.output_dir, 'masks'))
    mkdir(os.path.join(rendering.output_dir, 'depths'))
    mkdir(os.path.join(rendering.output_dir, 'flows'))
    clr_dir(os.path.join(rendering.output_dir, 'imgs'))
    clr_dir(os.path.join(rendering.output_dir, 'masks'))
    clr_dir(os.path.join(rendering.output_dir, 'depths'))
    clr_dir(os.path.join(rendering.output_dir, 'flows'))

    add_ground(rendering)

    # set up render parameters
    render_args = bpy.context.scene.render
    render_args.engine = 'CYCLES'
    render_args.resolution_x = rendering.width
    render_args.resolution_y = rendering.height
    render_args.resolution_percentage = 100
    render_args.tile_x = rendering.render_tile_size
    render_args.tile_y = rendering.render_tile_size
    if rendering.use_gpu == 1:
        # blender changed the API for enabling CUDA at some point
        pref = bpy.context.user_preferences.addons["cycles"].preferences
        pref.compute_device_type = "CUDA"
        for device in pref.devices:
            device.use = True
        # bpy.context.user_preferences.system.compute_device_type = 'CUDA'
        # bpy.context.user_preferences.system.compute_device = 'CUDA_0'
        render_args.tile_x = rendering.render_tile_size_gpu
        render_args.tile_y = rendering.render_tile_size_gpu

    # some CYCLES-specific stuff
    bpy.data.worlds['World'].cycles.sample_as_light = True
    bpy.context.scene.cycles.blur_glossy = 2.0
    bpy.context.scene.cycles.samples = rendering.render_num_samples
    bpy.context.scene.cycles.transparent_min_bounces = rendering.render_min_bounces
    bpy.context.scene.cycles.transparent_max_bounces = rendering.render_max_bounces
    if rendering.use_gpu == 1:
        bpy.context.scene.cycles.device = 'GPU'

    bpy.context.scene.use_nodes = True
    bpy.context.scene.render.layers['RenderLayer'].use_pass_object_index = True

    # set up camera
    set_camera(rendering.camera_rho, rendering.camera_theta, rendering.camera_phi,
               look_at=rendering.camera_look_at)

    # apply jitter to lamp positions
    if rendering.key_light_jitter > 0:
        for i in range(3):
            bpy.data.objects['Lamp_Key'].location[i] += rand_jitter(rendering.key_light_jitter)
    if rendering.back_light_jitter > 0:
        for i in range(3):
            bpy.data.objects['Lamp_Back'].location[i] += rand_jitter(rendering.back_light_jitter)
    if rendering.fill_light_jitter > 0:
        for i in range(3):
            bpy.data.objects['Lamp_Fill'].location[i] += rand_jitter(rendering.fill_light_jitter)

    # set up objects
    om = ObjectManager(config, rendering.shape_dir, rendering.material_dir, rendering.back_wall)

    mask_node = set_mask(os.path.join(rendering.output_dir, "masks"))
    depth_node = set_depth(os.path.join(rendering.output_dir, "depths"))
    flow_node = set_flow(os.path.join(rendering.output_dir, "flows"))

    # load motion
    with open(rendering.motion_file, 'r') as f:
        input_file = json.load(f)
        time_step = float(input_file['timestep'])
        motion = input_file['motion']

    # render it
    render_every = int(1 / time_step / rendering.fps)
    if render_every == 0:
        render_every = 1

    camera = dict(camera_rho=rendering.camera_rho, camera_theta=rendering.camera_theta,
                  camera_phi=rendering.camera_phi, camera_look_at=rendering.camera_look_at)
    scene_anns = dict(case_name=config.case_name, camera=camera, scene=[])

    if rendering.intro_time > 0:
        render_intro(om, rendering, motion[0])

    for n, m in enumerate(motion):
        if n % render_every == 0:
            bpy.context.scene.frame_set(n)
            # objects are before occluders
            for i, obj_motion in enumerate(m["objects"] + m["occluders"]):
                loc = obj_motion['location']
                euler = convert_euler(obj_motion['orientation'])
                om.set_position(om.obj_names[i], loc, euler, key_frame=True)

            i = len(m["objects"]) + len(m["occluders"])

            for desk_motion in m["desks"]:
                for obj_motion in desk_motion:
                    loc = obj_motion['location']
                    euler = convert_euler(obj_motion['orientation'])
                    om.set_position(om.obj_names[i], loc, euler, key_frame=True)
                    i += 1

    for n, m in enumerate(motion):
        if "ABORT" in globals():
            if globals()["ABORT"]:
                print("Aborted")
                raise KeyboardInterrupt

        if n % render_every == 0:
            bpy.context.scene.frame_set(n)
            image_path = os.path.join(rendering.output_dir, 'imgs',
                                      '%s_%06.2fs.png' % (rendering.image_prefix, n * time_step))
            render_args.filepath = image_path
            mask_base_name = '####_%s_%06.2fs.png' % (rendering.image_prefix, n * time_step)
            mask_node.file_slots[0].path = mask_base_name
            depth_base_name = '####_%s_%06.2fs.png' % (rendering.image_prefix, n * time_step)
            depth_node.file_slots[0].path = depth_base_name
            for ch in "RGBA":
                flow_base_name = '%s_####_%s_%06.2fs.png' % (ch, rendering.image_prefix, n * time_step)
                flow_node[ch].file_slots[0].path = flow_base_name

            bpy.ops.render.render(write_still=True)

            frame_anns = dict(image_path=image_path, objects=[])
            mask_file_path = os.path.join(rendering.output_dir, "masks", "{:04d}".format(n) + mask_base_name[4:])
            for i, obj_motion in enumerate(m["objects"] + m["occluders"]):
                mask = imread(mask_file_path)[:, :, 0] == i + 1
                frame_anns["objects"].append(om.log(i, obj_motion, mask))

            scene_anns["scene"].append(frame_anns)

    bpy.ops.wm.save_as_mainfile(filepath=os.path.join(rendering.output_dir, "scene.blend"))
    write_serialized(scene_anns, os.path.join(rendering.output_dir,
                                              "{:s}_ann.yaml".format(rendering.image_prefix)))
