import tensorflow as tf
import numpy as np
import os

from utils import nature_cnn
from base import QNet, 
from lib.common.utils import Color
from lib.senario.battle import play, generate_simple_gw


class CNNEmbedding(object):
    def __call__(self, obs_input, feat_input, fake_name="", reuse=False):
        with tf.variable_scope(fake_name + "embedding", reuse=reuse):
            h_obs = nature_cnn(obs_input)
            h_feat = fc(feat_input, 'feat', 64, init_scale=0.01)
            return tf.concat([h_obs, h_feat], axis=1)


class DQN(object):
    def __init__(self, obs_shape, feat_shape, global_scope, act_n, memory=None, action_noise=None, learning_rate=1e-4, gamma=0.995, use_eps=True, q_learning_rate=1e-4,
                 v_learning_rate=1e-4, u_learning_rate=1e-4, tau=0.001, update_every=5, use_dueling=False, use_graident_clip=False):
        super().__init__()
        # Inputs
        self.obs_input = tf.placeholder(tf.float32, shape=(None,) + obs_shape, name='Focus-View-Input')
        self.feat_input = tf.placeholder(tf.float32, shape=(None,) + feat_shape, name='Focus-Feat-Input')
        self.mask = tf.placeholder(tf.float32, shape=(None,), name='Terminate-Mask')
        self.rewards = tf.placeholder(tf.float32, shape=(None,), name='Rewards')
        self.terminates = tf.placeholder(tf.float32, shape=(None,), name='Terminates')

        # Parameters
        self.name = 'DQN'
        self.act_n = act_n
        self.gamma = gamma
        self.lr = learning_rate
        self.memory = memory
        self.action_noise = action_noise
        self.tau = tau
        self.normalize_returns = False
        self.enable_popart = False
        self.train_ct = 0
        self.path_format = '{}_{}'.format  # format: name, step
        self.global_scope = global_scope
        self.update_every = update_every

        # Create Emb layer
        emb_layer = CNNEmbedding()
        emb_layer = emb_layer(self.obs_input, self.feat_input)

        # Define q-net and target-net
        self.q = QNet()
        self.q_tf = self.q(obs=emb_layer, act_n=self.act_n, use_dueling=use_dueling)
        self.target_q = QNet(name='Target-Q-Net')
        self.target_q_tf = self.target_q(obs=emb_layer, act_n=self.act_n)

        # Set up
        self._setup_update_target()
        self.global_vars_dict = {}
        self._setup_optimizer()

        self._initialize()

    def _setup_update_target(self):
        q_init_updates, q_soft_updates = get_target_updates(self.q_net.vars, self.target_q.vars, self.tau)
        self.target_init_updates = [q_init_updates]
        self.target_soft_updates = [q_soft_updates]

    def _setup_target_q(self):
        self.target_q_input = tf.placeholder(tf.float32, shape=(None,))
        self.agent_num = tf.placeholder(tf.int32, shape=(None,))

        act_idx = tf.argmax(self.q_tf, axis=1)
        target_q = self.target_q_tf[self.agent_num, act_idx]
        self.get_target_q = self.rewards + (1. - self.terminates) * target_q

    def _setup_popart(self):
        """Normalize output, make q-learning robust (if `self.ret_rms` exists and not None)

        see [ArtPop](https://arxiv.org/pdf/1602.07714.pdf) for details
        """
        assert hasattr(self, 'ret_rms') and self.ret_rms is not None
        # TODO: implement the logic of pop-art

    def _initialize(self):
        # Initialize tf.Session
        sess_config = tf.ConfigProto(allow_soft_placement=True, log_device_placement=False)
        sess_config.gpu_options.allow_growth = True
        self.sess = tf.Session(config=sess_config)
        self.sess.run(tf.global_variables_initializer())
        self.sess.run(self.target_init_updates)

    def _setup_optimizer(self):
        self.loss = tf.reduce_sum(tf.square(self.target_q_input - self.q_tf) * self.mask) / tf.reduce_sum(self.mask)

        if self.use_graident_clip:
            pass
        else:
            self.train_op = tf.train.AdamOptimizer(self.lr).minimize(self.loss)

    def act(self, **kwargs):
        action = self.sess.run(self.action_exe, feed_dict={
            self.obs_input: kwargs['obs'],
            self.feat_input: kwargs['feat'],
            self.eps: kwargs['eps']
        })

        return action

    def store_transition(self, **kwargs):
        self.memory.append(**kwargs)

    def update_target(self):
        self.sess.run(self.target_soft_updates)

    def get_var_dict(self):
        var_dict = {}
        for k in self.global_vars_dict.keys():
            var_dict[k] = self.sess.run(self.global_vars_dict[k])
        return var_dict

    def self_play_update(self, v_name, value):
        my_value = self.sess.run(self.global_vars_dict[v_name])
        self.sess.run(tf.assign(self.global_vars_dict[v_name], self.tau * my_value + (1. - self.tau) * value))

    def train(self):
        # Get a batch
        batch = self.memory.sample()
        assert batch is not None

        target_Q = self.sess.run(self.get_target_q, feed_dict={
            self.obs_input: batch['next_obs'],
            self.feat_input: batch['next_feat'],
            self.rewards: batch['rewards'].reshape(-1),
            self.terminates: batch['terminals'].reshape(-1).astype(dtype=np.float32),
            self.agent_num: np.arange(len(batch['next_feat']))
        })

        loss, _ = self.sess.run([self.loss, self.train_op], feed_dict={
            self.obs_input: batch['obs'],
            self.feat_input: batch['feat'],
            self.act_input: batch['act'].reshape(-1),
            self.target_q_input: target_Q,
            self.mask: batch['mask'].reshape(-1).astype(dtype=np.float32)
        })

        if (self.train_ct + 1) % self.update_every == 0:
            self.update_target()

        self.train_ct += 1
        return loss

    def save(self, model_dir, step):
        model_vars = tf.get_collection(tf.GraphKeys.GLOBAL_VARIABLES, self.global_scope)
        saver = tf.train.Saver(model_vars)
        save_path = saver.save(self.sess, os.path.join(model_dir, self.path_format(self.name, step)))
        print(Color.INFO.format('[INFO] Saved model at:' + save_path))

    def load(self, model_dir, step):
        save_path = os.path.join(model_dir, self.path_format(self.name, step))
        try:
            model_vars = tf.get_collection(tf.GraphKeys.GLOBAL_VARIABLES, self.global_scope)
            saver = tf.train.Saver(model_vars)
            saver.restore(self.sess, save_path)
            print(Color.INFO.format('[INFO] Loaded model from: ' + save_path))
        except Exception as e:
            print(Color.ERROR.format('[ERROR] Loaded failed, please checkt `{}` exists'.format(save_path)))


class Runner(object):
    def __init__(self, *, env, handles, map_size, max_steps, render_every, eval_every, models, use_parallel=False):
        self.env = env
        self.models = models
        self.max_steps = max_steps
        self.handles = handles
        self.map_size = map_size
        self.render_every = render_every
        self.eval_every = eval_every
        self.use_parallel = use_parallel

    def run(self, variant_eps, iteration, model_dir):
        mode = "render"

        info = play(ct=iteration, env=self.env, handles=self.handles, map_size=self.map_size, models=self.models,
                    max_steps=self.max_steps, train=True, render=False if self.render_every == 0 else iteration % self.render_every == 0,
                    eps=variant_eps, print_every=50, mode=mode, use_parallel=self.use_parallel)
        return info


def learn(env, max_steps=400, map_size=40, render_every=5, lr=1e-4, n_updates=200, gamma=0.99, batch_size=16,
          memory_limit=2**4, save_interval=0, sf_update_every=0, use_parallel=False):

    handles = env.get_handles()
    obs_shape = [env.get_view_space(handles[i]) for i in range(len(handles))]
    feat_shape = [env.get_feature_space(handles[i]) for i in range(len(handles))]
    act_n = [env.get_action_space(handles[i])[0] for i in range(len(handles))]
    models = []

    save_dir = os.path.join(config.MODEL_DIR, 'FDQ')
    n_group = len(handles)

    # try to get max_num
    env.reset()
    generate_simple_gw(env, map_size, handles)
    max_num = [env.get_num(handles[i]) for i in range(n_group)]

    for i in range(n_group):
        with tf.variable_scope('agent_{}'.format(i)):
            ids = list(range(max_num[i]))
            memory = AgentMemory(ids, obs_shape[i], feat_shape[i], memory_limit, batch_size)
            models.append(DQN(obs_shape=obs_shape[i], feat_shape=feat_shape[i], act_n=act_n[i], memory=memory, global_scope=tf.get_variable_scope().name))

    summary = SummaryObj(log_name="dqn_battle")
    summary.register(["Sum_Reward", "Kill_Sum", "Mean_Reward"])  # summary register
    runner = Runner(env=env, handles=handles, map_size=map_size, max_steps=max_steps, render_every=render_every,
                    eval_every=10, models=models, use_parallel=use_parallel)

    for iteration in range(1, n_updates + 1):
        eps = piecewise_decay(iteration, [0, 200, 1500], [1.0, 0.5, 0.1])
        statis_info = runner.run(eps, iteration, save_dir)
        # TODO: collect stats info
        # summary.write(statis_info)
        batch_num = models[0].memory.get_batch_num()
        print('\n[INFO] --- #{} round training ---'.format(iteration))
        print('\n[INFO] batch-num:', batch_num)
        loss = 0.0
        for i in range(batch_num):
            temp_loss = models[0].train()

            if i % 5 == 0:
                print('[INFO] batch-{} loss: {}'.format(i, temp_loss))
            loss += temp_loss
        print('[INFO] mean-loss:', np.round(loss / batch_num, 6))

    del env
