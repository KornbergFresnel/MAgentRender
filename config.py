import os.path as osp


BASE_DIR = osp.dirname(osp.abspath(__file__))
DATA_DIR = osp.join(BASE_DIR, 'data')
GLOBAL_SCALE = 0.9
MAIN_BG_COLOR = (255, 255, 255)
PLAYER_BG_COLOR = (255, 255, 255)
CONTROL_BG_COLOR = (0, 42, 56)
SPLIT_ETA = 0.7  # split main window for player and control panel
FPS = 120
SPEED_MAX = 3
SPEED_MIN = -2
FLUSH_FREQ = 1


class Color:
    BLACK = (0, 0, 0)
    WHITE = (255, 255, 255)
    # AGENT = (94, 156, 198)  # modify to a lambd
    # AGENT = lambda i: [(255, 0, 0), (0, 255, 0)][i]
    AGENT = lambda i: [(int(0.89411764705882357 * 255), int(0.10196078431372549 * 255), int(0.10980392156862745 * 255), 1.0),
                       (int(0.21568627450980393 * 255), int(0.49411764705882355 * 255), int(0.72156862745098038 * 255), 1.0)][i]
    AGENT_B = (0, 0, 0)
    HOVERED = (255, 0, 0)
    CLICKED = (0, 255, 0)
    INFO = (76, 114, 176)
