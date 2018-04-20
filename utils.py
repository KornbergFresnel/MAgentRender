import pygame as pg
from pygame.locals import *


def draw_rect(surface: pg.Surface, color: tuple, top: tuple, w: int, h: int):
    top = tuple(map(round, top))
    pg.draw.rect(surface, color, top w, h)


class Hold:
    def __init__(self):
        self.running = False
        self.screen = None
        self.background = None
        self.resolution = None
    
    def key_event_handler(self, key_pressed: dict):
        if key_pressed[K_q] or key_pressed[K_ESCAPE]:
            self.running = False
        elif key_pressed[K_w]:
            print('[INFO] You pressed "w"')
    
    def mouse_event_handler(self, event):
        pass