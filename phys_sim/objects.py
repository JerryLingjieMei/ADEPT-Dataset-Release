import pybullet as p
import re
import os

from phys_sim.convert_pattern import *
from utils.constants import OCCLUDER_HALF_WIDTH
from utils.shape_net import SHAPE_DIMENSIONS


class ObjectManager(object):

    def __init__(self, config, obj_dir, num_steps):
        self.obj_dir = obj_dir
        self.config = config
        self.num_steps = num_steps

        self.plane_id, self.plane_visual_id = self.add_plane()
        self.object_ids = []
        self.desk_ids = []

        self.disappear_time = []
        self.appear_time = []
        self.init_positions = []
        for obj_params in self.config["objects"]:
            self.object_ids.append(self.add_object(**obj_params))

        self.num_link = 0
        self.joint_patterns = []
        self.occluder_info = self.add_occluders_start()
        if "occluders" in self.config:
            for occluder_params in self.config["occluders"]:
                self.add_occluder(**occluder_params)

        if "desks" in self.config:
            for desk_params in self.config["desks"]:
                self.add_desk(**desk_params)

        self.ground_id = self.add_occluders_end()

    def add_plane(self):
        """Add a plane"""
        plane_id = p.createCollisionShape(p.GEOM_MESH, fileName="plane.obj", meshScale=[100, 100, 100])
        plane_visual_id = p.createVisualShape(p.GEOM_MESH, fileName="plane.obj", rgbaColor=(1, 1, 1, 1))
        return plane_id, plane_visual_id

    def add_object(self, shape, mass=1, init_pos=(0, 0, 1), init_orn=(0, 0, 0), scale=(1, 1, 1), init_v=(0, 0, 0),
                   lat_fric=0.,
                   restitution=.9, lin_damp=0, angular_damp=0, disappear_time=100000, appear_time=0, **kwargs):
        """
        create an pybullet base object from a wavefront .obj file
        set up initial parameters and physical properties
        """
        scale = [x * y for x, y in zip(scale, SHAPE_DIMENSIONS[shape])]
        shape = "cube"
        obj_path = os.path.join(self.obj_dir, "shapes", '%s.obj' % shape)
        init_orn_quat = p.getQuaternionFromEuler(deg2rad(init_orn))
        col_id = p.createCollisionShape(p.GEOM_MESH, fileName=obj_path, meshScale=scale)
        obj_id = p.createMultiBody(mass, col_id, basePosition=init_pos, baseOrientation=init_orn_quat)
        p.resetBaseVelocity(obj_id, linearVelocity=init_v)
        p.changeDynamics(obj_id, -1, lateralFriction=lat_fric, restitution=restitution, linearDamping=lin_damp,
                         angularDamping=angular_damp)
        self.init_positions.append(init_pos)
        self.disappear_time.append(disappear_time)
        self.appear_time.append(appear_time)
        return obj_id

    def add_occluders_start(self):
        """Before adding occluders, to connect occluders with ground"""
        occluders_info = dict(baseCollisionShapeIndex=self.plane_id,
                              baseVisualShapeIndex=self.plane_visual_id,
                              basePosition=(0, 0, 0),
                              linkMasses=[],
                              linkCollisionShapeIndices=[],
                              linkVisualShapeIndices=[],
                              linkPositions=[], linkOrientations=[],
                              linkInertialFramePositions=[],
                              linkInertialFrameOrientations=[],
                              linkParentIndices=[],
                              linkJointTypes=[], linkJointAxis=[])
        return occluders_info

    def add_occluder(self, shape="cube", joint="revolute", mass=1, init_pos=(0, 0, 0), init_orn=(0, 0, 0),
                     scale=(.2, 4., 2.), joint_pattern=None, **kwargs):
        """Add an occluder with physical properties"""
        obj_path = os.path.join(self.obj_dir, "shapes", '%s.obj' % shape)
        init_orn_quat = p.getQuaternionFromEuler(deg2rad(init_orn))
        col_id = p.createCollisionShape(p.GEOM_MESH, fileName=obj_path, meshScale=scale,
                                        collisionFramePosition=(-scale[0], 0, scale[2]))
        self.occluder_info["linkMasses"].append(mass)
        self.occluder_info["linkCollisionShapeIndices"].append(col_id)
        self.occluder_info["linkVisualShapeIndices"].append(col_id)
        self.occluder_info["linkPositions"].append(init_pos)
        self.occluder_info["linkOrientations"].append(init_orn_quat)
        self.occluder_info["linkInertialFramePositions"].append((-scale[0], 0, scale[2]))
        self.occluder_info["linkInertialFrameOrientations"].append((0, 0, 0, 1))
        self.occluder_info["linkParentIndices"].append(0)
        self.occluder_info["linkJointAxis"].append((0, 1, 0))
        if joint == "revolute":
            self.occluder_info["linkJointTypes"].append(p.JOINT_REVOLUTE)
            if joint_pattern is None:
                self.joint_patterns.append(np.zeros(self.num_steps))
            else:
                self.joint_patterns.append(convert_rot_patterns(joint_pattern))
        elif joint == "prismatic":
            self.occluder_info["linkJointTypes"].append(p.JOINT_PRISMATIC)
            if joint_pattern is None:
                self.joint_patterns.append(np.zeros(self.num_steps))
            else:
                self.joint_patterns.append(convert_trans_patterns(joint_pattern))
        else:
            raise NotImplementedError("Joint type not supported")
        self.num_link += 1

    def add_occluders_end(self):
        """After adding occluders, to connect occluders with ground"""
        ground_id = p.createMultiBody(0., **self.occluder_info)
        return ground_id

    def add_desk(self, mass=100, init_pos=(0, 0, 0), init_orn=(0, 0, 0), scale=(1, 1, 1), **kwargs):
        """Add a desk, with scale[0], scale[1] being the half width of table,
        scale[2] being the half height of the cubic trunk"""
        if init_orn != [0, 0, 0]:
            print(init_orn)
            raise NotImplementedError("Only support horizontal desk")
        desk_id = []
        for i in (-1, 1):
            for j in (-1, 1):
                loc = (init_pos[0] + i * (scale[0] - scale[2]), init_pos[1] + j * (scale[1] - scale[2]),
                       init_pos[2] + scale[2])
                desk_id.append(self.add_object("cube", mass=mass, init_pos=loc, init_orn=(0, 0, 0), init_v=(0, 0, 0),
                                               scale=(scale[2], scale[2], scale[2])))
        desk_id.append(self.add_object("cube", mass=mass, init_pos=(

            init_pos[0], init_pos[1], init_pos[2] + scale[2] * 2 + OCCLUDER_HALF_WIDTH),
                                       init_orn=(90, 90, 0), init_v=(0, 0, 0),
                                       scale=(OCCLUDER_HALF_WIDTH, scale[0], scale[1])))
        self.desk_ids.append(desk_id)

    def set_object_motion(self, obj_id, time):
        """Object may appear or disappear"""
        loc, quat = p.getBasePositionAndOrientation(obj_id)
        v, omega = p.getBaseVelocity(obj_id)
        if time == 0 and self.appear_time[obj_id] != 0:
            new_loc = loc[0] + 20 * (1 + obj_id), loc[1], loc[2]
            p.resetBasePositionAndOrientation(obj_id, new_loc, quat)
            p.resetBaseVelocity(obj_id, v, omega)
        if time != 0 and self.appear_time[obj_id] == time:
            p.resetBasePositionAndOrientation(obj_id, self.init_positions[obj_id], quat)
            p.resetBaseVelocity(obj_id, v, omega)
        if self.disappear_time[obj_id] == time:
            new_loc = loc[0] + 20 * (1 + obj_id), loc[1], loc[2]
            p.resetBasePositionAndOrientation(obj_id, new_loc, quat)
            p.resetBaseVelocity(obj_id, v, omega)

    def get_object_motion(self, obj_id):
        """Return the location, orientation, velocity and angular velocity of an object"""
        loc, quat = p.getBasePositionAndOrientation(obj_id)
        orn = p.getEulerFromQuaternion(quat)
        v, omega = p.getBaseVelocity(obj_id)
        loc, orn, v, omega = list(loc), list(orn), list(v), list(omega)
        motion_dict = {
            'location': loc,
            'orientation': orn,
            'velocity': v,
            'angular_velocity': omega,
        }
        return motion_dict

    def set_occluder_motion(self, link_id, time):
        """Set the rotation of the occluder to a specific rotation"""
        p.resetJointState(self.ground_id, link_id, self.joint_patterns[link_id][time])

    def get_occluder_motion(self, link_id):
        """Return the location, orientation, velocity and angular velocity of an occluder"""
        loc, quat, _, _, _, _, v, omega = p.getLinkState(self.ground_id, link_id, computeLinkVelocity=True)
        orn = p.getEulerFromQuaternion(quat)
        loc, orn, v, omega = list(loc), list(orn), list(v), list(omega)
        if orn[1] < 0:
            loc[2] += 2 * np.sin(-orn[1]) * OCCLUDER_HALF_WIDTH
        motion_dict = {
            'location': loc,
            'orientation': orn,
            'velocity': v,
            'angular_velocity': omega
        }
        return motion_dict

    def get_desk_motion(self, desk_id):
        """Return the location, orientation, velocity and angular velocity of an table"""
        desk_motion = []
        for object_id in desk_id:
            desk_motion.append(self.get_object_motion(object_id))
        return desk_motion

    def has_collision(self):
        """Check if collision happens which involves objects"""
        for object_id in self.object_ids:
            if len(p.getContactPoints(object_id)) > 1:
                return True
            elif len(p.getContactPoints(object_id)) == 1:
                contact_point = p.getContactPoints(object_id)[0]
                contact_normal = contact_point[7]
                if abs(contact_normal[0]) > .1 or abs(contact_normal[1]) > .1:
                    return True
            loc, quat = p.getBasePositionAndOrientation(object_id)
            if -4 < loc[0] < -2.8:
                return True
        return False
