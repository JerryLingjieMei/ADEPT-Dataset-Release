import bpy
import os

import numpy as np
from PIL import Image
from imageio import imread

from render.camera import set_camera
from utils.geometry import convert_euler


def get_intro_camera(rendering, n):
    nn = int(n / 8)
    phi_s = np.concatenate([
        np.linspace(rendering.camera_phi, rendering.camera_phi + 10, nn),
        np.linspace(rendering.camera_phi + 10, rendering.camera_phi, nn),
        np.linspace(rendering.camera_phi, rendering.camera_phi - 10, nn),
        np.linspace(rendering.camera_phi - 10, rendering.camera_phi, nn),
        np.linspace(rendering.camera_phi, rendering.camera_phi, nn * 4)
    ])
    theta_s = np.concatenate([
        np.linspace(rendering.camera_theta, rendering.camera_theta, nn * 4),
        np.linspace(rendering.camera_theta, rendering.camera_theta - 10, nn),
        np.linspace(rendering.camera_theta - 10, rendering.camera_theta, nn),
        np.linspace(rendering.camera_theta, rendering.camera_theta + 10, nn),
        np.linspace(rendering.camera_theta + 10, rendering.camera_theta, nn)
    ])
    return phi_s, theta_s


def render_intro(om, rendering, m):
    render_args = bpy.context.scene.render
    time_step = 1 / rendering.fps
    phi_s, theta_s = get_intro_camera(rendering, int(rendering.intro_time * rendering.fps))
    for n in range(int(rendering.intro_time * rendering.fps)):
        if "ABORT" in globals():
            if globals()["ABORT"]:
                print("Aborted")
                raise KeyboardInterrupt

        set_camera(rendering.camera_rho, theta_s[n], phi_s[n], look_at=rendering.camera_look_at)

        # objects are before occluders
        for i, obj_motion in enumerate(m["objects"] + m["occluders"]):
            loc = obj_motion['location']
            euler = convert_euler(obj_motion['orientation'])
            om.set_position(om.obj_names[i], loc, euler)

        i = len(m["objects"]) + len(m["occluders"])

        for desk_motion in m["desks"]:
            for obj_motion in desk_motion:
                loc = obj_motion['location']
                euler = convert_euler(obj_motion['orientation'])
                om.set_position(om.obj_names[i], loc, euler)
                i += 1

        image_path = os.path.join(rendering.output_dir, 'imgs',
                                  '%s_-%05.2fs.png' % (rendering.image_prefix, n * time_step))
        render_args.filepath = image_path

        bpy.ops.render.render(write_still=True)

    set_camera(rendering.camera_rho, rendering.camera_theta, rendering.camera_phi,
               look_at=rendering.camera_look_at)
