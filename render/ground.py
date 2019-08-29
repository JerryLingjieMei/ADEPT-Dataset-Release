import bpy

import numpy as np

from utils.misc import rand


def add_ground(rendering):
    """Add a checkerboard background to the scene"""
    bpy.ops.wm.open_mainfile(filepath=rendering.base_scene_blendfile)

    # Select ground
    bpy.context.scene.objects.active = bpy.data.objects["Ground"]

    adjust_ground()

    # Create a new material; it is not attached to anything and
    # it will be called "Material"
    bpy.ops.material.new()

    # Get a reference to the material we just created and rename it;
    # then the next time we make a new material it will still be called
    # "Material" and we will still be able to look it up by name
    mat = bpy.data.materials['Material']
    mat.name = 'Material_ground'

    # Attach the new material to the active object
    # Make sure it doesn't already have materials
    obj = bpy.context.active_object
    assert len(obj.data.materials) == 0
    obj.data.materials.append(mat)

    # Assign the material to the new material slot (currently active)
    bpy.context.object.active_material = mat

    add_pattern(mat)


def add_pattern(mat):
    mat.use_nodes = True

    diffuse_bsdf = mat.node_tree.nodes.new("ShaderNodeBsdfDiffuse")
    checker = mat.node_tree.nodes.new("ShaderNodeTexChecker")
    checker.inputs["Color1"].default_value = (.95, .95, .95, .8)
    checker.inputs["Color2"].default_value = (.5, .5, .5, .8)
    checker.inputs["Scale"].default_value = 50
    mat.node_tree.links.new(checker.outputs["Color"], diffuse_bsdf.inputs["Color"])
    mat.node_tree.links.new(diffuse_bsdf.outputs["BSDF"], mat.node_tree.nodes['Material Output'].inputs['Surface'])


def adjust_ground():
    theta = rand(-np.pi / 3, np.pi / 3)
    depth = 15
    shift = rand(28, 32)
    bpy.context.scene.objects.active = bpy.data.objects["Ground"]
    bpy.context.object.rotation_mode = 'XYZ'
    bpy.context.object.rotation_euler = [0, 0, np.pi + theta]
    bpy.context.object.location = [-depth * np.cos(theta) + shift * np.sin(theta),
                                   -depth * np.sin(theta) - shift * np.cos(theta),
                                   0]
