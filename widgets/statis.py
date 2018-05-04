import pygame as pg
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.backends.backend_agg as agg
import pylab

from pygame.sprite import Sprite


class StatisPanel(Sprite):
    def __init__(self, pos, width, height, dpi, bg_color, init_points):
        super().__init__()
        self.pos = pos
        self.width = width
        self.height = height
        self.dpi = dpi
        self.figsize = [width / dpi, height / dpi]
        self.bg_color = bg_color

        plt.style.use('seaborn-darkgrid')
        self.palette = plt.get_cmap('Set1')

        self._set(init_points)
    
    def _set(self, learning_curve=None):
        plt.close()
        fig = pylab.figure(figsize=self.figsize, dpi=self.dpi)
        ax = fig.gca()

        # load data
        ax.plot(np.arange(len(learning_curve[0])), learning_curve[0], color=self.palette(0))
        ax.plot(np.arange(len(learning_curve[1])), learning_curve[1], color=self.palette(1))

        plt.tight_layout()
        canvas = agg.FigureCanvasAgg(fig)
        canvas.draw()
        size = canvas.get_width_height()
        renderer = canvas.get_renderer()
        raw_data = renderer.tostring_rgb()
        self.image = pg.image.fromstring(raw_data, size, 'RGB')
        self.rect = self.image.get_rect(center=(self.pos[0] + int(self.width / 2), self.pos[1] + int(self.height / 2)))
    
    def update(self, learning_curve=None):
        if learning_curve is None:
            return
        self.image.fill(self.bg_color, pg.Rect(self.pos[0], self.pos[1], self.width, self.height))
        self._set(learning_curve)
