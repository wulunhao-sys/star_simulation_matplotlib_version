# src/special_effect.py   ← 完整正确版本（请完全替换）
import matplotlib.pyplot as plt
import numpy as np
from src.config import RENDERER_PARAMS, SIMULATION_PARAMS


class SpecialEffect:
    def __init__(self, ax,renderer = None):
        self.ax = ax
        self.renderer = renderer
        self.total_frame = int(RENDERER_PARAMS['transition_ani_time'] / SIMULATION_PARAMS['dt']) + 1
        self.layer = RENDERER_PARAMS['layer']
        self.fusion_effect = []
        self.remove_effect = []

    def create_remove_effect(self, remove_id, state,fused_pair):
        for rid in remove_id:
            body = state.get_body(rid)
            circles = self._create_circles(body['position'], body['radius'], body['mass'],rid)
            for pair in fused_pair:
                if rid == pair[0]:
                    who_to_eat = pair[1]
            fusion_body = state.get_body(who_to_eat)
            end_pos = fusion_body['position']
            self.remove_effect.append({
                'circles': circles,
                'start_pos': body['position'].copy(),
                'end_pos':end_pos,
                'vel': body['velocity'].copy(),
                'radius': body['radius'],
                'frame': 0
            })

    def create_fusion_effect(self, fusion_id, old_state, new_state):
        for fid in fusion_id:
            #隐藏原天体
            if self.renderer:
                self.renderer.hide_body(fid)
            old_body = old_state.get_body(fid)
            new_body = new_state.get_body(fid)
            circles = self._create_circles(old_body['position'], old_body['radius'], old_body['mass'],fid)
            self.fusion_effect.append({
                'circles': circles,
                'id':fid,
                'start_pos': old_body['position'].copy(),
                'end_pos': new_body['position'].copy(),
                'start_radius': old_body['radius'],
                'end_radius': new_body['radius'],
                'frame': 0
            })

    def _create_circles(self, pos, radius, mass,id):
        circles = []
        ratio = np.clip((mass - SIMULATION_PARAMS['min_mass']) / (SIMULATION_PARAMS['max_mass'] - SIMULATION_PARAMS['min_mass'] + 1e-6), 0, 1)
        idx = min(int(ratio * 6), 5)
        inner = np.array(RENDERER_PARAMS['inner_color'][idx])
        outer = np.array(RENDERER_PARAMS['outer_color'][idx])
        if SIMULATION_PARAMS['center_mass'] and id == 0:
            inner = np.array([0.0, 0.0, 0.0])
            outer = outer_color = np.array([0.40, 0.02, 0.02])
        for layer in range(self.layer):
                r = (layer + 1) * radius / self.layer
                t = layer / (self.layer - 1) if self.layer > 1 else 0
                color = (1 - t) * inner + t * outer
                if layer == 0:
                    circle = plt.Circle(pos, r, color=color, ec='none', zorder=20)
                else:
                    lw = 1.5 + 28 * (r / radius)
                    circle = plt.Circle(pos, r, color=color, fill=False, linewidth=lw, ec=color, zorder=19 - layer)
                self.ax.add_patch(circle)
                circles.append(circle)
        return circles

    def update_remove_effect(self):
        for eff in self.remove_effect[:]:
            if eff['frame'] >= self.total_frame:
                for c in eff['circles']:
                    c.set_visible(False)
                self.remove_effect.remove(eff)
            else:
                eff['frame'] += 1
                t = eff['frame'] / self.total_frame
                t = t * t * (3 - 2 * t)
                old_pos = eff['start_pos']
                new_pos = eff['end_pos']
                for i, c in enumerate(eff['circles']):
                    c.center = t*new_pos+(1-t)*old_pos
                    c.radius = (i + 1) * eff['radius'] * (1 - t) / self.layer
                    c.set_alpha(1 - t)

    def update_fusion_effect(self):
        for eff in self.fusion_effect[:]:
            if eff['frame'] >= self.total_frame:
                for c in eff['circles']:
                    c.set_visible(False)
                if self.renderer:
                    self.renderer.show_body(eff['id'])
                self.fusion_effect.remove(eff)
            else:
                eff['frame'] += 1
                t = eff['frame'] / self.total_frame
                t = t * t * (3 - 2 * t)
                pos = (1 - t) * eff['start_pos'] + t * eff['end_pos']
                radius = (1 - t) * eff['start_radius'] + t * eff['end_radius']
                for i, c in enumerate(eff['circles']):
                    c.center = pos
                    c.radius = (i + 1) * radius / self.layer

