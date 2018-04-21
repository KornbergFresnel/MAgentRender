import pygame as pg


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
