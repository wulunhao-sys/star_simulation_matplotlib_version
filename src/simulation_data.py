# src/state.py

import numpy as np
from typing import List, Dict


# 一个天体 = 一个字典（和原来一模一样）
def create_body(id: int, mass: float, radius: float,
                position=None, velocity=None)->Dict:
    position = np.zeros(2) if position is None else np.asarray(position)
    velocity = np.zeros(2) if velocity is None else np.asarray(velocity)

    return {
        'id': id,
        'mass': mass,
        'radius': radius,
        'position': position.copy(),  # 希望数据单向流动，后一个步骤不能改之前的数据
        'velocity': velocity.copy(),
        'acceleration': np.zeros(2)
    }


# 整个宇宙 = 一个大字典，里面装着一堆小字典
class SimulationState:
    def __init__(self, bodies: List[dict], time: float = 0.0, frame: int = 0):
        self.bodies = bodies.copy()
        self.time = time
        self.frame = frame

        # 为了快速通过 id 找天体，做一个 id → body 的字典
        self.body_dict = {body['id']: body for body in self.bodies}

    # 通过 id 快速拿到某个天体（融合时最常用）
    def get_body(self, body_id: int) -> dict:
        return self.body_dict[body_id]

    # 返回一个“替换了某个天体”的全新状态（关键！不改原状态）
    def replace_body(self, new_body: dict) -> 'SimulationState':
        new_list = []
        for b in self.bodies:
            if b['id'] == new_body['id']:
                new_list.append(new_body)  # 换成新的
            else:
                new_list.append(b)  # 老的保留
        return SimulationState(new_list, self.time, self.frame)

    # 删除某个天体后返回新状态
    def remove_body(self, body_id: int) -> 'SimulationState': #前向类型声明，让类定义内部也能引用自己
        new_list = [b for b in self.bodies if b['id'] != body_id]
        return SimulationState(new_list, self.time, self.frame)

    # 时间前进一帧
    def next_frame(self, dt: float) -> 'SimulationState':
        return SimulationState(self.bodies, self.time + dt, self.frame + 1)

    # 深拷贝（如果你真的需要可变副本）
    def copy(self) -> 'SimulationState':
        copied_bodies = []
        for b in self.bodies:
            copied_bodies.append({
                'id': b['id'],
                'mass': b['mass'],
                'radius': b['radius'],
                'position': b['position'].copy(),
                'velocity': b['velocity'].copy(),
                'acceleration': b['acceleration'].copy(),
            })
        return SimulationState(copied_bodies, self.time, self.frame)