# __author__ = 'wing'
import numpy as np
from java import jclass
# from collections import OrderedDict
# import pyexcel_xls
time_step = 128
sensor_channels = 9
classification_num = 6
root_path = "./Data/"

class DataGenerater(object):
    def __init__(self,root_path):
        JavaBean = jclass("com.diy.edu.rd.Model.JavaBean")
        jb = JavaBean("python")
        jb.println("---------------------------->DataGenerater<----------------");
        self.root_path = root_path;
        self.train_data = np.reshape(np.loadtxt(root_path + "train_data.txt"), (-1, time_step,sensor_channels))
        self.train_label = np.reshape(np.loadtxt(root_path + "train_label.txt"), (-1, classification_num))
        self.test_data = np.reshape(np.loadtxt(root_path + "test_data.txt"), (-1, time_step,sensor_channels))
        self.test_label = np.reshape(np.loadtxt(root_path + "test_label.txt"), (-1, classification_num))
        self.train_batch_order = 0
        jb.println("DataGenerater init "+str(self.train_data.shape[0]))
        jb.println("train_data:"+str(self.train_data.shape))
        jb.println("train_label:"+str(self.train_label.shape))
        jb.println("test_data:"+str(self.test_data.shape))
        jb.println("test_label:"+str(self.test_label.shape))
        # save_data = OrderedDict()
        # save_data.update({"0": self.train_label})
        # save_data.update({"1": self.test_label})
        # pyexcel_xls.save_data("DataGenerater.xls", save_data)

    # @staticmethod
    # def max_min_normalization(data):
    #     max_value = np.ndarray.max(data, axis=0)
    #     min_value = np.ndarray.min(data,axis=0)
    #     return (data-min_value)/(max_value-min_value)

    def next_training_data(self, batch_num):
        x = self.train_data[self.train_batch_order:self.train_batch_order+batch_num]
        y = self.train_label[self.train_batch_order:self.train_batch_order+batch_num]
        self.train_batch_order += batch_num
        if self.train_batch_order >= self.train_data.shape[0]:
            self.train_batch_order = 0
            if x.shape[0] < batch_num:
                self.train_batch_order = batch_num - x.shape[0]
                x = np.vstack((x, self.train_data[0:self.train_batch_order]))
                y = np.vstack((y, self.train_label[0:self.train_batch_order]))
        return np.array(x), np.array(y)

    def get_train_data(self):
        return self.train_data, self.train_label

    def get_test_data(self):
        return self.test_data, self.test_label

if __name__ == "__main__":
    JavaBean = jclass("com.diy.edu.rd.Model.JavaBean")
    jb = JavaBean("python")
    jb.println("---------------------------->DataGenerater main<----------------");
    gd = DataGenerater()
    for i in range(3):
        train_x, train_y = gd.next_training_data(3)
        jb.println(str(i) + " " + str(train_x.shape) + " " + str(train_y.shape))
        # print("train_x:" + str(train_x))
        jb.println("train_y:" + str(train_y))
    test_x, test_y = gd.get_test_data()
    jb.println(test_x.shape)
    # print("test_x:" + str(test_x))
    jb.println(test_y.shape)
    # print("test_y:" + str(test_y))