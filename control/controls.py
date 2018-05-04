import pygame as pg
import numpy as np
from pygame.locals import *
from numpy.random import randint
from pygame.sprite import Sprite
from config import Color, GLOBAL_SCALE
from widgets.button import Button
from widgets.statis import StatisPanel
from widgets.textinput import InputText
from widgets.attention import Attention


class ControlPanel(Sprite):
    def __init__(self, pos, control_area: tuple, bg_color: tuple, init_points: list):
        super().__init__()
        self.surf = pg.Surface(control_area)
        self.surf.fill(bg_color)
        self.rect = self.surf.get_rect(center=(pos[0] + int(control_area[0] / 2), pos[1] + int(control_area[1] / 2)))
        self.image = self.surf
        self.width, self.height = control_area
        self.relate_center = [self.rect.centerx - self.rect.x, self.rect.centery - self.rect.y]
        self.relate_top = [0, 0]
        self.boder_margin = int(self.width * 0.03)
        self.bg_color = bg_color
        self.centry_set = {}
        self._init_points = init_points
        self.group = pg.sprite.Group()

    def _custom_ui(self):
        # Display some text at center
        font = pg.font.Font(None, int(45 * GLOBAL_SCALE))
        text = font.render('CONTROL PANEL', 1, (255, 255, 255))
        textpos = text.get_rect(center=(self.relate_center[0], int(self.height * 0.04)))
        self.surf.blit(text, textpos)

        last_y = textpos.y + textpos.height
        margin = int(self.height * 0.02)
        # Draw logo
        last_y = self._draw_logo(centry_offset=last_y + margin)
        self.centry_set['statis_centry'] = last_y + margin
        last_y = self._statis_info_box(centry_offset=last_y + margin)
        self.centry_set['widgets_centry'] = last_y + margin
        last_y = self._add_widgets(centry_offset=last_y + margin)
        self.centry_set['local_view_centry'] = last_y + margin
        self._local_view(centry_offset=last_y + margin)
    
    def _draw_logo(self, centry_offset: int):
        last_y, line_width, margin = centry_offset, 3, 4
        y_step = line_width + margin
        border_margin = self.boder_margin
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
        textpos.x = self.relate_top[0] + int(self.width * 0.1)
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
        topx, topy, width, height = self._set_title(content='Learning curve', font_size=int(40 * GLOBAL_SCALE), centry_offset=centry_offset, height=height)
        self.group.add(StatisPanel(pos=(topx, topy), width=width, height=height, dpi=40, bg_color=self.bg_color, init_points=self._init_points))
        return topy + height
    
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
        btn_width, btn_height = (capable_x - margin_btn * 2) / 3, int(self.height * 0.05)
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
        height = self.height - centry_offset - int(self.height * 0.04)
        topx, topy, width, height = self._set_title(content='Attention View', font_size=int(40 * GLOBAL_SCALE),
                                                    centry_offset=centry_offset, height=height)
        centery = topy + int(height / 2)
        print('[INFO] ', width, height)
        self.group.add(Attention((self.relate_center[0], centery), width, height, self.bg_color))
        return None
    
    def load_everything(self):
        self._custom_ui()
    
    def listen_widgets_event(self, event):
        self.btn_train_control.check_event(event)
        self.btn_stat_control.check_event(event)
        self.id_selector.check_event(event)     
    
    def update(self, *args):
        self.group.draw(self.surf)
        self.group.update(args[1])
        self.btn_train_control.update(self.surf)
        self.btn_stat_control.update(self.surf)
        self.id_selector.update(self.surf)
