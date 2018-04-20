import os.path as osp


BASE_DIR = osp.dirname(osp.abspath(__file__))
GLOBAL_SCALE = 0.6
MAIN_BG_COLOR = (255, 255, 255)
PLAYER_BG_COLOR = (255, 255, 255)
CONTROL_BG_COLOR = (0, 42, 56)
SPLIT_ETA = 0.7  # split main window for player and control panel


class Color:
    BLACK = (0, 0, 0)
    WHITE = (255, 255, 255)
    AGENT = (94, 156, 198)
