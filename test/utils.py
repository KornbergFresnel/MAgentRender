import numpy as np
import tensorflow as tf


def ortho_init(scale=1.0):
    def _ortho_init(shape, dtype, partition_info=None):
        # lasagne ortho init for tf
        shape = tuple(shape)
        if len(shape) == 2:
            flat_shape = shape
        elif len(shape) == 4:  # assumes NHWC
            flat_shape = (np.prod(shape[:-1]), shape[-1])
        else:
            raise NotImplementedError
        a = np.random.normal(0.0, 1.0, flat_shape)
        u, _, v = np.linalg.svd(a, full_matrices=False)
        q = u if u.shape == flat_shape else v  # pick the one with the correct shape
        q = q.reshape(shape)
        return (scale * q[:shape[0], :shape[1]]).astype(np.float32)
    return _ortho_init


def conv(x, scope, *, nf, rf, stride, pad='VALID', init_scale=1.0, data_format='NHWC'):
    if data_format == 'NHWC':
        channel_ax = 3
        strides = [1, stride, stride, 1]
        bshape = [1, 1, 1, nf]
    elif data_format == 'NCHW':
        channel_ax = 1
        strides = [1, 1, stride, stride]
        bshape = [1, nf, 1, 1]
    else:
        raise NotImplementedError

    nin = x.get_shape()[channel_ax].value
    wshape = [rf, rf, nin, nf]

    with tf.variable_scope(scope):
        w = tf.get_variable("w", wshape, initializer=ortho_init(init_scale))
        b = tf.get_variable("b", [1, nf, 1, 1], initializer=tf.constant_initializer(0.0))
        if data_format == 'NHWC': b = tf.reshape(b, bshape)
        return b + tf.nn.conv2d(x, w, strides=strides, padding=pad, data_format=data_format)


def fc(x, scope, nh, *, init_scale=1.0, init_bias=0.0):
    with tf.variable_scope(scope):
        nin = x.get_shape()[1].value
        w = tf.get_variable("w", [nin, nh], initializer=ortho_init(init_scale))
        b = tf.get_variable("b", [nh], initializer=tf.constant_initializer(init_bias))
        return tf.matmul(x, w)+b


def conv_to_fc(x):
    nh = np.prod([v.value for v in x.get_shape()[1:]])
    x = tf.reshape(x, [-1, nh])
    return x


def nature_cnn(input_data):
    """
    CNN from Nature paper.
    """
    active = tf.nn.relu

    h = active(conv(input_data, 'c1', nf=32, rf=8, stride=1, init_scale=np.sqrt(2)))
    h2 = active(conv(h, 'c2', nf=64, rf=4, stride=2, init_scale=np.sqrt(2)))
    h3 = active(conv(h2, 'c3', nf=64, rf=2, stride=1, init_scale=np.sqrt(2)))
    h3 = conv_to_fc(h3)
    return active(fc(h3, 'fc1', nh=512, init_scale=np.sqrt(2)))


def get_target_updates(eval_vars, target_vars, tau):
    soft_updates = []
    init_updates = []
    assert len(eval_vars) == len(target_vars)
    for eval_var, target_var in zip(eval_vars, target_vars):
        init_updates.append(tf.assign(target_var, eval_var))
        soft_updates.append(tf.assign(target_var, (1. - tau) * target_var + tau * eval_var))
    assert len(init_updates) == len(eval_vars)
    assert len(soft_updates) == len(eval_vars)

    return tf.group(*init_updates), tf.group(*soft_updates)