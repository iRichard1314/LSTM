# __author__ = 'wing'
import sys

import tensorflow as tf
import numpy as np
import DataGenerater
from model import HARClassifier
from lstm_model import LSTMModel
# tf.set_random_seed(1)
from java import jclass

input_size = 9
time_step = 128
class_num = 6
batch_size = 200

def train(sess, model, data):
    for i in range(200):
        batch_x, batch_y = data.next_training_data(batch_size)
        batch_x = np.reshape(batch_x, [-1, time_step, input_size])
        # batch_x = down_sampling(batch_x)
        batch_y = np.reshape(batch_y, [-1, class_num])
        if (i+1) % 50 == 0:
            train_accuracy = sess.run(model.accuracy, feed_dict={model.X:batch_x, model.y: batch_y, model.keep_prob: 1.0})
            message = "step %d, training accuracy %g" % ((i+1), train_accuracy)
            print(message)
        sess.run(model.train_op, feed_dict={model.X: batch_x, model.y: batch_y, model.keep_prob: 0.5})


def test(sess, model, data):
    test_x, test_y = data.get_test_data()
    test_x = np.reshape(test_x, [-1, time_step, input_size])
    test_y = np.reshape(test_y, [-1, class_num])
    test_x = down_sampling(test_x)
    test_accuracy= sess.run(model.accuracy, feed_dict={model.X: test_x, model.y: test_y, model.keep_prob: 1.0})
    message = "test accuracy: %g  " % test_accuracy
    print(message)


def down_sampling(data):
    for index in range(data.shape[0]):
        down_sampling_frequency = 12.5
        if down_sampling_frequency > 1:
            data[index,np.arange(time_step) % down_sampling_frequency != 0, :] = 0
    return data

def main():
    # # 设置 GPU 按需增长
    # config = tf.ConfigProto()
    # config.gpu_options.allow_growth = True
    # np.set_printoptions(threshold=10000)  #全部输出
    # sess = tf.Session(config=config)
    # coord = tf.train.Coordinator()
    # threads = tf.train.start_queue_runners(sess=sess, coord=coord)

    np.set_printoptions(threshold=10000)  # 全部输出
    sess = tf.Session()
    # model = HARClassifier(class_num=class_num)
    # model = HARClassifier()
    model = LSTMModel()
    sess.run(tf.global_variables_initializer())

    data = DataGenerater.DataGenerater()
    for i in range(50):
        train(sess, model, data)
        test(sess, model, data)
    # coord.request_stop()
    # coord.join(threads)

    saver = tf.train.Saver()
    save_dir = 'logs/models/'
    saver.save(sess, save_dir + '6')

# with tf.Session() as sess:
#     saver = tf.train.import_meta_graph('C:/czm_orange/code1/down_sampling/m/1.ckpt.meta')
#     # saver.restore(sess, tf.train.latest_checkpoint('./checkpoint_dir'))

def doRun(path):
    # # 设置 GPU 按需增长
    # config = tf.ConfigProto()
    # config.gpu_options.allow_growth = True
    # np.set_printoptions(threshold=10000)  #全部输出
    # sess = tf.Session(config=config)
    # coord = tf.train.Coordinator()
    # threads = tf.train.start_queue_runners(sess=sess, coord=coord)
    JavaBean = jclass("com.diy.edu.rd.Model.JavaBean")
    jb = JavaBean("python")
    jb.println("---------------------------->start<----------------");
    jb.println("---------------------------->"+path+"<----------------");
    np.set_printoptions(threshold=10000)  # 全部输出
    sess = tf.Session()
    # model = HARClassifier(class_num=class_num)
    # model = HARClassifier()
    model = LSTMModel()
    sess.run(tf.global_variables_initializer())

    data = DataGenerater.DataGenerater(path)
    for i in range(50):
        train(sess, model, data)
        test(sess, model, data)
    # coord.request_stop()
    # coord.join(threads)

    saver = tf.train.Saver()
    save_dir = path+'models/'
    saver.save(sess, save_dir + '6')


if __name__ == "__main__":
    main()


