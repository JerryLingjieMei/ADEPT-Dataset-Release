import re
from copy import copy
import os

import bpy
import pycocotools.mask as mask_util
import numpy as np

from utils.geometry import convert_euler, deg2rad
from utils.constants import COLORS, TYPES, OCCLUDER_HALF_WIDTH
from utils.shape_net import SHAPE_DIMENSIONS, get_shape_blend


class ObjectManager(object):

    def __init__(self, config, shape_dir, material_dir, back_wall):
        self.shape_dir = shape_dir
        self.material_dir = material_dir
        self.obj_names = []
        self.mask_nodes = []
        self.shapes = []
        self.scales = []
        self.colors = []
        self.load_materials()

        self.color_name_to_rgba = {}
        for name, rgb in COLORS.items():
            rgba = [float(c) / 255.0 for c in rgb] + [1.0]
            self.color_name_to_rgba[name] = rgba

        self.config = config
        for obj_params in self.config["objects"]:
            shape = obj_params['shape']
            scale, loc = obj_params['scale'], obj_params['init_pos']
            euler = convert_euler(deg2rad(obj_params['init_orn']))
            color = obj_params['color']
            name = self.add_object(shape, scale, loc, euler, color)
            material = obj_params['material']
            split = obj_params['split'] if "split" in obj_params else (0, 0, 0)
            self.add_material(name, material, color, split)

        if "occluders" in self.config:
            for obj_params in self.config["occluders"]:
                shape = obj_params['shape']
                scale, loc = obj_params['scale'], obj_params['init_pos']
                euler = convert_euler(deg2rad(obj_params['init_orn']))
                color = obj_params['color']
                name = self.add_object(shape, scale, loc, euler, color)
                material = obj_params['material']
                self.add_material(name, material, color)

        if "desks" in self.config:
            for obj_params in self.config["desks"]:
                scale, loc = obj_params['scale'], obj_params['init_pos']
                euler = convert_euler(deg2rad(obj_params['init_orn']))
                color = obj_params['color']
                names = self.add_desk(scale, loc, euler, color)
                material = obj_params['material']
                for name in names:
                    self.add_material(name, material, color)

        if back_wall:
            desk_name = self.add_back_wall("wall_color")
            material = "rubber"
            color = "wall"
            self.add_material(desk_name, material, color)

    def add_object(self, shape, scale, loc, euler, color, counted=True):
        # First figure out how many of this object are already in the scene so we can
        # give the new object a unique name

        count = 0
        if counted:
            for obj in bpy.data.objects:
                if obj.name.startswith(shape):
                    count += 1
        if re.match("^\d\d\d\d\d\d\d\d\d\d$", shape):
            filename = get_shape_blend(shape)
        else:
            filename = os.path.join(self.shape_dir, '%s.blend' % shape, 'Object', shape)
        bpy.ops.wm.append(filename=filename)

        # Give it a new name to avoid conflicts
        if counted:
            new_name = '%s_%d' % (shape, count)
        else:
            new_name = 'back_wall'
        bpy.data.objects[shape].name = new_name

        # Set the new object as active, then rotate, scale, and translate it
        bpy.context.view_layer.objects.active = bpy.data.objects[new_name]
        bpy.ops.transform.resize(value=scale)
        self.set_position(new_name, loc, euler)

        if counted:
            self.obj_names.append(new_name)
            bpy.context.object.pass_index = len(self.obj_names)
            self.shapes.append(shape)
            self.scales.append(scale)
            self.colors.append(color)
        return new_name

    def add_back_wall(self, color):
        return self.add_object("cube", [OCCLUDER_HALF_WIDTH, 4, 6], [-4, 0, 0], [np.pi / 2, 0, 0],
                               color, counted=False)

    def add_desk(self, scale, loc, euler, color):
        names = []
        for i in (-1, 1):
            for j in (-1, 1):
                new_loc = (loc[0] + i * (scale[0] - scale[2]), loc[1] + j * (scale[1] - scale[2]),
                           loc[2] + scale[2])
                names.append(self.add_object("cube", (scale[2], scale[2], scale[2]), new_loc,
                                             convert_euler(euler), color))
        names.append(self.add_object("cube", (.04, scale[0], scale[1]), (
            loc[0], loc[1], loc[2] + scale[2] * 2 + OCCLUDER_HALF_WIDTH), convert_euler(euler), color))
        return names

    def set_position(self, name, loc, euler, key_frame=False):
        bpy.context.view_layer.objects.active = bpy.data.objects[name]
        bpy.context.object.rotation_mode = 'XYZ'
        bpy.context.object.rotation_euler = euler
        bpy.context.object.location = loc
        if key_frame:
            bpy.context.object.keyframe_insert('location', group="LocRot")
            bpy.context.object.keyframe_insert("rotation_euler", group="LocRot")

    def load_materials(self):
        """
        Load materials from a directory. We assume that the directory contains .blend
        files with one material each. The file X.blend has a single NodeTree item named
        X; this NodeTree item must have a "Color" input that accepts an RGBA value.
        """
        for fn in os.listdir(self.material_dir):
            if not fn.endswith('.blend'):
                continue
            name = os.path.splitext(fn)[0]
            file_name = os.path.join(self.material_dir, fn, 'NodeTree', name)
            bpy.ops.wm.append(filename=file_name)
            if name == "rubber":
                file_name = os.path.join(self.material_dir, fn, 'NodeTree', "rubber_combine")
                bpy.ops.wm.append(filename=file_name)

    def add_material(self, obj_name, name, color, split=(0, 0, 0)):
        """
        Create a new material and assign it to the active object. "name" should be the
        name of a material that has been previously loaded using load_materials.
        """
        bpy.context.view_layer.objects.active = bpy.data.objects[obj_name]

        # Figure out how many materials are already in the scene
        mat_count = len(bpy.data.materials)

        # Create a new material; it is not attached to anything and
        # it will be called "Material"
        bpy.ops.material.new()

        # Get a reference to the material we just created and rename it;
        # then the next time we make a new material it will still be called
        # "Material" and we will still be able to look it up by name
        mat = bpy.data.materials['Material']
        mat.name = 'Material_%d' % mat_count

        # Attach the new material to the active object
        # Make sure it doesn't already have materials
        obj = bpy.context.active_object
        assert len(obj.data.materials) == 0
        obj.data.materials.append(mat)

        # Find the output node of the new material
        output_node = None
        for n in mat.node_tree.nodes:
            if n.name == 'Material Output':
                output_node = n
                break

        # Add a new GroupNode to the node tree of the active material,
        # and copy the node tree from the preloaded node group to the
        # new group node. This copying seems to happen by-value, so
        # we can create multiple materials of the same type without them
        # clobbering each other
        group_node = mat.node_tree.nodes.new('ShaderNodeGroup')

        # Find and set the "Color" input of the new group node
        if color == "wall" or "-" not in color:
            group_node.node_tree = bpy.data.node_groups[name]
            group_node.inputs["Color"].default_value = self.color_name_to_rgba[color] \
                if color != "wall" else (.85, .85, .85, .8)
        else:
            color_0, color_1 = color.split("-")
            name = "{}_{}".format(name, "combine")
            group_node.node_tree = bpy.data.node_groups[name]
            group_node.inputs["Color_0"].default_value = self.color_name_to_rgba[color_0]
            group_node.inputs["Color_1"].default_value = self.color_name_to_rgba[color_1]
            group_node.inputs["Split"].default_value = split

        # Wire the output of the new group node to the input of
        # the MaterialOutput node
        mat.node_tree.links.new(
            group_node.outputs['Shader'],
            output_node.inputs['Surface'],
        )

    def log(self, id, motion, mask):
        """log the motion of object id into log"""
        bpy.context.view_layer.objects.active = bpy.data.objects[self.obj_names[id]]
        obj_mask = np.asarray(mask, dtype=np.uint8, order="F")
        mask_code = mask_util.encode(obj_mask)
        mask_code["counts"] = mask_code["counts"].decode("ASCII")
        scale = [x * y for x, y in zip(self.scales[id], SHAPE_DIMENSIONS[self.shapes[id]])]
        shape = "Occluder" if self.scales[id][0] == OCCLUDER_HALF_WIDTH else TYPES[self.shapes[id]]
        return dict(mask=mask_code, name=self.obj_names[id], type=shape, scale=scale,
                    location=motion["location"], rotation=convert_euler(motion["orientation"]),
                    velocity=motion["velocity"], angular_velocity=convert_euler(motion["angular_velocity"]),
                    color=self.colors[id])
