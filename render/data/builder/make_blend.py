import argparse
import os
import bpy

import numpy as np

from utils.shape_net import SIM_SHAPE_FOLDER, RENDER_SHAPE_FOLDER
from utils.io import read_serialized, write_serialized


def parse_args():
    parser = argparse.ArgumentParser(description='')
    parser.add_argument('--obj_name', help='obj_names to convert', type=str, nargs="+")
    return parser.parse_args()


def obj_to_blend(name, all_dimensions):
    file_path = os.path.join(SIM_SHAPE_FOLDER, "{}.obj".format(name))
    out_path = os.path.join(RENDER_SHAPE_FOLDER, "{}.blend".format(name))
    bpy.ops.wm.read_homefile()
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete()

    bpy.ops.import_scene.obj(filepath=file_path, split_mode="OFF")
    bpy.context.scene.objects.active = bpy.context.scene.objects[0]

    object = bpy.context.selected_objects[0]

    object.name = name
    # setting the centre to the center of bounding box

    max_dimension = max(object.dimensions)
    scaling = 2. / max_dimension

    bpy.ops.object.origin_set(type='ORIGIN_GEOMETRY', center='BOUNDS')
    object.data.show_double_sided = True

    bpy.ops.object.mode_set(mode="EDIT")

    bpy.ops.transform.translate(value=[0, 0, 0])
    bpy.ops.transform.rotate(value=0, axis=(1, 0, 0))
    bpy.ops.transform.resize(value=[scaling, scaling, scaling])
    bpy.ops.mesh.normals_make_consistent(inside=False)

    bpy.ops.object.mode_set(mode="OBJECT")
    bpy.ops.transform.rotate(value=-np.pi / 2, axis=(1, 0, 0))

    all_dimensions[name] = list(x / 2 for x in object.dimensions)

    # remove all materials
    for material in bpy.data.materials:
        material.user_clear()
        bpy.data.materials.remove(material)

    for ob in bpy.context.selected_editable_objects:
        ob.active_material_index = 0
        for i in range(len(ob.material_slots)):
            bpy.ops.object.material_slot_remove({'object': ob})

    bpy.ops.wm.save_as_mainfile(filepath=out_path)
    print("{} generated".format(name))


if __name__ == '__main__':
    args = parse_args()
    if os.path.exists(os.path.join(SIM_SHAPE_FOLDER, "all_dimensions.json")):
        all_dimensions = read_serialized(os.path.join(SIM_SHAPE_FOLDER, "all_dimensions.json"))
    else:
        all_dimensions = dict()
    for name in args.obj_name:
        while True:
            try:
                obj_to_blend(name, all_dimensions)
            except:
                continue
            else:
                break

    write_serialized(all_dimensions, os.path.join(SIM_SHAPE_FOLDER, "all_dimensions.json"))
