import math
import random

import bpy
import numpy as np


def rand_jitter(jitter):
    return 2.0 * jitter * (random.random() - 0.5)


def obj_centered_camera_pos(dist, theta_deg, phi_deg):
    phi = float(phi_deg) / 180 * math.pi
    theta = float(theta_deg) / 180 * math.pi
    x = dist * math.cos(phi) * math.cos(theta)
    y = dist * math.sin(phi) * math.cos(theta)
    z = dist * math.sin(theta)
    return x, y, z


def norm_2(v):
    return math.sqrt(v[0] * v[0] + v[1] * v[1] + v[2] * v[2])


def get_rotation(r):
    x = -1 * r
    z = np.array([r[1], -r[0], 0])
    y = np.array([-1 * r[0] * r[2], -1 * r[2] * r[1], r[0] * r[0] + r[1] * r[1]])
    x = x / norm_2(x)
    y = y / norm_2(y)
    z = z / norm_2(z)
    M = [x, y, z]
    R = [M[2], M[1], M[0] * -1]
    return R


def delete_object(obj):
    """ Delete a specified blender object """
    for o in bpy.data.objects:
        o.select = False
    obj.select = True
    bpy.ops.object.delete()


def set_mask(base_path):
    """Set the output of mask"""
    scene = bpy.context.scene
    nodes = scene.node_tree.nodes
    links = bpy.context.scene.node_tree.links

    map_value_node = bpy.context.scene.node_tree.nodes.new("CompositorNodeMapValue")
    map_value_node.size[0] = 1 / 255
    links.new(nodes["Render Layers"].outputs["IndexOB"], map_value_node.inputs[0])

    file_output_node = bpy.context.scene.node_tree.nodes.new('CompositorNodeOutputFile')
    file_output_node.base_path = base_path
    links.new(map_value_node.outputs[0], file_output_node.inputs[0])

    return file_output_node


def set_depth(base_path):
    """Set the output of depth"""
    scene = bpy.context.scene
    nodes = scene.node_tree.nodes
    links = bpy.context.scene.node_tree.links

    map_value_node = bpy.context.scene.node_tree.nodes.new("CompositorNodeMapValue")
    map_value_node.size[0] = 1 / 20
    links.new(nodes["Render Layers"].outputs["Depth"], map_value_node.inputs[0])

    file_output_node = bpy.context.scene.node_tree.nodes.new('CompositorNodeOutputFile')
    file_output_node.base_path = base_path
    # use uint 16 for higher accuracy
    file_output_node.format.color_depth = "16"
    links.new(map_value_node.outputs[0], file_output_node.inputs[0])

    return file_output_node


def set_flow(base_path):
    """Set the output of depth
    R current - next x
    G current - previous y
    B current - previous x
    A current - next y"""
    scene = bpy.context.scene
    nodes = scene.node_tree.nodes
    links = bpy.context.scene.node_tree.links

    separate_rgba_node = bpy.context.scene.node_tree.nodes.new("CompositorNodeSepRGBA")
    links.new(nodes["Render Layers"].outputs["Vector"], separate_rgba_node.inputs[0])
    file_output_nodes = {}

    for ch in "RGBA":
        map_value_node = bpy.context.scene.node_tree.nodes.new("CompositorNodeMapValue")
        map_value_node.offset[0] = .5 * 20
        map_value_node.size[0] = 1 / 20
        links.new(separate_rgba_node.outputs[ch], map_value_node.inputs[0])

        file_output_node = bpy.context.scene.node_tree.nodes.new('CompositorNodeOutputFile')
        file_output_node.base_path = base_path
        file_output_nodes[ch] = file_output_node
        # use uint 16 for higher accuracy
        file_output_node.format.color_depth = "16"
        links.new(map_value_node.outputs[0], file_output_node.inputs[0])

    return file_output_nodes
