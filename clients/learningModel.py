import numpy as np
import random
import os
import pickle
import pandas as pd

#from imutils import paths
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelBinarizer
from sklearn.model_selection import train_test_split
from sklearn.utils import shuffle
from sklearn.metrics import accuracy_score

import tensorflow as tf
from tensorflow import keras
from keras.models import Sequential
from keras.layers import Conv2D
from keras.layers import MaxPooling2D
from keras.layers import Activation
from keras.layers import Flatten
from keras.layers import Dense, Dropout
from keras.optimizers import SGD
from keras import backend as K

class FLlearningModel: 
    
    ## @staticmethod
    def __init__(self, epochs, shape, classes, learningRate):
        self.lr = learningRate
        self.Epochs = epochs
        self.loss='categorical_crossentropy'
        self.metrics = ['accuracy']
        self.optimizer = SGD(learning_rate=self.lr,
                        ## decay=self.lr / 5,
                        momentum=0.9, 
                        nesterov=True
                    )
        self.model = Sequential()
        self.model.add(Dense(500,input_shape=(shape,)))
        self.model.add(Activation("relu"))
        self.model.add(Dropout(0.5))
        # self.model.add(Dense(500))
        # self.model.add(Activation("relu"))
        # self.model.add(Dense(300))
        # self.model.add(Activation("relu"))
        self.model.add(Dense(500))
        self.model.add(Activation("relu"))
        self.model.add(Dropout(0.5))
        self.model.add(Dense(classes))
        self.model.add(Activation("softmax"))
        # return self.model


    def weight_scalling_factor(self, clients_trn_data, client_name):
        client_names = list(clients_trn_data.keys())
        #get the bs (batch size)
        bs = list(clients_trn_data[client_name])[0][0].shape[0]
        #first calculate the total training data points across clients
        global_count = sum([tf.data.experimental.cardinality(clients_trn_data[client_name]).numpy() for client_name in client_names])*bs
        # get the total number of data points held by a client
        local_count = tf.data.experimental.cardinality(clients_trn_data[client_name]).numpy()*bs
        return local_count/global_count


    def scale_model_weights(self, weight, scalar):
        '''function for scaling a models weights'''
        weight_final = []
        steps = len(weight)
        for i in range(steps):
            weight_final.append(scalar * weight[i])
        return weight_final

    def scale_model_weights_2(self, weight, scalar):
        '''function for scaling a models weights'''
        weight_final = []
        steps = len(weight)
        for i in range(steps):
            weight_final.append(weight[i]/scalar)
        return weight_final

    def sum_scaled_weights(self, scaled_weight_list):
        '''Return the sum of the listed scaled weights. The is equivalent to scaled avg of the weights'''
        avg_grad = list()
        #get the average grad accross all client gradients
        for grad_list_tuple in zip(*scaled_weight_list):
            layer_mean = tf.math.reduce_sum(grad_list_tuple, axis=0)
            avg_grad.append(layer_mean)

        return avg_grad

    def batch_data(self, data_shard, bs=32):
        '''Takes in a clients data shard and create a tfds object off it
        args:
            shard: a data, label constituting a client's data shard
            bs:batch size
        return:
            tfds object'''
        #seperate shard into data and labels lists
        data, label = zip(*data_shard)
        dataset = tf.data.Dataset.from_tensor_slices((list(data), list(label)))
        return dataset.shuffle(len(label)).batch(bs)

    def test_model(self, X_test, Y_test, numRound, clientName):
        cce = tf.keras.losses.CategoricalCrossentropy(from_logits=True)
        #logits = model.predict(X_test, batch_size=100)
        logits = self.model.predict(X_test)
        #print(logits)
        loss = cce(Y_test, logits)
        acc = accuracy_score( tf.argmax(Y_test, axis=1),tf.argmax(logits, axis=1))
        # print('round: {} | client {} | accuracy: {:.3%} | loss: {}'.format(numRound, accountNum, acc, loss))
        print(f'round {numRound}: {clientName} accuracy: {acc}')
        return acc, loss

    def train_model(self, trainData):
        self.model.compile(loss=self.loss,
                      optimizer=self.optimizer,
                      metrics=self.metrics)
        self.model.fit(self.batch_data(trainData), epochs=self.Epochs, verbose=0)
        
    def get_weights(self):
        return self.model.get_weights()
    
    def set_weights(self, newWeights):
        self.model.set_weights(newWeights)
    