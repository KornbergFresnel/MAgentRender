import numpy as np
from env.python.magent import GridWorld
from test.senario import generate_simple_gw
from meta import StateList


class Resolution(object):
    def __init__(self, in_range, out_range):
        self.in_range = in_range
        self.out_range = out_range

        assert in_range['x'][1] > 0
        self.resolution = out_range['x'][1] / in_range['x'][1]

    def refactory(self, data: np.ndarray):
        return data *= self.resolution


class Env(object):
    def __init__(self, name, in_range, map_size=110, max_steps=300):
        self.env = GridWorld('battle', map_size=map_size)
        self.n_group = 0
        self.map_size = map_size
        self.max_steps = max_steps
        self.resolution = Resolution(in_range, out_range={'x': [0, 110], 'y': [0, 110]})
        self._virtual_run()

    def _virtual_run(self):
        self.env.reset()
        self.handles = self.env.get_handles()
        self.n_group = len(self.handles)

        generate_simple_gw(self.env, self.map_size, self.handles)
        self.agent_num = [self.env.get_num(self.handles[i]) for i in range(self.n_group)]

    def start(self):
        self.env.reset()
        self.handles = self.env.get_handles()
        generate_simple_gw(self.env, self.map_size, self.handles)

    def get_obs(self):
        """Return a list of observation whose length must be euqal to `self.n_group`
        """

        obs = [self.env.get_observation(self.handles[i]) for i in range(self.n_group)]
        return obs

    def get_states(self, actions):
        """Accept actions list, then step a stage, return a list contains
        ids, alives and position, and if an agent is not alive, you need remove
        it from the render or map

        Parameters
        ----------
        actions: list
            actions list for n_group agents

        Returns
        -------
        result: list
            the structure of elements a tuple likes (id, alive, position), and
            position is also a tuple likes (x, y)
        """

        if self.done:
            return None

        for i in range(self.n_group):
            self.env.set_action(self.handles[i], actions[i])

        self.steps += 1
        self.done = self.env.step() or self.steps >= self.max_steps

        # collection rewards or not
        # collect alives
        ids = [self.env.get_agent_id(self.handles[i]) for i in range(self.n_group)]
        alive = [self.env.get_alive(self.handles[i]) for i in range(self.n_group)]

        # pos at here you can make resolution
        pos = [self.env.get_pos(self.handles[i]) for i in range(self.n_group)]
        pos = self.resolution.refactory(np.array(pos))

        result = list(zip(ids, alive, pos))
        return StateList(result)


class ModelGroup(object):
    def __init__(self, sub_models: list, env: Env):
        self.n_models = len(sub_models)
        self.models = []
        for i in range(self.n_models):
            obs_shape = env.env.get_view_space(env.handles[i])
            feat_shape = env.env.get_feature_space(env.handles[i])
            act_n = env.env.get_action_space(env.handles[i])[0]
            self.models.append(sub_models[i](obs_shape, feat_shape, 'agent_{}'.format(i), act_n))

    def act(self, **kwargs):
        """Obs is necessary, then this method will return a list whose
        length must be equal to `self.n_models`
        """
        actions = []
        for i in range(self.n_models):
            actions.append(self.models[i].act(obs=kwargs['obs'][i][0], feat=kwargs['obs'][i][1], eps=0.1))
        return actions
