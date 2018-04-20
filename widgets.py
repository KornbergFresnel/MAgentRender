import pygame as pg


class Button(object):
    def __init__(self, rect: tuple, color: tuple, trigger, **kwargs):
        self.rect = pg.Rect(rect)
        self.color = color
        self.trigger = trigger

        # Flags
        self.clicked = False
        self.hovered = False
        self.hover_text = None
        self.clicked_text = None
        self._parse(kwargs)
        self._render_text()
    
    def _parse(self, kwargs):
        settings = {"text" : None,
                    "font" : pg.font.Font(None,16),
                    "call_on_release" : True,
                    "hover_color" : None,
                    "clicked_color" : None,
                    "font_color" : pg.Color("white"),
                    "hover_font_color" : None,
                    "clicked_font_color" : None,
                    "click_sound" : None,
                    "hover_sound" : None}
        
        for kwarg in kwargs:
            if kwarg in settings:
                settings[kwarg] = kwargs[kwarg]
            else:
                raise AttributeError("Button has no keyword: {}".format(kwarg))
        self.__dict__.update(settings)
    
    def _render_text(self):
        """Pre render the button text."""
        if self.text:
            if self.hover_font_color:
                color = self.hover_font_color
                self.hover_text = self.font.render(self.text,True,color)
            if self.clicked_font_color:
                color = self.clicked_font_color
                self.clicked_text = self.font.render(self.text,True,color)
            self.text = self.font.render(self.text,True,self.font_color)
    
    def check_event(self, event):
        """The button needs to be passed events from your program event loop."""
        if event.type == pg.MOUSEBUTTONDOWN and event.button == 1:
            self.on_click(event)
        elif event.type == pg.MOUSEBUTTONUP and event.button == 1:
            self.on_release(event)
    
    def on_click(self, event):
        if self.rect.collidepoint(event.pos):
            self.clicked = True
            if not self.call_on_release:
                self.trigger()
    
    def on_release(self, event):
        if self.clicked and self.call_on_release:
            self.trigger()
        self.clicked = False
    
    def check_hover(self):
        if self.rect.collidepoint(pg.mouse.get_pos()):
            if not self.hovered:
                self.hovered = True
                if self.hover_sound:
                    self.hover_sound.play()
        else:
            self.hovered = False

    def update(self, surface):
        """Update needs to be called every frame in the main loop."""
        color = self.color
        text = self.text
        self.check_hover()
        if self.clicked and self.clicked_color:
            color = self.clicked_color
            if self.clicked_font_color:
                text = self.clicked_text
        elif self.hovered and self.hover_color:
            color = self.hover_color
            if self.hover_font_color:
                text = self.hover_text
        surface.fill(pg.Color("black"),self.rect)
        surface.fill(color,self.rect.inflate(-4,-4))
        if self.text:
            text_rect = text.get_rect(center=self.rect.center)
            surface.blit(text,text_rect)


class InputText(object):
    def __init__(self, rect: tuple, color: tuple, trigger, **kwargs):
        self.rect = pg.Rect(rect)
        self.color = color
        self.trigger = trigger

        self.focused = False
        self._parse(kwargs)
        self._render_text()

    def _parse(self, kwargs):
        settings = {
            "placeholder" : None,
            "font" : pg.font.Font(None,14),
            "clicked_color" : None,
            "font_color" : pg.Color("gray"),
        }
        
        for kwarg in kwargs:
            if kwarg in settings:
                settings[kwarg] = kwargs[kwarg]
            else:
                raise AttributeError("Button has no keyword: {}".format(kwarg))
        self.__dict__.update(settings)
    
    def _render_text(self):
        """Pre render the button text."""
        self.text = self.font.render(self.placeholder,True,self.font_color)

    def on_focus(self, event):
        if self.rect.collidepoint(event.pos):
            self.focused = True
            self.trigger()

    def check_event(self, event):
        """The button needs to be passed events from your program event loop."""
        if event.type == pg.MOUSEBUTTONDOWN and event.button == 1:
            self.on_focus(event)
            self.text = ''
        if event.type == pg.KEYDOWN:
            if self.focused:
                if event.key == pg.K_RETURN:
                    self.text = ''
                elif event.key == pg.K_BACKSPACE:
                    self.text = self.text[:-1]
                else:
                    self.text += event.unicode

    def update(self, surface):
        """Update needs to be called every frame in the main loop."""
        color = self.color
        text = self.text
        surface.fill(pg.Color("black"),self.rect)
        surface.fill(color,self.rect.inflate(-4,-4))
        if self.text:
            text_rect = text.get_rect(center=self.rect.center)
            surface.blit(text, text_rect)
