#__author__ = 'wing'
import tensorflow as tf

time_step = 128
input_size = 9
class HARClassifier(object):
    def __init__(self,class_num):
        self.X = tf.placeholder(tf.float32, [None, time_step, input_size],name='x_input')
        self.y = tf.placeholder(tf.float32, [None, class_num],name='y_input')
        self.keep_prob = tf.placeholder(tf.float32,name='keep_prob')
        x_image = tf.reshape(self.X, [-1,time_step, input_size,1])  # 重塑图片结构，-1代表样本数量不确定，最后面的1代表颜色通道
        # 定义第一层卷积层
        # w_conv1 = self.weight_variable([5, 5, 1, 16])  # 使用32个5*5的卷积核
        w_conv1 = tf.Variable(tf.truncated_normal([5, 5, 1, 16], stddev=0.1), dtype=tf.float32)
        # b_conv1 = self.bias_variable([16])
        b_conv1 = tf.Variable(tf.constant(0.1, shape=[16]), dtype=tf.float32)
        h_conv1 = tf.nn.relu(tf.nn.conv2d(x_image, w_conv1, strides=[1, 2, 1, 1], padding='SAME') + b_conv1)
        h_pool1 = tf.nn.max_pool(h_conv1, ksize=[1, 2, 1, 1], strides=[1, 2, 1, 1], padding='SAME')  # 降采样

        # 定义第二层卷积层
        # w_conv2 = self.weight_variable([5, 5,16, 32])  # 这里有32个通道，使用64个5*5的卷积核
        w_conv2 = tf.Variable(tf.truncated_normal([5, 5,16, 32], stddev=0.1), dtype=tf.float32)
        # b_conv2 = self.bias_variable([32])
        b_conv2 = tf.Variable(tf.constant(0.1, shape=[32]), dtype=tf.float32)
        h_conv2 = tf.nn.relu(tf.nn.conv2d(h_pool1, w_conv2, strides=[1, 2, 1, 1], padding='SAME') + b_conv2)
        h_pool2 = tf.nn.max_pool(h_conv2, ksize=[1, 2, 1, 1], strides=[1, 2, 1, 1], padding='SAME')

        # 再连接一层全连接层
        # w_fc1 = self.weight_variable([6 * 32, 256])
        w_fc1 = tf.Variable(tf.truncated_normal([72 * 32, 256], stddev=0.1), dtype=tf.float32)
        # b_fc1 = self.bias_variable([256])
        b_fc1 = tf.Variable(tf.constant(0.1, shape=[256]), dtype=tf.float32)
        h_pool2_flat = tf.reshape(h_pool2, [-1,72 * 32])  # 将图片再展开成为一维结构
        h_fc1 = tf.nn.relu(tf.matmul(h_pool2_flat, w_fc1) + b_fc1)

        # 没事又再搞一个dropout
        # keep_prob = tf.placeholder(tf.float32)
        h_fc1_drop = tf.nn.dropout(h_fc1, self.keep_prob)

        # w_fc2 = self.weight_variable([256, class_num])
        w_fc2 = tf.Variable(tf.truncated_normal([256, class_num], stddev=0.1), dtype=tf.float32)
        # b_fc2 = self.bias_variable([class_num])
        b_fc2 = tf.Variable(tf.constant(0.1, shape=[class_num]), dtype=tf.float32)
        # 输出层为softmax层
        self.y_pre = tf.nn.softmax(tf.matmul(h_fc1_drop, w_fc2) + b_fc2,name='features')
        self.out = tf.argmax(self.y_pre,1,name='output')
        cross_entropy = -tf.reduce_mean(self.y * tf.log(self.y_pre))
        self.train_op = tf.train.AdamOptimizer(0.0005).minimize(cross_entropy)

        self.correct_prediction = tf.equal(tf.argmax(self.y_pre,1), tf.argmax(self.y,1))
        self.accuracy = tf.reduce_mean(tf.cast(self.correct_prediction, "float"))

    # def weight_variable(self,shape):  # shape为参数的矩阵形状
    #     initial = tf.truncated_normal(shape, stddev=0.1)
    #     return tf.Variable(initial, dtype=tf.float32)


    # def bias_variable(self,shape):
    #     initial = tf.constant(0.1, shape=shape)
    #     return tf.Variable(initial, dtype=tf.float32)


    # 然后我们再定义卷积和池化两个函数，以方便使用。
    # def conv2d(self,x, W):  # x是输入，W是参数，例如输入w[5,5,1,32],代表使用32个5*5的卷积核，颜色通道为1，代表图片仅有灰度单色
    #     return tf.nn.conv2d(x, W, strides=[1, 2, 2, 1], padding='SAME')
    #     # strides=[1,k,k,1],k代表横竖方向移动的步长，这里取1padding='same'代表边界处理的方式，即让输出和输入保持同样尺寸


    # def max_pool_2x2(self,x):
    #     return tf.nn.max_pool(x, ksize=[1, 2, 2, 1], strides=[1, 2, 2, 1], padding='SAME')
        # 这里ksize=[1,k,k,1]代表将2*2像素降为1*1像素，strides=[1,k,k,1]依然代表横竖移动2个步长


