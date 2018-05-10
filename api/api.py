import numpy as np
import tensorflow as tf
from env.magent import GridWorld

from api.senario import generate_simple_gw
from api.meta import StateList


class Resolution(object):
    def __init__(self, in_range, out_range):
        self.in_range = in_range
        self.out_range = out_range

        assert in_range['x'][1] > 0

    def __call__(self, data):
        for i in range(len(data)):
            data[i][:, 0] = data[i][:, 0] * self.in_range['x'][1] / self.out_range['x'][1]
            data[i][:, 1] = data[i][:, 1] * self.in_range['y'][1] / self.out_range['y'][1]
        return data


class Env(object):
    def __init__(self, name, in_range, map_size=100, max_steps=300):
        self.env = GridWorld(name, map_size=map_size)
        self.handles = None
        self.done = False
        self._rewards = [[], []]
        self.n_group = 0
        self.map_size = map_size
        self.max_steps = max_steps
        self.steps = 0
        self.resolution = Resolution(in_range, out_range={'x': [0, map_size], 'y': [0, map_size]})
        self._virtual_run()

    def _virtual_run(self):
        self.env.reset()
        self.handles = self.env.get_handles()
        self.n_group = len(self.handles)

        generate_simple_gw(self.env, self.map_size, self.handles)
        self.agent_num = [self.env.get_num(self.handles[i]) for i in range(self.n_group)]

        for i in range(self.n_group):
            self._rewards[i].append(sum(self.env.get_reward(self.handles[i])))

    def start(self):
        self.env.reset()
        self.handles = self.env.get_handles()
        generate_simple_gw(self.env, self.map_size, self.handles)

    def get_obs(self):
        """Return a list of observation whose length must be euqal to `self.n_group`
        """

        obs = [self.env.get_observation(self.handles[i]) for i in range(self.n_group)]
        return obs
    
    def get_neighbor(self):
        """Neighbor includes feature vector (or message of local agents)
        """
        return [self.env.get_neighbors(self.handles[i]) for i in range(self.n_group)]

    def get_num(self):
        nums = [self.env.get_num(self.handles[i]) for i in range(self.n_group)]
        return nums

    def get_rewards(self):
        return self._rewards

    def get_states(self, actions=None):
        """Accept actions list, then step a stage, return a list contains
        ids, alive and position, and if an agent is not alive, you need remove
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
        if actions is not None:
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
        for i in range(self.n_group):
            self._rewards[i].append(self._rewards[i][-1] + sum(self.env.get_reward(self.handles[i])))
        self.env.clear_dead()

        pos = self.resolution(pos)

        result = [StateList(list(zip(ids[i], alive[i], pos[i]))) for i in range(self.n_group)]
        return result


class ModelGroup(object):
    def __init__(self, sub_models: list, env: Env, names: list):
        self.n_models = len(sub_models)
        self.models = []
        sess = tf.Session()

        for i in range(self.n_models):
            with tf.variable_scope('agent_{}_{}'.format(names[i], i)):
                global_scope = tf.get_variable_scope().name
                obs_shape = env.env.get_view_space(env.handles[i])
                feat_shape = env.env.get_feature_space(env.handles[i])
                act_n = env.env.get_action_space(env.handles[i])[0]
                self.models.append(sub_models[i](obs_shape, feat_shape, act_n, None, global_scope, sess=sess))

        sess.run(tf.global_variables_initializer())
        for i in range(self.n_models):
            self.models[i].initialize()

    def act(self, **kwargs):
        """Obs is necessary, then this method will return a list whose
        length must be equal to `self.n_models`
        """
        actions = []
        for i in range(self.n_models):
            action = self.models[i].act(ids=kwargs['ids'][i], obs=kwargs['obs'][i][0], feat=kwargs['obs'][i][1], neighbor=kwargs['neighbor'][i], eps=0.05)
            actions.append(action)
        return actions

    def load(self, dirs, epochs):
        for i in range(2):
            self.models[i].load(dirs[i], epochs[i])
