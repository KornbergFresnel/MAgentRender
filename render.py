import pygame as pg
import numpy as np

import config

from pygame.locals import *

from utils import Hold
from player import Player
from controls import ControlPanel


hold = Hold()

pg.init()
info = pg.display.Info()
resolution = int(info.current_w * config.GLOBAL_SCALE), int(info.current_h * config.GLOBAL_SCALE)
hold.resolution = resolution
hold.screen = pg.display.set_mode(resolution, DOUBLEBUF | HWSURFACE, 0)
pg.display.set_caption('Magent Render')


split_line = int(resolution[0] * (1. - config.SPLIT_ETA))
# ==== Set player ====
player = Player(pos=(0, 0), control_area=(resolution[0] - split_line, resolution[1]), bg_color=config.PLAYER_BG_COLOR, agent_num=228)
player.load_everything()


# ==== Set control panel ====
control = ControlPanel(pos=(resolution[0] - split_line, 0), control_area=(split_line, resolution[1]), bg_color=config.CONTROL_BG_COLOR)
control.load_everything()


# ==== Main runner ====
hold.running = True
clock = pg.time.Clock()
step = 0
function = lambda x: np.sin(x * 0.02 * np.pi)
learning_curve = [function(step)]
max_len = 200
group = pg.sprite.Group(player, control)

while hold.running:
    for event in pg.event.get():
        if event.type == QUIT:
            hold.running = False
        elif event.type == KEYDOWN:
            hold.key_event_handler(pg.key.get_pressed())
        control.listen_widgets_event(event)
    
    group.draw(hold.screen)
    group.update(int(clock.get_fps()), learning_curve if step % config.FLUSH_FREQ == 0 else None)
    pg.display.flip()
    clock.tick(config.FPS)
    step += 1
    learning_curve.append(function(step))
    if len(learning_curve) > max_len:
        learning_curve = learning_curve[1:]

pg.quit()
