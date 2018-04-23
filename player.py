import pygame as pg
import numpy as np
from pygame.locals import *
from numpy.random import randint
from pygame.sprite import Sprite
from config import Color
from config import SPEED_MAX, SPEED_MIN


class Agent(Sprite):
    def __init__(self, agent_id, color, pos, w, h, x_min, x_max, y_min, y_max):
        super().__init__()
        self.agent_id = agent_id
        self.image = pg.Surface((w, h))
        self.image.fill(color)
        self.rect = self.image.get_rect(center=(pos[0] + int(w / 2), pos[1] + int(h / 2)))
        self.x_min, self.x_max, self.y_min, self.y_max = \
            x_min, x_max, y_min, y_max

        init = np.random.choice([1, 2, 3, 4], 1)[0]
        inity = np.random.choice([1, 2, 3, 4], 1)[0]
        self.dir_x, self.dir_y = np.random.choice([-init, init], 1), np.random.choice([-inity, inity], 1)
        self.stat = 1
    
    def move(self, dir_x, dir_y):
        # if self.stat % 30 == 0:
        #     init = np.random.choice([1, 2, 3, 4], 1)[0]
        #     inity = np.random.choice([1, 2, 3, 4], 1)[0]
        #     self.dir_x, self.dir_y = np.random.choice([-init, init], 1), np.random.choice([-inity, inity], 1)

        new_x = self.rect.x + self.rect.width + self.dir_x
        new_y = self.rect.y + self.rect.height + self.dir_y
        if new_x > self.x_max or new_x - self.rect.width < self.x_min:
            self.dir_x *= -1
        if new_y > self.y_max or new_y - self.rect.height < self.y_min:
            self.dir_y *= -1
        
        self.stat += 1
    
    def update(self):
        self.rect.move_ip(self.dir_x, self.dir_y)      


class Player(Sprite):
    def __init__(self, pos, control_area: tuple, bg_color: tuple, agent_num: int):
        super().__init__()
        self.bg_color = bg_color
        self.surf = pg.Surface(control_area).convert()
        self.surf.fill(bg_color)
        self.rect = self.surf.get_rect(center=(pos[0] + int(control_area[0] / 2), pos[1] + int(control_area[1] / 2)))
        self.image = self.surf
        self.width, self.height = control_area
        self.border_width = 0
        self.agents = None
        # self.step_random = lambda x: zip(randint(SPEED_MIN, SPEED_MAX, size=x), randint(SPEED_MIN, SPEED_MAX, size=x))
        self.step_random = lambda x: zip(np.random.choice([-1, 1], size=x), np.random.choice([-1, 1], size=x))
        self.agent_property = {'size': [10, 10], 'color': (200, 200, 200)}
        self.agent_border = (self.width - self.border_width - 10, self.height - self.border_width - 10)
        self.agent_num = agent_num
        self.last_fps = 0
    
    def _custom_ui(self):
        # Display some text at center
        font = pg.font.Font(None, 36)
        text = font.render('Hello World!', 1, (255, 255, 255))
        textpos = text.get_rect(center=(self.rect.centerx, self.rect.centery))
        self.surf.blit(text, textpos)

        # Draw border line
        self._init_obj()
    
    def _init_obj(self):
        w, h = self.agent_property['size']
        # Produce agent
        width_random = randint(low=self.border_width, high=self.agent_border[0], size=self.agent_num)
        height_random = randint(low=self.border_width, high=self.agent_border[1], size=self.agent_num)
        agents = dict(zip(range(self.agent_num), zip(width_random, height_random)))

        # Draw agent
        self.agents = pg.sprite.Group()
        for agent_id, pos in agents.items():
            self.agents.add(Agent(agent_id, Color.AGENT, pos, w, h, 0, self.rect.x + self.rect.width, 0, self.rect.y + self.rect.height))
        
        width_random = randint(low=self.border_width, high=self.agent_border[0], size=self.agent_num)
        height_random = randint(low=self.border_width, high=self.agent_border[1], size=self.agent_num)
        agents = dict(zip(range(self.agent_num), zip(width_random, height_random)))

        for agent_id, pos in agents.items():
            self.agents.add(Agent(agent_id, Color.AGENT_B, pos, w, h, 0, self.rect.x + self.rect.width, 0, self.rect.y + self.rect.height))
    
    def load_everything(self):
        self._custom_ui()
    
    def flush_fps(self, fps: int, color: tuple):
        font = pg.font.Font(None, 20)
        fps_text = font.render('FPS: {}'.format(fps), 1, color)
        self.last_fps = fps
        textpos = fps_text.get_rect()
        textpos.centerx = self.rect.centerx
        self.surf.blit(fps_text, textpos)
    
    def update(self, *args):
        """Let agent go
        """
        # refill backgroud
        self.surf.fill(self.bg_color)

        step = list(self.step_random(self.agent_num * 2))
        for i in range(len(step)):
            self.agents.sprites()[i].move(step[i][0], step[i][1]) 
        self.agents.draw(self.surf)
        self.agents.update()
        # display fps
        self.flush_fps(fps=args[0], color=Color.BLACK)
