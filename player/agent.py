import pygame as pg

from pygame.sprite import Sprite
from pygame.sprite import Group
from test.meta import State, StateList


class Agent(Sprite):
    def __init__(self, agent_id, color, fake_center, pos, w, h, x_min, x_max, y_min, y_max):
        super().__init__()
        self.agent_id = agent_id
        self.image = pg.Surface((w, h))
        self.image.fill(color)
        self.fake_center = fake_center
        self.w, self.h = w, h
        self.rect = self.image.get_rect(center=(int(pos[0] + w / 2), int(pos[1] + h / 2)))
        self.x_min, self.x_max, self.y_min, self.y_max = x_min, x_max, y_min, y_max

    def update_state(self, state: State):
        self.rect.centerx = int(state.position[0] + self.w / 2)
        self.rect.centery = int(state.position[1] + self.h / 2)


class AgentGroup(Group):
    def __init__(self, fake_center: tuple, agent_num: int, stats: StateList, color: tuple, w: int, h: int, x_min: int,
                 x_max: int, y_min: int, y_max: int):
        super().__init__()
        self.n_agent = agent_num
        self._agent = {}

        for i in range(agent_num):
            self._agent[stats[i].id] = Agent(stats[i].id, color, fake_center, stats[i].position, w, h, x_min, x_max,
                                             y_min, y_max)
            self.add(self._agent[stats[i].id])

    def update_states(self, states: StateList):
        """States: id, alive, position
        """

        assert len(states) == self.n_agent

        for i in range(self.n_agent):
            if not states[i].alive and states[i].id in self._agent.keys():
                self.remove(self._agent[states[i].id])
                self._agent.pop(states[i].id)
                self.n_agent -= 1
            elif states[i].alive and states[i].id in self._agent.keys():
                self._agent[states[i].id].update_state(states[i])

