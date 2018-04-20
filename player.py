import pygame as pg
import numpy as np
from pygame.locals import *
from numpy.random import randint
from pygame.sprite import Sprite
from config import Color


class Player(Sprite):
    def __init__(self, control_area: tuple, bg_color: tuple, agent_num: int):
        super().__init__()
        self.bg_color = bg_color
        self.surf = pg.Surface(control_area).convert()
        self.surf.fill(bg_color)
        self.rect = self.surf.get_rect()
        self.width, self.height = control_area
        self.border_width = 0
        self.agents = None
        self.step_random = lambda x: zip(randint(-1, 2, size=x), randint(-1, 2, size=x))
        self.agent_property = {'size': [10, 10], 'color': (200, 200, 200)}
        self.agent_border = (self.width - self.border_width - 10, self.height - self.border_width - 10)
        self.agent_num = agent_num
    
    def _custom_ui(self):
        # Display some text at center
        font = pg.font.Font(None, 36)
        text = font.render('Hello World!', 1, (255, 255, 255))
        textpos = text.get_rect(center=(self.rect.centerx, self.rect.centery))
        self.surf.blit(text, textpos)

        # Draw border line
        # pg.draw.lines(self.surf, Color.WHITE, True, [[0, 0], [self.width, 0], [self.width, self.height], [0, self.height]], self.border_width)
        self._init_obj()
    
    def _init_obj(self):
        w, h = self.agent_property['size']
        # Produce agent
        width_random = randint(low=self.border_width, high=self.agent_border[0], size=self.agent_num)
        height_random = randint(low=self.border_width, high=self.agent_border[1], size=self.agent_num)
        self.agents = dict(zip(range(self.agent_num), zip(width_random, height_random)))

        # Draw agent
        for pos in self.agents.values():
            pg.draw.rect(self.surf, Color.AGENT, [pos[0], pos[1], w, h])
    
    def load_everything(self):
        self._custom_ui()
    
    def step(self):
        """Let agent go
        """
        # refill backgroud
        self.surf.fill(self.bg_color)

        step = list(self.step_random(self.agent_num))
        w, h = self.agent_property['size']
        for i, key in enumerate(self.agents.keys()):
            x = max(self.border_width, min(self.agent_border[0], self.agents[key][0] + step[i][0]))
            y = max(self.border_width, min(self.agent_border[1], self.agents[key][1] + step[i][1]))
            self.agents[key] = (x, y)
            pg.draw.rect(self.surf, Color.AGENT, [self.agents[key][0], self.agents[key][1], w, h])  
