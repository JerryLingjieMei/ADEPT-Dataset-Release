import argparse
from multiprocessing import Pool, cpu_count, Manager
import os
from collections import defaultdict

import numpy as np
import bpy

from utils.io import write_serialized, read_serialized
from utils.misc import get_host_id
from utils.shape_net import SIM_SHAPE_NET_FOLDER, RENDER_SHAPE_NET_FOLDER, SHAPE_NET_CATEGORY, SHAPE_NET_NUMS, mkdir


def parse_args():
    parser = argparse.ArgumentParser(description='')
    parser.add_argument('--start_index', help='image index to start', type=int)
    parser.add_argument("--stride", help="image index stride", type=int, default=1)
    parser.add_argument("--reduce", help="reduce all results", type=int, default=0)
    return parser.parse_args()


def obj_to_blend(cat_name, shape_name, all_dimensions):
    name = cat_name + shape_name
    file_path = os.path.join(SIM_SHAPE_NET_FOLDER, cat_name, "{}.obj".format(shape_name))
    mkdir(os.path.join(RENDER_SHAPE_NET_FOLDER, cat_name))
    out_path = os.path.join(RENDER_SHAPE_NET_FOLDER, cat_name, "{}.blend".format(shape_name))
    bpy.ops.wm.read_homefile()
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete()

    bpy.ops.import_scene.obj(filepath=file_path, split_mode="OFF")
    bpy.context.view_layer.objects.active = bpy.context.scene.objects[0]

    object = bpy.context.selected_objects[0]

    object.name = name
    # setting the centre to the center of bounding box

    max_dimension = max(object.dimensions)
    scaling = 2. / max_dimension

    bpy.ops.object.origin_set(type='ORIGIN_GEOMETRY', center='BOUNDS')

    bpy.ops.object.mode_set(mode="EDIT")

    bpy.ops.transform.translate(value=[0, 0, 0])
    bpy.ops.transform.rotate(value=np.pi / 2, axis=(1, 0, 0))
    bpy.ops.transform.resize(value=[scaling, scaling, scaling])
    bpy.ops.mesh.normals_make_consistent(inside=False)
    bpy.ops.object.mode_set(mode="OBJECT")

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
    if args.start_index is None:
        args.start_index = get_host_id() % args.stride

    if args.reduce:
        all_dimensions = dict()
        for i in range(args.stride):
            all_dimensions.update(
                read_serialized(os.path.join(SIM_SHAPE_NET_FOLDER, "all_dimensions_{:02d}.json".format(i))))

        write_serialized(dict(all_dimensions),
                         os.path.join(SIM_SHAPE_NET_FOLDER, "all_dimensions.json"))

        to_rotate_index = defaultdict(int)
        for name, dimension in all_dimensions.items():
            # x > y bad
            if dimension[0] > dimension[1]:
                to_rotate_index[name[:4]] += 1
            else:
                to_rotate_index[name[:4]] -= 1
        write_serialized(dict(to_rotate_index),
                         os.path.join(SIM_SHAPE_NET_FOLDER, "categories_to_rotate.json"))

    else:
        manager = Manager()
        all_dimensions = manager.dict()
        worker_args = []

        for cat_id in SHAPE_NET_CATEGORY.keys():
            for shape_id in range(SHAPE_NET_NUMS[cat_id]):
                shape_id = "{:06d}".format(shape_id)
                worker_args.append((cat_id, shape_id, all_dimensions))
        worker_args = worker_args[args.start_index::args.stride]

        with Pool(cpu_count()) as p:
            p.starmap(obj_to_blend, worker_args)

        write_serialized(dict(all_dimensions),
                         os.path.join(SIM_SHAPE_NET_FOLDER, "all_dimensions_{:02d}.json".format(args.start_index)))
