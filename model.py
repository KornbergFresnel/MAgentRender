import pygame as pg
import pylab
import matplotlib.pyplot as plt
import matplotlib.backends.backend_agg as agg
import numpy as np
from pygame.locals import *
from numpy.random import randint
from pygame.sprite import Sprite


class Color:
    BLACK = (0, 0, 0)
    WHITE = (255, 255, 255)


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
            pg.draw.rect(self.surf, Color.WHITE, [pos[0], pos[1], w, h])
    
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
            pg.draw.rect(self.surf, Color.WHITE, [self.agents[key][0], self.agents[key][1], w, h])  


class ControlPanel(Sprite):
    def __init__(self, control_area: tuple, bg_color: tuple):
        super().__init__()
        self.surf = pg.Surface(control_area).convert()
        self.surf.fill(bg_color)
        self.rect = self.surf.get_rect()
        self.width, self.height = control_area
    
    def _custom_ui(self):
        # Display some text at center
        font = pg.font.Font(None, 36)
        text = font.render('CONTROL PANEL', 1, (255, 255, 255))
        textpos = text.get_rect()
        textpos.centerx = self.rect.centerx
        textpos.centery += 10
        self.surf.blit(text, textpos)

        last_y = self._basic_info_box(centry_offset=textpos.y + textpos.height + 20)
        last_y = self._statis_info_box(centry_offset=last_y + 20)
    
    def _set_title(self, content: str, font_size: int, centry_offset: int):
        # Display some text at center
        font = pg.font.Font(None, font_size)
        text = font.render(content, 1, (255, 255, 255))
        textpos = text.get_rect()
        # textpos.centerx = self.rect.centerx
        textpos.x = self.rect.x + 20
        textpos.centery += centry_offset
        self.surf.blit(text, textpos)
        return textpos.y + textpos.height
    
    def _basic_info_box(self, centry_offset: int):
        width, height = int(self.width * 0.8), int(self.height * 0.2)

        self.b_info_surf = pg.Surface((width, height))
        self.b_info_surf.fill(Color.WHITE)

        sub_pos = self.b_info_surf.get_rect()
        sub_pos.centerx = self.rect.centerx
        sub_pos.centery += centry_offset
        self.surf.blit(self.b_info_surf, sub_pos)

        return sub_pos.y + height
    
    def _statis_info_box(self, centry_offset):
        # Set title
        centry_offset = self._set_title(content='Learning curve', font_size=30, centry_offset=centry_offset)
        width, height = int(self.width * 0.8), int(self.height * 0.25)
        dpi = 40
        figsize = [int((width + dpi - 1) / dpi), int((height + dpi - 1) / dpi)]

        # self.statis = pg.Surface((width, height))
        plt.style.use('seaborn-darkgrid')
        palette = plt.get_cmap('Set1')
        fig = pylab.figure(figsize=figsize, dpi=dpi)
        ax = fig.gca()

        # load data
        x = np.arange(0., 2., 0.01)
        y = np.sin(2 * np.pi * x)
        ax.plot(x, y, color=palette(0))
        plt.tight_layout()

        canvas = agg.FigureCanvasAgg(fig)
        canvas.draw()
        size = canvas.get_width_height()
        renderer = canvas.get_renderer()
        raw_data = renderer.tostring_rgb()
        self.statis = pg.image.fromstring(raw_data, size, 'RGB')

        sub_pos = self.statis.get_rect()
        sub_pos.centerx = self.rect.centerx
        sub_pos.centery += centry_offset + 5
        self.statis_pos = sub_pos
        self.surf.blit(self.statis, sub_pos)

        return sub_pos.y + height
    
    def _local_view(self, agent_id):
        pass
    
    def load_everything(self):
        self._custom_ui()
    
    def flush_statis(self):
        pass
