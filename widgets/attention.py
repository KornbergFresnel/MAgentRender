"""Attention support for display local view of a certain agent,
it is in test processing currently
"""

import pygame as pg
import numpy as np
import math
import matplotlib.pyplot as plt
import matplotlib.backends.backend_agg as agg
import pylab

from pygame.sprite import Sprite
from config import Color
from multiprocessing.dummy import Pool as ThreadPool


def draw_rects(surf, color, num, size, x_min, x_max, y_min, y_max):
    width_random = np.random.randint(low=x_min, high=x_max, size=num)
    height_random = np.random.randint(low=y_min, high=y_max, size=num)
    pos_list = list(zip(width_random, height_random))

    for i, pos in enumerate(pos_list):
        color = Color.AGENT(i % 2)
        pg.draw.rect(surf, color, [pos[0], pos[1], size, size])
    

class Attention(Sprite):
    def __init__(self, pos, width, height, bg_color):
        super().__init__()
        self.width = width
        self.height = height
        self.image = pg.Surface((width, height))
        self.image.fill(bg_color)
        self.rect = self.image.get_rect(center=(pos[0], pos[1]))
        self.radius = int(height / 2.5)
        self.bg_color = bg_color
        print('[INFO] width, height', pos[0], pos[1] - 50)

        width = height = self.radius / math.sqrt(2)
        self.fake_centerx = pos[0] - self.rect.x
        self.fake_centery = pos[1] - self.rect.y
        self.min_x = self.fake_centerx - width
        self.min_y = self.fake_centery - height
        self.max_x = self.fake_centerx + width
        self.max_y = self.fake_centery + height

        pg.draw.circle(self.image, (255, 255, 255), [self.fake_centerx, self.fake_centery], self.radius, self.radius)
        pg.draw.circle(self.image, (0, 0, 0), [self.fake_centerx, self.fake_centery], self.radius + 2, 2)

        self.stat = 1
        
    def _set(self, attention=None):
        pg.draw.circle(self.image, (255, 255, 255), [self.fake_centerx, self.fake_centery], self.radius, self.radius)
        draw_rects(self.image, Color.AGENT, num=10, size=10, x_min=self.min_x, x_max=self.max_x - 10, y_min=self.min_y, y_max=self.max_y - 10)
    
    def update(self, *args):
        if self.stat % 1 == 0:
            self.image.fill(self.bg_color)
            self._set()
        self.stat += 1
