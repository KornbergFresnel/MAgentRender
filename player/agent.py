from pygame.sprite import Sprite
from pygame.sprite import Group


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

    def update_state(self, state):
        self.rect.move_ip(state[2][0], state[2][1])

    def update(self):
        self.rect.move_ip(self.dir_x, self.dir_y)


class AgentGroup(Group):
    def __init__(self, agent_num: int, stats: dict, color: tuple, w: int, h: int, x_min: int, x_max: int, y_min: int, y_max: int):
        self.n_agent = agent_num
        self.inner_agent = {}
        for i in range(agent_num):
            self.inner_agent[i] = Agent(i, color, pos, w, h, x_min, x_max, y_min, y_max)
            self.add(Agent(self.inner_agent[i])

    def update_states(self, states):
        """States: id, alive, position
        """

        assert len(states) == self.n_agent
        for i in range(self.n_agent):
            if states[i][1] == False:
                self.remove(self.inner_agent[i])
            else:
                self.inner_agent[i].update_state(states[i])
