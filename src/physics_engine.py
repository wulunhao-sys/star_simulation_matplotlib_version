# physics_engine.py - 纯物理计算，不涉及任何动画
import numpy as np
from typing import List, Dict,Tuple

from src.simulation_data import SimulationState

"""原则：尽量以天体id代替天体索引进行遍历查找"""

class PhysicsEngine:
    def __init__(self, params):
        self.params = params
        self.G = params['G']
        self.dt = params['dt']
        self.id = 0

    def initialize_physics_state(self, params:Dict)->SimulationState:
        """初始化物理状态"""
        num_bodies = params['num_bodies']
        bodies = []
        time = 0.0
        frame = 0

        for i in range(num_bodies):
            # 创建天体状态
            mass = np.random.uniform(params['min_mass'], params['max_mass'])
            if params['center_mass'] and i == 0:
                mass = params['center_mass_num']

            radius = 3 / 7 * mass ** (1 / 3)

            position = np.array([
                np.random.uniform(-params['x_lim'], params['x_lim']),
                np.random.uniform(-params['y_lim'], params['y_lim'])
            ])

            velocity = np.array([
                np.random.uniform(-params['max_velocity'], params['max_velocity']),
                np.random.uniform(-params['max_velocity'], params['max_velocity'])
            ])

            if params['center_mass'] and i == 0:
                position = np.array([0.0, 0.0])
                velocity = np.array([0.0, 0.0])

            body = {}
            body['position'] = position
            body['velocity'] = velocity
            body['mass'] = mass
            body['radius'] = radius
            body['id'] = self.id
            body['acceleration'] = np.array([0, 0])
            bodies.append(body)
            self.id += 1
        return SimulationState(bodies.copy(),time,frame)

    def detect_fusion(self,SimulationState)->Tuple[List,List,List[Dict],List[Dict]]:
        """检测哪些天体需要融合，创建新列表更新融合对象，但其中不删除被融合天体"""
        bodies = SimulationState.bodies
        fusion_pairs = [] #创建列表储存需要融合的天体对
        fusion_id = [] #储存融合天体id
        remove_id = [] #储存消失天体id
        fused_pair = [] #储存融合队，为每个消失天体找到被谁吞了
        fusion_new_bodies = []
        after_fusion_new_bodies = [] #融合出的新天体
        body_dict = {b['id']: b for b in bodies}
        for i in range(len(bodies)):
            for j in range(i+1,len(bodies)):
                body_a = bodies[i]
                body_b = bodies[j]
                dr=body_a['position'] - body_b['position']
                distance = np.linalg.norm(dr)
                if distance < (body_a['radius'] + body_b['radius'])/3:
                    fusion_pairs.append((distance,body_a['id'],body_b['id']))
        # 按距离排序，优先处理最近的天体对
        fusion_pairs.sort(key=lambda x: x[0])
        for i in range(len(fusion_pairs)):
            #用id进行匹配
            matching_body_a = body_dict[fusion_pairs[i][1]]
            matching_body_b = body_dict[fusion_pairs[i][2]]
            if matching_body_a['mass'] < matching_body_b['mass']:
                fusion_body_id = fusion_pairs[i][2]
                remove_body_id = fusion_pairs[i][1]
            else:
                fusion_body_id = fusion_pairs[i][1]
                remove_body_id = fusion_pairs[i][2]
            if remove_body_id not in remove_id and fusion_body_id not in remove_id:
                fusion_id.append(fusion_body_id)
                remove_id.append(remove_body_id)
                fusion_body = body_dict[fusion_body_id]
                removed_body = body_dict[remove_body_id]
                #根据动量守恒计算融合后新天体状态
                new_mass = fusion_body['mass']+removed_body['mass']
                new_position = (fusion_body['position']*fusion_body['mass']+
                removed_body['position']*removed_body['mass'])/new_mass
                new_velocity = (fusion_body['velocity'] * fusion_body['mass'] +
                                removed_body['velocity'] * removed_body['mass']) / new_mass
                new_radius = 3 / 7 * new_mass ** (1 / 3)
                fusion_new_body = {
                    'mass': new_mass,
                    'position': new_position,
                    'velocity': new_velocity,
                    'radius': new_radius,
                    'id': fusion_body_id,
                    'acceleration': fusion_body['acceleration']
                }
                fusion_new_bodies.append(fusion_new_body)
                fused_pair.append([remove_body_id,fusion_body_id])

        for body1 in bodies:
            for body2 in fusion_new_bodies:
                if body1['id'] == body2['id']:
                    after_fusion_new_bodies.append(body2)
                    break
            else:
                after_fusion_new_bodies.append(body1)
        return fusion_id,remove_id,fused_pair,after_fusion_new_bodies.copy()

    def update_del_bodies(self, remove_id,after_fusion_new_bodies)->List[Dict]:
        """更新融合天体数据,通过新列表进行替换"""
        remove_set = set(remove_id)
        after_del_new_bodies = []
        for new_body in after_fusion_new_bodies:
            for id in remove_set:
                if new_body['id'] == id:
                    break
            else:
                after_del_new_bodies.append(new_body)
        return after_del_new_bodies

    def compute_acceleration_and_update(self,SimulationState)->List[Dict]:
        """计算天体加速度并根据此更新位置速度"""
        bodies = SimulationState.bodies
        after_acceleration_new_bodies = []

        accelerations = []
        for i,body_i in enumerate(bodies):
            acceleration = np.array([0.0, 0.0])
            for j in range(len(bodies)):
                body_i = bodies[i]
                body_j = bodies[j]
                if i != j:
                    dr = body_i['position'] - body_j['position']
                    distance = np.linalg.norm(dr)+2 # 加1是为了防止除以0
                    force_magnitude = self.G * body_j['mass'] / (distance ** 2)
                    acceleration += force_magnitude * dr / distance
            accelerations.append(acceleration)
        for i,body in enumerate(bodies):
            acceleration = accelerations[i]
            velocity = body['velocity']+acceleration*self.dt
            position = (body['position']+body['velocity']*self.dt+
                        1/2*acceleration*self.dt**2)
            after_acceleration_new_bodies.append({
                'position': position.copy(),
                'velocity': velocity.copy(),
                'mass': body['mass'],
                'radius': body['radius'],
                'acceleration': acceleration.copy(),
                'id': body['id']
            })
        return after_acceleration_new_bodies







