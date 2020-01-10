#__author__ = 'wing'
import tensorflow as tf
import numpy as np

class LSTMModel(object):
    def __init__(self):
        input_size = 9
        time_step = 128
        class_num = 6

        parallel_unit_size = 24
        merging_unit_size = 64
        parallel_unit_num = 6
        samples_per_unit = 21
        self.X = tf.placeholder(tf.float32, [None, time_step, input_size])
        self.y = tf.placeholder(tf.float32, [None, class_num])
        self.keep_prob = tf.placeholder(tf.float32)
        self.out = []
        cell = tf.nn.rnn_cell.DropoutWrapper(cell=tf.nn.rnn_cell.GRUCell(num_units=parallel_unit_size), input_keep_prob=1.0, output_keep_prob=self.keep_prob)
        for i in range(parallel_unit_num):
            with tf.variable_scope('LSTM_'+str(i)):
                x_test = self.X[:,i*samples_per_unit:(i+1)*samples_per_unit, :]

                init_state = cell.zero_state(tf.shape(self.X)[0], dtype=tf.float32)
                outputs, states = tf.nn.dynamic_rnn(cell,x_test, initial_state=init_state,time_major=False)
                output = tf.unstack(tf.transpose(outputs,[1,0,2]))
                h_state = output[-1]
                self.out.append(h_state)
        self.state = tf.concat(values=self.out, axis=1)
        self.state = tf.reshape(self.state,shape=[tf.shape(self.X)[0],parallel_unit_num, parallel_unit_size])
        lstm_cell = tf.nn.rnn_cell.DropoutWrapper(cell=tf.nn.rnn_cell.LSTMCell(num_units=merging_unit_size,forget_bias=1.0), input_keep_prob=1.0, output_keep_prob=self.keep_prob)
        init_state = lstm_cell.zero_state(tf.shape(self.state)[0], dtype=tf.float32)
        outputs, states = tf.nn.dynamic_rnn(lstm_cell, self.state, initial_state=init_state, time_major=False)
        output = tf.unstack(tf.transpose(outputs, [1,0,2]))
        h_state = output[-1]

        hidden_size_1 = 64
        hidden_size_2 = 32
        output1 = tf.nn.dropout(self.add_layer(h_state, merging_unit_size, hidden_size_1,activation_function=tf.nn.relu6), keep_prob=self.keep_prob)
        output2 = tf.nn.dropout(self.add_layer(output1, hidden_size_1, hidden_size_2,activation_function=tf.nn.relu6), keep_prob=self.keep_prob)
        self.y_pre = self.add_layer(output2, hidden_size_2, class_num,activation_function=None)

        tv = tf.get_collection("L2_loss")
        regularization_cost = 0.02 * tf.reduce_sum([tf.nn.l2_loss(v) for v in tv])
        self.cross_entropy = tf.reduce_mean(tf.nn.softmax_cross_entropy_with_logits(labels=self.y, logits=self.y_pre))+ regularization_cost
        self.train_op = tf.train.AdamOptimizer(0.001).minimize(self.cross_entropy)
        self.correct_prediction = tf.equal(tf.argmax(tf.nn.softmax(self.y_pre), 1), tf.argmax(self.y, 1))
        self.accuracy = tf.reduce_mean(tf.cast(self.correct_prediction, "float"))

    def add_layer(self, inputs, in_size, out_size, activation_function=None):
        # 添加层功能
        Weights = tf.Variable(tf.random_normal([in_size, out_size], mean=0., stddev=1.))
        tf.add_to_collection("L2_loss",Weights)
        biases = tf.Variable(tf.zeros([1, out_size]) + 0.1)
        wx_plus_b = tf.matmul(inputs, Weights) + biases
        fc_mean, fc_var = tf.nn.moments(wx_plus_b, axes=[0])
        scale = tf.Variable(tf.ones([out_size]))
        shift = tf.Variable(tf.zeros([out_size]))
        epsilon = 0.001
        ema = tf.train.ExponentialMovingAverage(decay=0.5)  # exponential moving average 的 decay 度
        def mean_var_with_update():
            ema_apply_op = ema.apply([fc_mean, fc_var])
            with tf.control_dependencies([ema_apply_op]):
                return tf.identity(fc_mean), tf.identity(fc_var)
        mean, var = mean_var_with_update()      # 根据新的 batch 数据, 记录并稍微修改之前的 mean/var
        # 将修改后的 mean / var 放入下面的公式
        wx_plus_b = tf.nn.batch_normalization(wx_plus_b, mean, var, shift, scale, epsilon)
        if activation_function is None:
            outputs = wx_plus_b
        else:
            outputs = activation_function(wx_plus_b)
        return outputs
