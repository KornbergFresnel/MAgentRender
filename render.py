import pygame as pg

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


# ==== Set player ====
player = Player(control_area=(int(resolution[0] * config.SPLIT_ETA), resolution[1]), bg_color=config.PLAYER_BG_COLOR, agent_num=464)
player.load_everything()


# ==== Set control panel ====
control = ControlPanel(control_area=(int(resolution[0] * (1. - config.SPLIT_ETA)), resolution[1]), bg_color=config.CONTROL_BG_COLOR)
control.load_everything()


# ==== Main runner ====
hold.running = True
clock = pg.time.Clock()

while hold.running:
    for event in pg.event.get():
        if event.type == QUIT:
            hold.running = False
        elif event.type == KEYDOWN:
            hold.key_event_handler(pg.key.get_pressed())
        control.listen_widgets_event(event)
    
    player.step()
    control.update()
    hold.screen.blit(player.surf, (0, 0))
    hold.screen.blit(control.surf, (int(resolution[0] * config.SPLIT_ETA), 0))
    pg.display.flip()
    clock.tick(config.FPS)

pg.quit()
