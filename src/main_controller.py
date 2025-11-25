# src/main_controller.py
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
from src.physics_engine import PhysicsEngine
from src.renderer import Renderer
from src.special_effect import SpecialEffect
from src.simulation_data import SimulationState
from src.config import SIMULATION_PARAMS, RENDERER_PARAMS

class MainController:
    def __init__(self, save_gif=True):
        # 1.初始化各个模块
        self.physics = PhysicsEngine(SIMULATION_PARAMS)
        self.renderer = Renderer()
        self.effect = SpecialEffect(self.renderer.ax,self.renderer)

        # 2.创建初始状态
        self.state = self.physics.initialize_physics_state(SIMULATION_PARAMS)

        # 3.初始化渲染
        self.renderer.initialize_graphics(self.state)

        # 4. 创建动画
        self.ani = FuncAnimation(
            self.renderer.fig,
            self.update_frame,
            interval=int(SIMULATION_PARAMS['dt'] * 1000),  # dt 是秒，转毫秒
            blit=False,
            cache_frame_data=False
        )

    def update_frame(self, frame):
        old_state = self.state

        # 1. 先进行正常的运动积分
        after_acceleration_new_bodies = self.physics.compute_acceleration_and_update(old_state)

        # 用运动后的状态作为基础进行碰撞检测
        temp_state = SimulationState(after_acceleration_new_bodies, old_state.time, old_state.frame)

        # 2. 检测融合
        fusion_id, remove_id, fused_pair, after_fusion_new_bodies = self.physics.detect_fusion(temp_state)
        # 3. 如果有融合，创建特效
        if fusion_id:
            # 需要传入正确的旧状态和新状态给特效
            new_state_for_effect = SimulationState(after_fusion_new_bodies, old_state.time, old_state.frame)
            self.effect.create_fusion_effect(fusion_id, old_state, new_state_for_effect)
            self.effect.create_remove_effect(remove_id, temp_state,fused_pair)

        # 4. 删除被融合天体
        after_del_new_bodies = self.physics.update_del_bodies(remove_id, after_fusion_new_bodies)
        # 5. 真实状态再次更新（删除天体)
        self.state = SimulationState(
            bodies=after_del_new_bodies,
            time=old_state.time + SIMULATION_PARAMS['dt'],
            frame=old_state.frame + 1
        )

        # 6. 渲染更新
        updated_graphics = self.renderer.update_graphics(self.state,remove_id)
        self.effect.update_remove_effect()
        self.effect.update_fusion_effect()

        return self.renderer.ax.patches


    def run(self):
        plt.show()


