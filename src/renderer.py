#src/renderer 渲染模块，只负责渲染真实对象
import matplotlib.pyplot as plt
import numpy as np
from src.config import RENDERER_PARAMS, SIMULATION_PARAMS
from typing import List,Tuple,Dict


class Renderer:
    def __init__(self):
        self.layer = RENDERER_PARAMS['layer']
        self.dt = SIMULATION_PARAMS['dt']

        self.fig, self.ax = plt.subplots(figsize=RENDERER_PARAMS['figure_size'])
        self.ax.set_xlim(RENDERER_PARAMS['axe_x_lim'])
        self.ax.set_ylim(RENDERER_PARAMS['axe_y_lim'])
        self.ax.set_aspect('equal')
        self.ax.set_facecolor('black')
        self.fig.patch.set_facecolor('black')
        # 背景星星
        num_stars = 300
        star_x = np.random.uniform(*RENDERER_PARAMS['axe_x_lim'], num_stars)
        star_y = np.random.uniform(*RENDERER_PARAMS['axe_y_lim'], num_stars)
        star_sizes = np.random.uniform(0.5, 3, num_stars)
        star_alpha = np.random.uniform(0.4, 1, num_stars)
        self.ax.scatter(star_x, star_y, s=star_sizes, c='white', alpha=star_alpha,zorder = 15-self.layer)
        self.graphics = []  # 真实天体对象


    def initialize_graphics(self, SimulationState):
        bodies = SimulationState.bodies
        self.graphics.clear() #如果重置过模拟，则需要清理之前的图形对象
        for body in bodies:
            circles = self.create_single_body(body)
            self.graphics.append({
                'id': body['id'],
                'body_circles': circles,
                'radius': body['radius'],
            })

    def update_graphics(self,SimulationState,remove_id):
        """根据物理状态更新天体对象"""
        bodies = SimulationState.bodies
        graphic_dict = {g['id']: g for g in self.graphics}
        body_dict = {b['id']: b for b in bodies}
        current_ids = set(body_dict.keys())
        #从画布上删除消失天体
        for id in remove_id:
            for c in graphic_dict[id]['body_circles']:
                c.remove()


        # 删除已不存在的天体图形
        self.graphics = [g for g in self.graphics if g['id'] in current_ids]

        # 更新现有天体
        for graphic in self.graphics:
            pos = body_dict[graphic['id']]['position']
            new_radius = body_dict[graphic['id']]['radius']
            for layer,circle in enumerate(graphic['body_circles']):
                layer_radius = (layer + 1) * new_radius / self.layer
                circle.center = (pos[0], pos[1])
                circle.radius=layer_radius

        # 调试信息
        #for graphic in self.graphics:
            #print(f'天体半径{graphic["id"]}：{graphic["radius"]}')

    def create_single_body(self, body)->List:
        """利用多层圆环创建天体实现颜色径向渐变"""
        circles = []
        mass = body['mass']
        radius = body['radius']
        pos = body['position']

        # === 正确的质量 → 颜色映射
        min_m = SIMULATION_PARAMS['min_mass']
        max_m = SIMULATION_PARAMS['max_mass']
        ratio = (mass - min_m) / (max_m - min_m + 1e-6)
        idx = min(int(ratio * 6), 5)  # 6个颜色段
        inner_color = np.array(RENDERER_PARAMS['inner_color'][idx])
        outer_color = np.array(RENDERER_PARAMS['outer_color'][idx])
        if body['id'] == 0 and SIMULATION_PARAMS['center_mass']:
            inner_color = np.array([0.0, 0.0, 0.0])      # 绝对纯黑（视界）
            outer_color = outer_color = np.array([0.40, 0.02, 0.02])    # 深紫红吸积盘辉光（最经典的黑洞颜色）

        for layer in range(self.layer):
            current_radius = (layer + 1) * radius / self.layer
            # 颜色从内到外线性渐变
            t = layer / (self.layer - 1) if self.layer > 1 else 0
            color = (1 - t) * inner_color + t * outer_color

            if layer == 0:
                # 最里面一层：实心圆
                circle = plt.Circle(pos, current_radius, color=color, ec='none', zorder=10)
            else:
                # 外层：空心圆环，线宽随半径自适应（越大的天体外环越粗）
                base_lw = 1.5
                linewidth = base_lw + 28 * (current_radius / radius)
                circle = plt.Circle(pos, current_radius, color=color, fill=False,
                                    linewidth=linewidth, ec=color, zorder=10 - layer)

            self.ax.add_patch(circle)
            circles.append(circle)

        return circles

    def hide_body(self, body_id):
        """隐藏某个天体的所有图形"""
        for graphic in self.graphics:
            if graphic['id'] == body_id:
                for circle in graphic['body_circles']:
                    circle.set_visible(False)
                break

    def show_body(self, body_id):
        """显示某个天体的所有图形"""
        for graphic in self.graphics:
            if graphic['id'] == body_id:
                for circle in graphic['body_circles']:
                    circle.set_visible(True)
                break