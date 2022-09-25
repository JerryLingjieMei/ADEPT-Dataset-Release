import bpy

import numpy as np
import mathutils
from render.render_utils import obj_centered_camera_pos, get_rotation, rand_jitter, delete_object


def set_camera(rho, theta, phi=0, look_at=(0, 0, 0), jitter=0):
    camera = bpy.data.objects['Camera']

    # compute spatial parameters
    cx, cy, cz = obj_centered_camera_pos(rho, theta, phi)
    R = get_rotation(np.array([-cx, -cy, cz]))
    rot = mathutils.Matrix(R)
    rot.transpose()
    rot_euler = rot.to_euler()

    # set up spatial parameters
    camera.location[0] = cx + look_at[0]
    camera.location[1] = cy + look_at[1]
    camera.location[2] = cz + look_at[2]
    camera.rotation_mode = 'XYZ'
    camera.rotation_euler = rot_euler
    if jitter > 0:
        for i in range(3):
            camera.location[i] += rand_jitter(jitter)

    origin = bpy.data.objects["Empty"]
    origin.location = look_at

    # get directions
    directions = {}
    bpy.ops.mesh.primitive_plane_add(size=10)  # plane added for computing cardinal directions
    plane = bpy.context.object

    plane_normal = plane.data.vertices[0].normal
    cam_behind = camera.matrix_world.to_quaternion() @ mathutils.Vector((0, 0, -1))
    cam_left = camera.matrix_world.to_quaternion() @ mathutils.Vector((-1, 0, 0))
    cam_up = camera.matrix_world.to_quaternion() @ mathutils.Vector((0, 1, 0))
    plane_behind = (cam_behind - cam_behind.project(plane_normal)).normalized()
    plane_left = (cam_left - cam_left.project(plane_normal)).normalized()
    plane_up = cam_up.project(plane_normal).normalized()

    delete_object(plane)  # remove plane

    directions['behind'] = tuple(plane_behind)
    directions['front'] = tuple(-plane_behind)
    directions['left'] = tuple(plane_left)
    directions['right'] = tuple(-plane_left)
    directions['above'] = tuple(plane_up)
    directions['below'] = tuple(-plane_up)
    return directions
