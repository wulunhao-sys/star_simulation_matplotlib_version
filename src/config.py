#基本配置文件，规定一些不在GUI界面可修改的参数，使用者可在此界面修改更细化的参数

SIMULATION_PARAMS = {
    'num_bodies': 10,
    'G': 4,
    'total_time': 10,
    'dt': 0.05,
    'max_velocity': 5,
    'center_mass': True,
    'center_mass_num':3000,
    'min_mass':10,
    'max_mass':1000,
    'x_lim':50,
    'y_lim':50 #创建天体分布范围
}


RENDERER_PARAMS = {
    'show_trails': True,
    'layer': 30,
    #质量由小到大共划分六个区间
    #深蓝-蓝-淡蓝-淡黄-黄-橙红
    'inner_color':[(1.0, 0.7, 0.3),(0.2, 0.4, 1.0),(0.4, 0.7, 0.9),
                   (0.8, 0.9, 1.0),(1.0, 1.0, 0.8),(1.0, 0.9, 0.6)],
    #白-淡黄-浅橙-橙-深橙-深橙
    'outer_color':[(1.0, 1.0, 1.0),(1.0, 0.9, 0.8),(1.0, 0.8, 0.6),
                   (1.0, 0.7, 0.3),(1.0, 0.5, 0.1),(1.0, 0.3, 0.0)],
    'axe_x_lim':(-50, 50),
    'axe_y_lim':(-50, 50),#坐标轴范围
    'figure_size':(10,10),
    'transition_ani_time':0.25, #融合过渡动画持续时间，单位：s
}
GUI_CONFIG = {
    'window_size': '800x800',
    'theme': 'Dark',

}
