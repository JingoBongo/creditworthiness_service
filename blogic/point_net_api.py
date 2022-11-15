import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

import os.path
from sklearn.model_selection import train_test_split

import tensorflow as tf
from tensorflow import keras
from keras import backend as K
from tensorflow.keras import layers

class OrthogonalRegularizer(keras.regularizers.Regularizer):
    """enhance keras regularizer via its overwriting
    """
    def __init__(self, num_features: int, l2reg=0.001):
        """form regularizer with specified number of features and value for
        L2 regularization

        Args:
            num_features (int): how many dimensions does one record have
            l2reg (float, optional): value of regularization. Defaults to 0.001.
        """
        self.num_features = num_features
        self.l2reg = l2reg
        self.eye = tf.eye(num_features)

    def __call__(self, x):
        """overwrite of the call function for the class

        Args:
            x: input

        Returns:
            regularization result
        """
        x = tf.reshape(x, (-1, self.num_features, self.num_features))
        xxt = tf.tensordot(x, x, axes=(2, 2))
        xxt = tf.reshape(xxt, (-1, self.num_features, self.num_features))
        return tf.reduce_sum(self.l2reg * tf.square(xxt - self.eye))
    

def read_all_pickles(prefix_names: list=None, top_value: int=20000) -> pd.DataFrame:
    """
    Read all pickle files located at the specified folder. Pickle files are suggested to have format
    like "<process_forming_pickle_PID>_landmarks.pkl". In case of adding other datasets information
    there is a specified prefix name.

    Args:
        prefix_names (list, optional): prefixes in the beginning of file names. Defaults to None.
        top_value (int, optional): threshold of pickle files count. Defaults to 20000.

    Returns:
        pd.DataFrame: dataframe of training data collected out of different datasets
    """
    global_df = None

    #   go through base files
    for index in range(top_value):
        current_path = 'original_pkls/' + str(index) + '_landmarks.pkl'
        if os.path.isfile(current_path):
            cur_df = pd.read_pickle(current_path)
            global_df = pd.concat([global_df, cur_df])

    #   go through prefix files if there are any specified
    if prefix_names is not None:
        for prefix in prefix_names:
            for index in range(top_value):
                current_path = 'original_pkls/' + prefix + str(index) + '_landmarks.pkl'
                if os.path.isfile(current_path):
                    cur_df = pd.read_pickle(current_path)
                    global_df = pd.concat([global_df, cur_df])

    return global_df


def conv_bn(x, filters: int, activation_function: str="relu", kernel_size: int=1):
    """1D convolution with batch normalization, setting specified activation function

    Args:
        x: input data
        filters (int): how many filters apply for convolution (how many neurons)
        activation_function (str, optional): activation function for neuron, defaults to 'relu'
        kernel_size (int): size of convolutional kernel

    Returns:
        Convolutional layer with specified activation function and filters
    """
    x = layers.Conv1D(filters, kernel_size=1, padding="valid")(x)
    x = layers.BatchNormalization(momentum=0.0)(x)
    return layers.Activation(activation_function)(x)


def dense_bn(x, filters: int, activation_function: str='relu'):
    """Dense layer with specification of how many neurons and what activation function to use

    Args:
        x: input data
        filters (int): how many filters to use (or how many neurons in layer)
        activation_function (str, optional): activation function for neuron. Defaults to 'relu'

    Returns:
        Dense layer with specified amount of neurons and activation function
    """
    x = layers.Dense(filters)(x)
    x = layers.BatchNormalization(momentum=0.0)(x)
    return layers.Activation(activation_function)(x)

def tnet(inputs, num_features: int, first_degree: int, second_degree: int, third_degree: int, fourth_degree: int):
    """T-net layer that performs multiple 1D convolutions with Max Pooling of received results to reduce
    dimensionality and complexity of the problem. Final layers are represented by Dense layers.
    Results that will be received after all those transformations will be dot of original matrix
    with new one.

    Args:
        inputs: input data
        num_features (int): dimensionality of the input data
        first, second, third and fourth degrees (int): how many neurons to set for specific layers,
                                                        try to use numbers with base 2

    Returns:
        dot product of the original matrix with updated one.
    """

    # Initalise bias as the indentity matrix
    bias = keras.initializers.Constant(np.eye(num_features).flatten())
    reg = OrthogonalRegularizer(num_features)

    x = conv_bn(inputs, 32)
    x = conv_bn(x, first_degree)
    x = conv_bn(x, fourth_degree)
    x = layers.GlobalMaxPooling1D()(x)
    x = dense_bn(x, third_degree)
    x = dense_bn(x, second_degree)
    x = layers.Dense(
        num_features * num_features,
        kernel_initializer="zeros",
        bias_initializer=bias,
        activity_regularizer=reg,
    )(x)
    feat_T = layers.Reshape((num_features, num_features))(x)
    # Apply affine transformation to input features
    return layers.Dot(axes=(2, 1))([inputs, feat_T])