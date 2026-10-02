"""Synthetic tracking controls and atomic, local developer-process transport."""
from __future__ import annotations

from dataclasses import replace
import json
import math
from pathlib import Path
import time

from .tracking import Landmark, Observation, observation_from_dict, observation_to_dict
from ._face_fixture import FACE_VERTICES

BODY_NAMES = (
    'nose left_eye_inner left_eye left_eye_outer right_eye_inner right_eye '
    'right_eye_outer left_ear right_ear mouth_left mouth_right left_shoulder '
    'right_shoulder left_elbow right_elbow left_wrist right_wrist left_pinky '
    'right_pinky left_index right_index left_thumb right_thumb left_hip right_hip '
    'left_knee right_knee left_ankle right_ankle left_heel right_heel left_toe right_toe'
).split()
HAND_NAMES = ['wrist'] + [f'{finger}_{joint}' for finger in ('thumb', 'index', 'middle', 'ring', 'pinky') for joint in ('base', 'proximal', 'distal', 'tip')]
EXPRESSIONS = ['browDownLeft', 'browDownRight', 'browInnerUp', 'browOuterUpLeft', 'browOuterUpRight', 'cheekPuff', 'cheekSquintLeft', 'cheekSquintRight', 'eyeBlinkLeft', 'eyeBlinkRight', 'eyeLookDownLeft', 'eyeLookDownRight', 'eyeLookInLeft', 'eyeLookInRight', 'eyeLookOutLeft', 'eyeLookOutRight', 'eyeLookUpLeft', 'eyeLookUpRight', 'eyeSquintLeft', 'eyeSquintRight', 'eyeWideLeft', 'eyeWideRight', 'jawForward', 'jawLeft', 'jawOpen', 'jawRight', 'mouthClose', 'mouthDimpleLeft', 'mouthDimpleRight', 'mouthFrownLeft', 'mouthFrownRight', 'mouthFunnel', 'mouthLeft', 'mouthLowerDownLeft', 'mouthLowerDownRight', 'mouthPressLeft', 'mouthPressRight', 'mouthPucker', 'mouthRight', 'mouthRollLower', 'mouthRollUpper', 'mouthShrugLower', 'mouthShrugUpper', 'mouthSmileLeft', 'mouthSmileRight', 'mouthStretchLeft', 'mouthStretchRight', 'mouthUpperUpLeft', 'mouthUpperUpRight', 'noseSneerLeft', 'noseSneerRight', 'tongueOut']
BODY_EDGES = [(11,12),(11,13),(13,15),(12,14),(14,16),(11,23),(12,24),(23,24),(23,25),(25,27),(24,26),(26,28),(27,29),(29,31),(28,30),(30,32)]
HAND_EDGES = [(0, 1 + finger * 4) for finger in range(5)] + [(i, i+1) for start in (1,5,9,13,17) for i in range(start,start+3)]


def _body(pose):
    xy = [(0.5,.15),(.48,.13),(.46,.13),(.44,.13),(.52,.13),(.54,.13),(.56,.13),(.41,.16),(.59,.16),(.47,.19),(.53,.19),(.38,.3),(.62,.3),(.29,.45),(.71,.45),(.22,.6),(.78,.6),(.2,.62),(.8,.62),(.21,.64),(.79,.64),(.24,.61),(.76,.61),(.43,.55),(.57,.55),(.42,.73),(.58,.73),(.41,.89),(.59,.89),(.4,.92),(.6,.92),(.36,.94),(.64,.94)]
    if pose == 'arms_up':
        for i, point in {13:(.29,.2),14:(.71,.2),15:(.25,.07),16:(.75,.07)}.items():
            xy[i] = point
        for i in range(17,23):
            xy[i] = (xy[15 if i % 2 else 16][0], .05)
    elif pose == 'squat':
        xy = [(x, y+.18 if i < 25 else y) for i,(x,y) in enumerate(xy)]
        xy[25], xy[26] = (.3,.76), (.7,.76)
    return [Landmark(x,y,0.,1.) for x,y in xy]


def _hand(side, pose):
    center = .32 if side == 'left' else .68
    sign = 1 if side == 'left' else -1
    points = [Landmark(center,.72,0.)]
    for finger in range(5):
        for joint in range(4):
            x = center + sign * ((finger-2)*.045)
            y = .62 - joint * (.055 if finger != 0 else .035)
            z = 0.
            if pose == 'fist':
                y = .61 + joint*.017
                z = -.02*math.sin(joint)
            points.append(Landmark(x,y,z))
    if pose == 'pinch':
        points[4] = Landmark(center-sign*.04,.48,-.02)
        points[8] = Landmark(center-sign*.04,.48,-.02)
    return points


def _face():
    points = [Landmark(.5+x/40, .48-y/40, -z/40) for x,y,z in FACE_VERTICES]
    # Authored iris centers/rings extend the canonical 468 vertices in Tasks order.
    for outer, inner, upper, lower in ((33,133,159,145),(362,263,386,374)):
        cx = (points[outer].x+points[inner].x)/2
        cy = (points[upper].y+points[lower].y)/2
        cz = (points[outer].z+points[inner].z)/2
        radius = abs(points[outer].x-points[inner].x)*.18
        points.extend(Landmark(cx+dx,cy+dy,cz) for dx,dy in
                      ((0,0),(radius,0),(0,-radius),(-radius,0),(0,radius)))
    return points


class SimulatorProvider:
    """Editable authored observations; stale mode freezes time, not landmarks.

    Synthetic world coordinates use fixed meter scales (body 2, hands .5 per
    image unit), centered on the hip midpoint or hand centroid. Translation
    preserves them; rotation rotates them. They are not estimated measurements.
    Face world coordinates are unsupported. Canonical face coordinates and
    authored iris/expression geometry are development fixtures, not physiology.
    """
    def __init__(self, profile):
        if profile not in ('body','hands','face'):
            raise ValueError(f'Unknown tracking profile: {profile}')
        self.profile = profile
        self.stale = False
        self.hidden = set()
        groups = {'body': _body('standing')} if profile == 'body' else ({side:_hand(side,'open') for side in ('left','right')} if profile == 'hands' else {'face':_face()})
        self.observation = Observation(
            profile=profile, timestamp=time.monotonic(), landmarks=groups,
            handedness={side: {'label':side, 'score':None} for side in groups} if profile == 'hands' else {},
            confidence_source='authored')
        self._sync_world()

    def _sync_world(self):
        world = {}
        for key, points in self.observation.landmarks.items():
            if key == 'face':
                continue
            origin = [points[23],points[24]] if key == 'body' else points
            center = [sum(getattr(p,axis) or 0. for p in origin)/len(origin) for axis in ('x','y','z')]
            # Fixed authored scales in meters, independent of image translation.
            scale = 2. if key == 'body' else .5
            world[key] = [Landmark((p.x-center[0])*scale,(p.y-center[1])*scale,
                                   ((p.z or 0.)-center[2])*scale,p.visibility) for p in points]
        self.observation = replace(self.observation, world_landmarks=world)

    def read(self):
        if not self.stale:
            self.observation = replace(self.observation, timestamp=time.monotonic())
        observation = replace(
            self.observation,
            landmarks={key:points for key,points in self.observation.landmarks.items() if key not in self.hidden},
            world_landmarks={key:points for key,points in self.observation.world_landmarks.items() if key not in self.hidden},
            handedness={key:value for key,value in self.observation.handedness.items() if key not in self.hidden})
        return observation_from_dict(observation_to_dict(observation))

    def set_joint(self, group, index, x, y, z, visibility=None):
        self.observation.landmarks[group][index] = Landmark(x,y,z,visibility)
        self._sync_world()

    def move(self, group, dx=0., dy=0., dz=0.):
        self.observation.landmarks[group] = [Landmark(p.x+dx,p.y+dy,(p.z or 0.)+dz,p.visibility) for p in self.observation.landmarks[group]]
        if group == 'face' and self.observation.transformation_matrix is not None:
            matrix = [row[:] for row in self.observation.transformation_matrix]
            for row, delta in zip(matrix, (dx,dy,dz)):
                row[3] += delta
            self.observation = replace(self.observation, transformation_matrix=matrix)
        self._sync_world()

    def rotate(self, group, pitch=0., yaw=0., roll=0.):
        points = self.observation.landmarks[group]
        cx,cy,cz = (sum(getattr(p,axis) or 0. for p in points)/len(points) for axis in ('x','y','z'))
        a,b,c = (math.radians(value) for value in (pitch,yaw,roll))
        ca,sa,cb,sb,cc,sc = math.cos(a),math.sin(a),math.cos(b),math.sin(b),math.cos(c),math.sin(c)
        matrix = [[cc*cb,cc*sb*sa-sc*ca,cc*sb*ca+sc*sa],[sc*cb,sc*sb*sa+cc*ca,sc*sb*ca-cc*sa],[-sb,cb*sa,cb*ca]]
        rotated = []
        for p in points:
            vec = (p.x-cx,p.y-cy,(p.z or 0.)-cz)
            xyz = [sum(row[j]*vec[j] for j in range(3))+center for row,center in zip(matrix,(cx,cy,cz))]
            rotated.append(Landmark(*xyz,p.visibility))
        self.observation.landmarks[group] = rotated
        if group == 'face':
            old = self.observation.transformation_matrix or [[1.,0.,0.,0.],[0.,1.,0.,0.],[0.,0.,1.,0.],[0.,0.,0.,1.]]
            composed = [[sum(matrix[i][k]*old[k][j] for k in range(3)) for j in range(3)]+[center] for i,center in enumerate((cx,cy,cz))]
            self.observation = replace(self.observation, transformation_matrix=composed+[[0.,0.,0.,1.]])
        self._sync_world()

    def preset(self, group, name):
        self.observation.landmarks[group] = _body(name) if group == 'body' else (_face() if group == 'face' else _hand(group,name))
        if group == 'face':
            expressions = dict.fromkeys(EXPRESSIONS,0.)
            for expression in {'smile':['mouthSmileLeft','mouthSmileRight'], 'surprise':['jawOpen','eyeWideLeft','eyeWideRight','browInnerUp'], 'blink':['eyeBlinkLeft','eyeBlinkRight']}.get(name,[]):
                expressions[expression] = 1.
            if name == 'smile':
                for index in (61,291,78,308):
                    point = self.observation.landmarks[group][index]
                    point.y -= .02
            elif name == 'surprise':
                for index in (14,17,84,181,91,146,314,405,321,375):
                    self.observation.landmarks[group][index].y += .035
            elif name == 'blink':
                for upper,lower in ((159,145),(158,153),(160,144),(386,374),(385,380),(387,373)):
                    points = self.observation.landmarks[group]
                    points[upper].y = points[lower].y = (points[upper].y+points[lower].y)/2
            self.observation = replace(self.observation, expressions=expressions, transformation_matrix=None)
        self._sync_world()

    def close(self):
        pass


def write_state(path, provider):
    path = Path(path)
    temporary = path.with_suffix('.tmp')
    observation = provider.read()
    temporary.write_text(json.dumps({'observation':observation_to_dict(observation), 'stale':provider.stale}, allow_nan=False), encoding='utf-8')
    temporary.replace(path)
    return observation


class FileSimulatorProvider:
    """Consume atomic panel snapshots without a camera or network listener."""
    def __init__(self, profile, path):
        self.profile = profile
        self.path = Path(path)
        self.observation = None

    def read(self):
        state = json.loads(self.path.read_text(encoding='utf-8'))
        observation = observation_from_dict(state['observation'])
        if observation.profile != self.profile:
            raise ValueError('Simulator profile does not match game profile')
        self.observation = observation
        return observation

    def close(self):
        pass
