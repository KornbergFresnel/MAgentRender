import pygame as pg
import numpy as np

import config

from pygame.locals import *

from entity import Hold
from test.api import Env, ModelGroup
from test.model import DQN
from player.player import Player
from control.controls import ControlPanel


# ==== Initialize environment ====
hold = Hold()
max_steps = 600
map_size = 100

pg.init()
info = pg.display.Info()
resolution = int(info.current_w * config.GLOBAL_SCALE), int(info.current_h * config.GLOBAL_SCALE)
hold.resolution = resolution
hold.screen = pg.display.set_mode(resolution, DOUBLEBUF | HWSURFACE, 0)
pg.display.set_caption('Magent Render')

split_line = int(resolution[0] * (1. - config.SPLIT_ETA))
env = Env('battle', in_range={'x': [0, resolution[0] - split_line], 'y': [0, resolution[1]]}, max_steps=max_steps,
          map_size=map_size)


# ==== Set player ====
player = Player(pos=(0, 0), control_area=(resolution[0] - split_line, resolution[1]), bg_color=config.PLAYER_BG_COLOR,
                agent_num=env.agent_num, n_group=2)
player.load_everything(pos_list=env.get_states())


# ==== Set control panel ====
control = ControlPanel(pos=(resolution[0] - split_line, 0), control_area=(split_line, resolution[1]),
                       bg_color=config.CONTROL_BG_COLOR, init_points=env.get_rewards())
control.load_everything()


# ==== Set models ====
model_group = ModelGroup(sub_models=[DQN, DQN], env=env)


# ==== Main runner ====
hold.running = True
clock = pg.time.Clock()
step = 0
max_len = 400
group = pg.sprite.Group(player, control)
learning_curve = env.get_rewards()
env.start()
done = False

while hold.running and step < max_steps and not done:
    for event in pg.event.get():
        if event.type == QUIT:
            hold.running = False
        elif event.type == KEYDOWN:
            hold.key_event_handler(pg.key.get_pressed())
        control.listen_widgets_event(event)

    group.draw(hold.screen)

    # player need update states
    actions = model_group.act(obs=env.get_obs())
    player.update_state(env.get_states(actions))
    group.update(int(clock.get_fps()), learning_curve if step % config.FLUSH_FREQ == 0 else None, env.get_num())
    pg.display.flip()
    clock.tick(config.FPS)
    done = env.done
    step += 1
    learning_curve = env.get_rewards()
    if len(learning_curve[0]) > 80:
        for i in range(2):
            learning_curve[i] = learning_curve[i][-80:]

pg.quit()
