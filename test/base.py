import os
import tensorflow as tf
import tensorflow.contrib as tc


os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'


class BaseFrame(object):
    def __init__(self, name, global_scope):
        self.name = name
        self.global_scope = global_scope
        self.path_format = "{}_{}".format

        self.sess = None

    def _initialize(self):
        raise NotImplementedError

    def act(self, **kwargs):
        raise NotImplementedError

    def store_transition(self, **kwargs):
        raise NotImplementedError

    def train(self):
        raise NotImplementedError

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