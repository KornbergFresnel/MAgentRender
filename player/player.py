import pygame as pg
import numpy as np

from pygame.locals import *
from numpy.random import randint
from pygame.sprite import Sprite
from config import Color, GLOBAL_SCALE
from config import SPEED_MAX, SPEED_MIN
from multiprocessing.pool import Pool
from agent import AgentGroup


class Player(Sprite):
    def __init__(self, pos, control_area: tuple, bg_color: tuple, n_group: int, agent_num: int, pos: list):
        super().__init__()
        self.bg_color = bg_color
        self.surf = pg.Surface(control_area).convert()
        self.surf.fill(bg_color)
        self.rect = self.surf.get_rect(center=(pos[0] + int(control_area[0] / 2), pos[1] + int(control_area[1] / 2)))
        self.image = self.surf
        self.width, self.height = control_area
        self.border_width = 0
        self.n_group = n_group
        self.agent_group = []
        self.agent_property = {'size': [10, 10], 'color': (200, 200, 200)}
        self.agent_border = (self.width - self.border_width - 10, self.height - self.border_width - 10)
        self.agent_num = agent_num
        self.last_fps = 0

    def _custom_ui(self):
        # Display some text at center
        font = pg.font.Font(None, int(36 * GLOBAL_SCALE))
        text = font.render('Hello World!', 1, (255, 255, 255))
        textpos = text.get_rect(center=(self.rect.centerx, self.rect.centery))
        self.surf.blit(text, textpos)

    def _init_obj(self, pos_list: list):
        w, h = self.agent_property['size']
        x_min, x_max = 0, self.width - w
        y_min, y_max = 0, self.height - h

        assert len(pos_list) == self.n_group
        for i in range(self.n_group):
            self.agent_group.append(AgentGroup(self.agent_num, pos_list[i], Color.AGENT(i), w, h, x_min, x_max, y_min, y_max))

    def load_everything(self, pos_list):
        self._custom_ui()
        self._init_obj(pos_list)

    def flush_fps(self, fps: int):
        font = pg.font.Font(None, 20)
        fps_text = font.render('FPS: {}'.format(fps), 1, Color.BLACK)
        self.last_fps = fps
        textpos = fps_text.get_rect()
        textpos.centerx = self.rect.centerx
        self.surf.blit(fps_text, textpos)

    def update_state(self, state_list: list):
        """Update states of agents with different groups

        Parameters
        ----------
        states: list
            a state list, and the elements in it are StateLists
        """

        for i in range(self.n_group):
            self.agent_group[i].update_states(state_list[i])

    def update(self, *args):
        """Let agent go
        """

        self.surf.fill(self.bg_color)

        for i in range(self.n_group):
            self.agent_group[i].draw(self.surf)
            self.agent_group[i].update()

        self.flush_fps(fps=args[0])
