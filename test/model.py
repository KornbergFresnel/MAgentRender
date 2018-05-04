import os
import random
import numpy as np
import tensorflow as tf

from test.utils import nature_cnn, fc, get_target_updates
from test.base import QNet


class CNNEmbedding(object):
    def __call__(self, obs_input, feat_input, fake_name="", reuse=False):
        with tf.variable_scope(fake_name + "embedding", reuse=reuse):
            h_obs = nature_cnn(obs_input)
            h_feat = fc(feat_input, 'feat', 64, init_scale=0.01)
            return tf.concat([h_obs, h_feat], axis=1)


class DQN(object):
    def __init__(self, obs_shape, feat_shape, global_scope, act_n, memory=None, action_noise=None, learning_rate=1e-4,
                 gamma=0.995, tau=0.001, update_every=5, use_dueling=False):
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
        self._setup_q()
        self._setup_optimizer()

        self._initialize()

    def _setup_update_target(self):
        q_init_updates, q_soft_updates = get_target_updates(self.q.vars, self.target_q.vars, self.tau)
        self.target_init_updates = [q_init_updates]
        self.target_soft_updates = [q_soft_updates]

    def _setup_q(self):
        self.target_q_input = tf.placeholder(tf.float32, shape=(None,))
        self.agent_num = tf.placeholder(tf.int32, shape=(None,))

        # act_idx = tf.argmax(self.q_tf, axis=1, output_type=tf.int32)
        # target_q = self.target_q_tf[self.agent_num, act_idx]
        # self.get_target_q = self.rewards + (1. - self.terminates) * target_q

        # arg max q
        self.arg_max_q = tf.argmax(self.q_tf, axis=1, output_type=tf.int32)

    def _initialize(self):
        # Initialize tf.Session
        sess_config = tf.ConfigProto(allow_soft_placement=True, log_device_placement=False)
        sess_config.gpu_options.allow_growth = True
        self.sess = tf.Session(config=sess_config)
        self.sess.run(tf.global_variables_initializer())
        self.sess.run(self.target_init_updates)

    def _setup_optimizer(self):
        self.loss = tf.reduce_sum(tf.square(self.target_q_input - self.q_tf) * self.mask) / tf.reduce_sum(self.mask)
        self.train_op = tf.train.AdamOptimizer(self.lr).minimize(self.loss)

    def act(self, **kwargs):
        num = len(kwargs['obs'])
        if random.random() < kwargs['eps']:
            return np.random.choice(self.act_n, num).astype(dtype=np.int32)
        else:
            action = self.sess.run(self.arg_max_q, feed_dict={
                self.obs_input: kwargs['obs'],
                self.feat_input: kwargs['feat'],
            })

            return action

    def store_transition(self, **kwargs):
        self.memory.append(**kwargs)

    def update_target(self):
        self.sess.run(self.target_soft_updates)

    def save(self, model_dir, step):
        model_vars = tf.get_collection(tf.GraphKeys.GLOBAL_VARIABLES, self.global_scope)
        saver = tf.train.Saver(model_vars)
        save_path = saver.save(self.sess, os.path.join(model_dir, self.path_format(self.name, step)))
        # print(Color.INFO.format('[INFO] Saved model at:' + save_path))

    def load(self, model_dir, step):
        save_path = os.path.join(model_dir, self.path_format(self.name, step))
        try:
            model_vars = tf.get_collection(tf.GraphKeys.GLOBAL_VARIABLES, self.global_scope)
            saver = tf.train.Saver(model_vars)
            saver.restore(self.sess, save_path)
            # print(Color.INFO.format('[INFO] Loaded model from: ' + save_path))
        except Exception as e:
            pass
            # print(Color.ERROR.format('[ERROR] Loaded failed, please checkt `{}` exists'.format(save_path)))
