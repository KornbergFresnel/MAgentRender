import os
import tensorflow as tf
import tensorflow.contrib as tc


os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'


class Model(object):
    def __init__(self, name):
        self.name = name

    @property
    def vars(self):
        return tf.get_collection(tf.GraphKeys.GLOBAL_VARIABLES, scope=self.name)

    @property
    def trainable_vars(self):
        return tf.get_collection(tf.GraphKeys.TRAINABLE_VARIABLES, scope=self.name)

    @property
    def perturbable_vars(self):
        return [var for var in self.trainable_vars if "LayerNorm" not in var.name]


class QNet(Model):
    def __init__(self, name="Q-Net", layer_norm=True):
        super().__init__(name=name)
        self.layer_norm = layer_norm

    def __call__(self, obs, act_n, reuse=False, use_dueling=False):
        with tf.variable_scope(self.name) as scope:
            self.name = tf.get_variable_scope().name

            if reuse:
                scope.reuse_variables()

            x = tf.layers.dense(obs, units=64, name='Obs-emb')

            if self.layer_norm:
                x = tc.layers.layer_norm(x, center=True, scale=True)
            x = tf.nn.relu(x)

            x = tf.layers.dense(x, units=64)
            if self.layer_norm:
                x = tc.layers.layer_norm(x, center=True, scale=True)
            x = tf.nn.relu(x)

            x = tf.layers.dense(x, units=act_n, kernel_initializer=tf.random_uniform_initializer(minval=-1e-3, maxval=1e-3))
            x = tf.nn.tanh(x)

        return x