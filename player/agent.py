from pygame.sprite import Sprite
from pygame.sprite import Group
from test.meta import State, StateList


class Agent(Sprite):
    def __init__(self, agent_id, color, pos, w, h, x_min, x_max, y_min, y_max):
        super().__init__()
        self.agent_id = agent_id
        self.image = pg.Surface((w, h))
        self.image.fill(color)
        self.rect = self.image.get_rect(center=(pos[0] + int(w / 2), pos[1] + int(h / 2)))
        self.x_min, self.x_max, self.y_min, self.y_max = \
            x_min, x_max, y_min, y_max

    def update_state(self, state: State):
        self.rect.move_ip(*state.position)

    def update(self):
        self.rect.move_ip(self.dir_x, self.dir_y)


class AgentGroup(Group):
    def __init__(self, agent_num: int, stats: StateList, color: tuple, w: int, h: int, x_min: int, x_max: int, y_min: int, y_max: int):
        self.n_agent = agent_num
        self._agent = {}

        for i in range(agent_num):
            self._agent[stats[i].id] = Agent(stats[i].id, color, stats[i].position, w, h, x_min, x_max, y_min, y_max)
            self.add(Agent(self.inner_agent[i]))

    def update_states(self, states: StateList):
        """States: id, alive, position
        """

        assert len(states) == self.n_agent
        for i in range(self.n_agent):
            if states[i].alive == False:
                self.remove(self._agent[states[i].id])
                self.n_agent -= 1
            else:
                self._agent[states[i].id].update_state(states[i])
