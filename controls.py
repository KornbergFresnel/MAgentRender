import pygame as pg
import pylab
import matplotlib.pyplot as plt
import matplotlib.backends.backend_agg as agg
import numpy as np
from pygame.locals import *
from numpy.random import randint
from pygame.sprite import Sprite
from config import Color
from widgets import Button, InputText


class ControlPanel(Sprite):
    def __init__(self, control_area: tuple, bg_color: tuple):
        super().__init__()
        self.surf = pg.Surface(control_area).convert()
        self.surf.fill(bg_color)
        self.rect = self.surf.get_rect()
        self.width, self.height = control_area
        self.boder_margin = 20
    
    def _custom_ui(self):
        # Display some text at center
        font = pg.font.Font(None, 36)
        text = font.render('CONTROL PANEL', 1, (255, 255, 255))
        textpos = text.get_rect()
        textpos.centerx = self.rect.centerx
        textpos.centery += 10
        self.surf.blit(text, textpos)

        last_y = textpos.y + textpos.height
        # Draw logo
        last_y = self._draw_logo(centry_offset=last_y + 20)
        last_y = self._statis_info_box(centry_offset=last_y + 20)
        last_y = self._add_widgets(centry_offset=last_y + 20)
        self._local_view(centry_offset=last_y + 20)
    
    def _draw_logo(self, centry_offset: int):
        last_y, line_width, margin = centry_offset, 3, 4
        y_step = line_width + margin
        border_margin = 20
        dots = [[border_margin, last_y], [self.width - border_margin, last_y], 
                [self.width - border_margin, last_y + y_step * 2], [border_margin, last_y + y_step * 2],
                [border_margin, last_y + y_step * 4], [self.width - border_margin, last_y + y_step * 4]]
        pg.draw.lines(self.surf, Color.WHITE, False, dots, line_width)
        return last_y + y_step * 5
    
    def _set_title(self, content: str, font_size: int, centry_offset: int, height: int):
        # Display some text at center
        font = pg.font.Font(None, font_size)
        text = font.render(content, 1, (255, 255, 255))
        textpos = text.get_rect()
        # textpos.centerx = self.rect.centerx
        textpos.x = self.rect.x + 40
        textpos.centery += centry_offset
        self.surf.blit(text, textpos)

        last_y, line_width, border_pad, border_margin  = textpos.centery, 1, 5, self.boder_margin
        width, height = self.width - border_margin * 2, height
        inner_width, inner_height = width - border_pad * 2, height - int(textpos.height / 2) - border_pad * 2
        inner_topx, inner_topy = border_margin + border_pad, textpos.y + int(textpos.height) + border_pad

        # Draw border
        dots = [[textpos.x - 5, last_y], [border_margin, last_y], [border_margin, height + last_y],
                [self.width - border_margin, height + last_y], [self.width - border_margin, last_y], [textpos.x + textpos.width + 5, last_y]]
        pg.draw.lines(self.surf, Color.WHITE, False, dots, line_width)

        return inner_topx, inner_topy, inner_width, inner_height
    
    def _statis_info_box(self, centry_offset):
        # Set title
        height = int(self.height * 0.3)
        topx, topy, width, height = self._set_title(content='Learning curve', font_size=30, centry_offset=centry_offset, height=height)
        dpi = 40
        figsize = [width / dpi, height / dpi]

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
        sub_pos.centery = topy + int(height / 2)
        self.statis_pos = sub_pos
        self.surf.blit(self.statis, sub_pos)

        return sub_pos.y + height
    
    def _add_widgets(self, centry_offset: int):
        BUTTON_STYLE = {
            "hover_color" : Color.HOVERED,
            "clicked_color" : Color.CLICKED,
        }
        button_text = 'TRANINIG PAUSE'
        self.btn_goup = None # will contain more buttons

        def button_trigger():
            print('[INFO] You cliked me! TRAINING PAUSE')
        
        def input_trigger():
            print('[INFO] Focus on input')
        
        # Register train control
        margin_btn = 10
        capable_x = self.width - self.boder_margin * 2
        btn_width, btn_height = (capable_x - margin_btn * 2) / 3, int(self.height * 0.08)
        self.btn_train_control = Button(rect=(0, 0, btn_width, btn_height), color=Color.INFO, trigger=button_trigger, 
                                    text='TRAIN / PAUSE', **BUTTON_STYLE)
        self.btn_train_control.rect.center = (self.boder_margin + int(btn_width / 2), centry_offset + int(btn_height / 2))
        self.btn_train_control.update(self.surf)

        # Register stats control
        self.btn_stat_control = Button(rect=(0, 0, btn_width, btn_height), color=Color.INFO, trigger=button_trigger, 
                                    text='FLUSH CURVE', **BUTTON_STYLE)
        self.btn_stat_control.rect.center = (self.boder_margin + margin_btn + int(btn_width * 3 / 2), centry_offset + int(btn_height / 2))
        self.btn_stat_control.update(self.surf)

        # Register agent id selector
        self.id_selector = InputText(rect=(0, 0, btn_width, btn_height), color=Color.WHITE, trigger=input_trigger, placeholder='input ...')
        self.id_selector.rect.center = (self.boder_margin + margin_btn * 2 + int(btn_width * 5 / 2), centry_offset + int(btn_height / 2))
        self.id_selector.update(self.surf)

        return centry_offset + btn_height

    def _local_view(self, centry_offset: int, agent_id=None):
        # Set title
        height = int(self.height * 0.35)
        topx, topy, width, height = self._set_title(content='Attention View', font_size=30, centry_offset=centry_offset, height=height)
        centery = topy + int(height / 2)
        radius = int(height / 2)

        # Draw local circle
        pg.draw.circle(self.surf, Color.WHITE, [self.rect.centerx, centery], radius, radius)
        pg.draw.circle(self.surf, Color.BLACK, [self.rect.centerx, centery], radius + 2, 2)
        return None
    
    def load_everything(self):
        self._custom_ui()
    
    def listen_widgets_event(self, event):
        self.btn_train_control.check_event(event)
        self.btn_stat_control.check_event(event)
        self.id_selector.check_event(event)
    
    def flush_statis(self):
        pass
    
    def update(self):
        self.btn_train_control.update(self.surf)
        self.btn_stat_control.update(self.surf)
        self.id_selector.update(self.surf)
