import tensorflow as tf
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split, KFold
from tensorflow.keras.layers import Conv2D, ReLU, Flatten, Dense, GlobalAveragePooling2D, BatchNormalization, Dropout
from tensorflow.keras import layers, models, Sequential
from tensorflow.keras import regularizers
from tensorflow.keras.callbacks import EarlyStopping
from data_process import FRAME_STACK




def doppler_model(frame_stack):
    model_1 = Sequential([
        layers.Conv2D(filters=32, kernel_size=(5, 5), strides=(1, 2), input_shape=(16, 256, frame_stack),kernel_regularizer=regularizers.l2(0.01)),
        layers.ReLU(),
        layers.BatchNormalization(),
        layers.Conv2D(filters=64, kernel_size=(3, 3), strides=(2, 2),kernel_regularizer=regularizers.l2(0.01)),
        layers.ReLU(),
        layers.BatchNormalization(),
        layers.Conv2D(filters=128, kernel_size=(3, 3), strides=(1, 1),kernel_regularizer=regularizers.l2(0.01)),
        layers.ReLU(),
        layers.BatchNormalization(),
        layers.GlobalAveragePooling2D(),
        layers.Dropout(0.3)
    ])
    return model_1


def azimuth_model(frame_stack):
    model_2 = Sequential([
        layers.Conv2D(filters=32, kernel_size=(5, 5), strides=(2, 2), input_shape=(100, 100, frame_stack),kernel_regularizer=regularizers.l2(0.01)),
        layers.ReLU(),
        layers.BatchNormalization(),
        layers.Conv2D(filters=64, kernel_size=(3, 3), strides=(2, 2),kernel_regularizer=regularizers.l2(0.01)),
        layers.ReLU(),
        layers.BatchNormalization(),
        layers.Conv2D(filters=128, kernel_size=(3, 3), strides=(2, 2),kernel_regularizer=regularizers.l2(0.01)),
        layers.ReLU(),
        layers.BatchNormalization(),
        layers.GlobalAveragePooling2D(),
        layers.Dropout(0.3)
    ])
    return model_2


def combined_model(FRAME_STACK):

    dop_input = layers.Input(shape=(16, 256, FRAME_STACK))
    dop_features = doppler_model(FRAME_STACK)(dop_input)

    azim_input = layers.Input(shape=(100, 100, FRAME_STACK))
    azim_features = azimuth_model(FRAME_STACK)(azim_input)
   
    combined_features = layers.Concatenate()([dop_features, azim_features])
   
    z = layers.Dense(96, activation='relu')(combined_features)
    z = layers.Dense(32, activation='relu')(z)
    z = layers.Dense(FRAME_STACK, activation='linear')(z)  
    
    
    model = models.Model(inputs=[dop_input, azim_input], outputs=z)
    return model


model = combined_model(FRAME_STACK)

model.compile(optimizer=tf.keras.optimizers.Adam(learning_rate=0.001),
              loss=tf.keras.losses.Huber(),  
              metrics=['mae'])  


model.save('model.h5')





