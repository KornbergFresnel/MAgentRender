import os
import numpy as np
import tensorflow as tf


class Net:
    def __init__(self, obs_shape, feat_shape, global_scope, act_n,
                 batch_size=64, learning_rate=1e-4, reward_decay=0.99,
                 train_freq=1, target_update=2000, memory_size=2 ** 20, eval_obs=None,
                 use_dueling=True, use_double=True, use_conv=True,
                 num_gpu=1, infer_batch_size=8192, network_type=0):
        self.name = global_scope
        self.subclass_name = "tfdqn_0"
        self.view_space = obs_shape
        # self.view_space = (13, 13, 7)
        self.feature_space = feat_shape
        # self.feature_space = (34,)
        self.num_actions = act_n
        # self.num_actions = 21

        self.batch_size = batch_size
        self.learning_rate = learning_rate
        self.train_freq = train_freq  # train time of every sample (s,a,r,s')
        self.target_update = target_update  # target network update frequency
        self.eval_obs = eval_obs
        self.infer_batch_size = infer_batch_size  # maximum batch size when infer actions,
        # change this to fit your GPU memory if you meet a OOM

        self.use_dueling = use_dueling
        self.use_double = use_double
        self.num_gpu = num_gpu
        self.network_type = network_type

        self.train_ct = 0

        # ======================= build network =======================
        # input place holder
        self.target = tf.placeholder(tf.float32, [None])
        self.weight = tf.placeholder(tf.float32, [None])

        self.input_view = tf.placeholder(tf.float32, (None,) + self.view_space)
        self.input_feature = tf.placeholder(tf.float32, (None,) + self.feature_space)
        self.action = tf.placeholder(tf.int32, [None])
        self.mask = tf.placeholder(tf.float32, [None])
        self.eps = tf.placeholder(tf.float32)  # e-greedy

        # build graph
        with tf.variable_scope(self.name):
            with tf.variable_scope("eval_net_scope"):
                self.eval_scope_name = tf.get_variable_scope().name
                self.qvalues = self._create_network(self.input_view, self.input_feature, use_conv)

            if self.num_gpu > 1:  # build inference graph for multiple gpus
                self._build_multi_gpu_infer(self.num_gpu)

            with tf.variable_scope("target_net_scope"):
                self.target_scope_name = tf.get_variable_scope().name
                self.target_qvalues = self._create_network(self.input_view, self.input_feature, use_conv)

        # loss
        self.gamma = reward_decay
        self.actions_onehot = tf.one_hot(self.action, self.num_actions)
        td_error = tf.square(self.target - tf.reduce_sum(tf.multiply(self.actions_onehot, self.qvalues), axis=1))
        self.loss = tf.reduce_sum(td_error * self.mask) / tf.reduce_sum(self.mask)

        # train op (clip gradient)
        optimizer = tf.train.AdamOptimizer(learning_rate=learning_rate)
        gradients, variables = zip(*optimizer.compute_gradients(self.loss))
        gradients, _ = tf.clip_by_global_norm(gradients, 5.0)
        self.train_op = optimizer.apply_gradients(zip(gradients, variables))

        # output action
        def out_action(qvalues):
            best_action = tf.argmax(qvalues, axis=1)
            best_action = tf.to_int32(best_action)
            random_action = tf.random_uniform(tf.shape(best_action), 0, self.num_actions, tf.int32)
            should_explore = tf.random_uniform(tf.shape(best_action), 0, 1) < self.eps
            return tf.where(should_explore, random_action, best_action)

        self.output_action = out_action(self.qvalues)
        if self.num_gpu > 1:
            self.infer_out_action = [out_action(qvalue) for qvalue in self.infer_qvalues]

        # target network update op
        self.update_target_op = []
        t_params = tf.get_collection(tf.GraphKeys.GLOBAL_VARIABLES, self.target_scope_name)
        e_params = tf.get_collection(tf.GraphKeys.GLOBAL_VARIABLES, self.eval_scope_name)
        for i in range(len(t_params)):
            self.update_target_op.append(tf.assign(t_params[i], e_params[i]))

        # init tensorflow session
        config = tf.ConfigProto(allow_soft_placement=True, log_device_placement=False)
        config.gpu_options.allow_growth = True
        self.sess = tf.Session(config=config)
        self.sess.run(tf.global_variables_initializer())

        # init replay buffers
        self.replay_buf_len = 0
        self.memory_size = memory_size
        # if mask[i] == 0, then the item is used for padding, not for training

    def _create_network(self, input_view, input_feature, use_conv=True, reuse=None):
        """define computation graph of network

        Parameters
        ----------
        input_view: tf.tensor
        input_feature: tf.tensor
            the input tensor
        """
        kernel_num = [32, 32]
        hidden_size = [256]

        if use_conv:  # convolution
            h_conv1 = tf.layers.conv2d(input_view, filters=kernel_num[0], kernel_size=3,
                                       activation=tf.nn.relu, name="conv1", reuse=reuse)
            h_conv2 = tf.layers.conv2d(h_conv1, filters=kernel_num[1], kernel_size=3,
                                       activation=tf.nn.relu, name="conv2", reuse=reuse)
            flatten_view = tf.reshape(h_conv2, [-1, np.prod([v.value for v in h_conv2.shape[1:]])])
            h_view = tf.layers.dense(flatten_view, units=hidden_size[0], activation=tf.nn.relu,
                                     name="dense_view", reuse=reuse)
        else:  # fully connected
            flatten_view = tf.reshape(input_view, [-1, np.prod([v.value for v in input_view.shape[1:]])])
            h_view = tf.layers.dense(flatten_view, units=hidden_size[0], activation=tf.nn.relu)

        h_emb = tf.layers.dense(input_feature, units=hidden_size[0], activation=tf.nn.relu,
                                name="dense_emb", reuse=reuse)

        dense = tf.concat([h_view, h_emb], axis=1)

        if self.use_dueling:
            value = tf.layers.dense(dense, units=1, name="value", reuse=reuse)
            advantage = tf.layers.dense(dense, units=self.num_actions, use_bias=False,
                                        name="advantage", reuse=reuse)

            qvalues = value + advantage - tf.reduce_mean(advantage, axis=1, keep_dims=True)
        else:
            qvalues = tf.layers.dense(dense, units=self.num_actions, name="value", reuse=reuse)

        return qvalues

    def act(self, **kwargs):
        view = kwargs['obs']
        feature = kwargs['feat']
        eps = 0.15

        n = len(view)
        batch_size = min(n, self.infer_batch_size)

        ret = []
        for i in range(0, n, batch_size):
            beg, end = i, i + batch_size
            ret.append(self.sess.run(self.output_action, feed_dict={
                self.input_view: view[beg:end],
                self.input_feature: feature[beg:end],
                self.eps: eps}))
        ret = np.concatenate(ret)
        return ret

    def load(self, dir_name):
        """Fix it, no need to modify. save model to dir

        Parameters
        ----------
        dir_name: str
            name of the directory
        epoch: int
        """
        # if name is None or name == self.name:  # the name of saved model is the same as ours
        path = os.path.join(dir_name, self.subclass_name)
        model_vars = tf.get_collection(tf.GraphKeys.GLOBAL_VARIABLES, self.name)
        saver = tf.train.Saver(model_vars)
        saver.restore(self.sess, path)
