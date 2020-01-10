#__author__ = 'wing'
import numpy as np
DATASET_PATH = "../UCI HAR Dataset/"
classification=[[1,0,0,0,0,0,],[0,1,0,0,0,0,],[0,0,1,0,0,0,],[0,0,0,1,0,0,],[0,0,0,0,1,0,],[0,0,0,0,0,1]]
INPUT_SIGNAL_TYPES = [
    "body_acc_x_",
    "body_acc_y_",
    "body_acc_z_",
    "body_gyro_x_",
    "body_gyro_y_",
    "body_gyro_z_",
    "total_acc_x_",
    "total_acc_y_",
    "total_acc_z_"
]
TRAIN = "train/"
TEST = "test/"


class DataReader(object):
    def __init__(self):
        self.X_train_signals_paths = [
            DATASET_PATH + TRAIN + "Inertial Signals/" + signal + "train.txt" for signal in INPUT_SIGNAL_TYPES
        ]
        self.X_test_signals_paths = [
            DATASET_PATH + TEST + "Inertial Signals/" + signal + "test.txt" for signal in INPUT_SIGNAL_TYPES
        ]
        self.train_data, self.train_label, self.test_data, self.test_label = self.load_data()
        self._random()

        print(self.train_data.shape)
        print(self.train_label.shape)
        print(self.test_data.shape)
        print(self.test_label.shape)
        np.savetxt("train_data.txt", np.reshape(self.train_data, self.train_data.size))
        np.savetxt("train_label.txt", np.reshape(self.train_label, self.train_label.size))
        np.savetxt("test_data.txt", np.reshape(self.test_data, self.test_data.size))
        np.savetxt("test_label.txt", np.reshape(self.test_label, self.test_label.size))
        self.train_batch_order = 0

    def _random(self):
        data = []
        label = []
        batch_num = self.train_label.shape[0]
        for i in range(batch_num):
            num = np.random.randint(0, batch_num - i)
            data.append(self.train_data[num])
            label.append(self.train_label[num])
            np.delete(self.train_data,num,0)
            np.delete(self.train_label,num,0)
        self.train_data = np.array(data)
        self.train_label = np.array(label)

    def load_data(self):
        y_train_path = DATASET_PATH + TRAIN + "y_train.txt"
        y_test_path = DATASET_PATH + TEST + "y_test.txt"
        X_train = self.load_X(self.X_train_signals_paths)
        X_test = self.load_X(self.X_test_signals_paths)
        y_train = self.one_hot(self.load_y(str(y_train_path)))
        y_test = self.one_hot(self.load_y(y_test_path))
        # y_train = self.load_y(str(y_train_path))
        # y_test = self.load_y(y_test_path)
        return X_train,y_train,X_test,y_test

    # Load "X" (the neural network's training and testing inputs)
    def load_X(self,X_signals_paths):
        X_signals = []
        for signal_type_path in X_signals_paths:
            file = open(signal_type_path, 'r')
            # Read dataset from disk, dealing with text files' syntax
            X_signals.append(
                [np.array(serie, dtype=np.float32) for serie in [
                    row.replace('  ', ' ').strip().split(' ') for row in file
                ]]
            )
            file.close()
        return np.transpose(np.array(X_signals), (1, 2, 0))


    # Load "y" (the neural network's training and testing outputs)
    def load_y(self,y_path):
        file = open(y_path, 'r')
        # Read dataset from disk, dealing with text file's syntax
        y_ = np.array(
            [elem for elem in [
                row.replace('  ', ' ').strip().split(' ') for row in file
            ]],
            dtype=np.int32
        )
        file.close()
        # Substract 1 to each output class for friendly 0-based indexing
        return y_ - 1

    def one_hot(self,y_):
        # Function to encode output labels from number indexes
        # e.g.: [[5], [0], [3]] --> [[0, 0, 0, 0, 0, 1], [1, 0, 0, 0, 0, 0], [0, 0, 0, 1, 0, 0]]
        y_ = y_.reshape(len(y_))
        n_values = int(np.max(y_)) + 1
        return np.eye(n_values)[np.array(y_, dtype=np.int32)]  # Returns FLOATS

    def next_training_data(self, batch_num):
        x = self.train_data[self.train_batch_order:self.train_batch_order+batch_num]
        y = self.train_label[self.train_batch_order:self.train_batch_order+batch_num]
        self.train_batch_order += batch_num
        if self.train_batch_order >= self.train_data.shape[0]:
            self.train_batch_order = 0
            if x.shape[0] < batch_num:
                # print(x.__len__())
                self.train_batch_order = batch_num - x.shape[0]
                x = np.vstack((x, self.train_data[0:self.train_batch_order]))
                y = np.vstack((y, self.train_label[0:self.train_batch_order]))
        return np.array(x), np.array(y)

    def get_test_data(self):
        return self.test_data, self.test_label

    def get_train_data(self):
        return self.train_data, self.train_label

if __name__ == "__main__":
    gd = DataReader()
    for i in range(30):
        train_x, train_y = gd.next_training_data(3)
        print(str(i) + " " + str(train_x.shape) + " " + str(train_y.shape))
        # print("train_x:" + str(train_x))
        # print("train_y:" + str(train_y))
    test_x, test_y = gd.get_test_data()
    print(test_x.shape)
    # print("test_x:" + str(test_x))
    print(test_y.shape)
    # print("test_y:" + str(test_y))
