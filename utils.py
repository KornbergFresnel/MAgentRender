import pygame as pg


def draw_rect(surface: pg.Surface, color: tuple, top: tuple, w: int, h: int):
    top = tuple(map(round, top))
    pg.draw.rect(surface, color, top w, h)
