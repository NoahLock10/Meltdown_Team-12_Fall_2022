# -*- coding: utf-8 -*-
"""MeltdownClassifier.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/16F6odsinwjqeIQqB8Xk5xjZE0mdGcHHM
"""

# Commented out IPython magic to ensure Python compatibility.
# Load the TensorBoard notebook extension
# %load_ext tensorboard

# Libraries
import tensorflow as tf
from tensorflow import keras
from keras.models import Sequential
from keras.layers import Dense
from keras.layers import Dropout
from keras.layers import Activation
from keras.models import Model
from keras.optimizers import adam_v2
from sklearn.preprocessing import LabelBinarizer
from sklearn.preprocessing import MinMaxScaler
from sklearn.model_selection import train_test_split
import pandas as pd
import numpy as np
import os

print(tf.__version__)

# Load in data from csv using Pandas library
inputPath = "dataset.csv"
# Read csv to pandas dataframe object
df = pd.read_csv(inputPath, sep=",") 
print(df.head()) # Visualize dataset

# Feature selection
features = list(df.columns.values)
features.remove("Label")
print(features)
# Split features and labels
X = df[features]
y = df["Label"]

print(X.head())

print(y.head())

# Converts pandas dataframe objects
# into numpy arrays for training
X = X.to_numpy()
y = y.to_numpy()

print(max(X[:,0]))

print(max(X[:,1]))

# Preprocess numpy arrays for training
# All train/test data falls between 0-1

# Min-Max scaling of continuous values
# i.e. HR => [0, 1] range
X[:,0] = X[:,0] / max(X[:,0])
X[:,1] = X[:,1] / max(X[:,1])

# One-hot encoding of categorical data
# i.e Acoustic Class => [1 0 0 0 0 0 0 0]
one_hots = np.zeros((X[:,2].size, int(max(X[:,2]))+1))
one_hots[np.arange(X[:,2].size), X[:,2].astype(int)] = 1

# Concatenate scaled cont. vals and one-hot encoded cat. vals
X = np.hstack((X[:,0:2], one_hots))

# Split data into a training and testing set
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2)

print(y_train.shape)

# Define multilayer perceptron
dim = X_train[0].shape
model = keras.Sequential()
model.add(Dense(16, input_shape=dim, activation="relu"))
#model.add(Dropout(0.2))
model.add(Dense(8, activation="relu"))
#model.add(Dense(2, activation="relu"))
model.add(Dense(1, activation="sigmoid"))

print(model.summary())

# Compile model using 
#  - binary_crossentropy loss
#  - adam optimizer
model.compile(optimizer="adam", loss="binary_crossentropy", metrics=["accuracy"])

print(X_train[0].shape)

# Train the model
# Here, we will use 
# - epochs=8 (1 epoch = 1 complete pass over training data)
# - Stochastic Gradient Descent (batch_size=1)
log_dir = "logs/fit/"
tensorboard_callback = tf.keras.callbacks.TensorBoard(log_dir=log_dir, histogram_freq=1)
# ALEX SAYS 7 MAX?
model.fit(X_train, y_train, epochs=12, batch_size=1, validation_data=(X_test, y_test), callbacks=[tensorboard_callback])

# Test the network
test_loss, test_acc = model.evaluate(X_test, y_test)
print(test_acc)

# Commented out IPython magic to ensure Python compatibility.
# %tensorboard --logdir logs/fit

"""Max Avg. HR: 200.1; Max Final-Initial HR: 28"""

# Perform inference
# Acoustic Class 0 : Crowd Conversations

crowdConv_vec = np.array([[87.5/200.1, 18/28, 1, 0, 0, 0, 0, 0, 0, 0], # Meltdown
                     [140.7/200.1, 12/28, 1, 0, 0, 0, 0, 0, 0, 0], # Meltdown
                     [100/200.1, 10/28, 1, 0, 0, 0, 0, 0, 0, 0], # Meltdown
                     [115.5/200.1, 10/28, 1, 0, 0, 0, 0, 0, 0, 0], # Meltdown
                     [75.9/200.1, 2/28, 1, 0, 0, 0, 0, 0, 0, 0], # Non
                     [79.2/200.1, 4/28, 1, 0, 0, 0, 0, 0, 0, 0], # Non
                     [81.4/200.1, 0/28, 1, 0, 0, 0, 0, 0, 0, 0], # Non
                     [76.2/200.1, 6/28, 1, 0, 0, 0, 0, 0, 0, 0]]) # Non
pred = model.predict(crowdConv_vec)
print(pred)

# Perform inference
# Acoustic Class 1 : Large Conversations

largeConv_vec = np.array([[115.5/200.1, 13/28, 0, 1, 0, 0, 0, 0, 0, 0], # Meltdown
                     [105.3/200.1, 15/28, 0, 1, 0, 0, 0, 0, 0, 0], # Meltdown
                     [100/200.1, 14/28, 0, 1, 0, 0, 0, 0, 0, 0], # Meltdown
                     [122.3/200.1, 8/28, 0, 1, 0, 0, 0, 0, 0, 0], # Meltdown
                     [90.2/200.1, 2/28, 0, 1, 0, 0, 0, 0, 0, 0], # Non
                     [76.8/200.1, 5/28, 0, 1, 0, 0, 0, 0, 0, 0], # Non
                     [82.4/200.1, 1/28, 0, 1, 0, 0, 0, 0, 0, 0], # Non
                     [85.3/200.1, 6/28, 0, 1, 0, 0, 0, 0, 0, 0]]) # Non
pred = model.predict(largeConv_vec)
print(pred)

# Perform inference
# Acoustic Class 2 : Noise

noise_vec = np.array([[99/200.1, 15/28, 0, 0, 1, 0, 0, 0, 0, 0], # Meltdown
                     [113.6/200.1, 9/28, 0, 0, 1, 0, 0, 0, 0, 0], # Meltdown
                     [107.8/200.1, 12/28, 0, 0, 1, 0, 0, 0, 0, 0], # Meltdown
                     [120.1/200.1, 7/28, 0, 0, 1, 0, 0, 0, 0, 0], # Meltdown
                     [90.2/200.1, 8/28, 0, 0, 1, 0, 0, 0, 0, 0], # Non
                     [86.5/200.1, 7/28, 0, 0, 1, 0, 0, 0, 0, 0], # Non
                     [84.3/200.1, 5/28, 0, 0, 1, 0, 0, 0, 0, 0], # Non
                     [88.2/200.1, 6/28, 0, 0, 1, 0, 0, 0, 0, 0]]) # Non
pred = model.predict(noise_vec)
print(pred)

# Perform inference
# Acoustic Class 3 : Quiet

quiet_vec = np.array([[117.7/200.1, 14/28, 0, 0, 0, 1, 0, 0, 0, 0], # Meltdown
                     [105.3/200.1, 16/28, 0, 0, 0, 1, 0, 0, 0, 0], # Meltdown
                     [108.0/200.1, 11/28, 0, 0, 0, 1, 0, 0, 0, 0], # Meltdown
                     [118.3/200.1, 10/28, 0, 0, 0, 1, 0, 0, 0, 0], # Meltdown
                     [91.3/200.1, 2/28, 0, 0, 0, 1, 0, 0, 0, 0], # Non
                     [74.3/200.1, 5/28, 0, 0, 0, 1, 0, 0, 0, 0], # Non
                     [81.2/200.1, 8/28, 0, 0, 0, 1, 0, 0, 0, 0], # Non
                     [69.9/200.1, 10/28, 0, 0, 0, 1, 0, 0, 0, 0]]) # Non
pred = model.predict(quiet_vec)
print(pred)

# Perform inference
# Acoustic Class 4 : Small Conversation

smallConv_vec = np.array([[121.7/200.1, 7/28, 0, 0, 0, 0, 1, 0, 0, 0], # Meltdown
                     [103.7/200.1, 13/28, 0, 0, 0, 0, 1, 0, 0, 0], # Meltdown
                     [111/200.1, 15/28, 0, 0, 0, 0, 1, 0, 0, 0], # Meltdown
                     [132.3/200.1, 7/28, 0, 0, 0, 0, 1, 0, 0, 0], # Meltdown
                     [89.5/200.1, 6/28, 0, 0, 0, 0, 1, 0, 0, 0], # Non
                     [92.3/200.1, 3/28, 0, 0, 0, 0, 1, 0, 0, 0], # Non
                     [83.1/200.1, 4/28, 0, 0, 0, 0, 1, 0, 0, 0], # Non
                     [89.9/200.1, 8/28, 0, 0, 0, 0, 1, 0, 0, 0]]) # Non
pred = model.predict(smallConv_vec)
print(pred)

# Perform inference
# Acoustic Class 5 : Stimuli

stimuli_vec = np.array([[110.8/200.1, 9/28, 0, 0, 0, 0, 0, 1, 0, 0], # Meltdown
                     [135.5/200.1, 4/28, 0, 0, 0, 0, 0, 1, 0, 0], # Meltdown
                     [95.6/200.1, 20/28, 0, 0, 0, 0, 0, 1, 0, 0], # Meltdown
                     [101.2/200.1, 16/28, 0, 0, 0, 0, 0, 1, 0, 0], # Meltdown
                     [87.4/200.1, 3/28, 0, 0, 0, 0, 0, 1, 0, 0], # Non
                     [91.2/200.1, 5/28, 0, 0, 0, 0, 0, 1, 0, 0], # Non
                     [78.4/200.1, 4/28, 0, 0, 0, 0, 0, 1, 0, 0], # Non
                     [69.9/200.1, 5/28, 0, 0, 0, 0, 0, 1, 0, 0]]) # Non
pred = model.predict(stimuli_vec)
print(pred)

# Perform inference
# Acoustic Class 6 : Unknown

unknown_vec = np.array([[119.3/200.1, 10/28, 0, 0, 0, 0, 0, 0, 1, 0], # Meltdown
                     [100.3/200.1, 17/28, 0, 0, 0, 0, 0, 0, 1, 0], # Meltdown
                     [117.2/200.1, 9/28, 0, 0, 0, 0, 0, 0, 1, 0], # Meltdown
                     [126/200.1, 5/28, 0, 0, 0, 0, 0, 0, 1, 0], # Meltdown
                     [89.3/200.1, 5/28, 0, 0, 0, 0, 0, 0, 1, 0], # Non
                     [84.1/200.1, 7/28, 0, 0, 0, 0, 0, 0, 1, 0], # Non
                     [95/200.1, 3/28, 0, 0, 0, 0, 0, 0, 1, 0], # Non
                     [76.4/200.1, 7/28, 0, 0, 0, 0, 0, 0, 1, 0]]) # Non
pred = model.predict(unknown_vec)
print(pred)

# Perform inference
# Acoustic Class 7 : Wind

wind_vec = np.array([[114.3/200.1, 10/28, 0, 0, 0, 0, 0, 0, 0, 1], # Meltdown
                     [139.4/200.1, 4/28, 0, 0, 0, 0, 0, 0, 0, 1], # Meltdown
                     [110/200.1, 11/28, 0, 0, 0, 0, 0, 0, 0, 1], # Meltdown
                     [98.9/200.1, 19/28, 0, 0, 0, 0, 0, 0, 0, 1], # Meltdown
                     [68.4/200.1, 9/28, 0, 0, 0, 0, 0, 0, 0, 1], # Non
                     [74.5/200.1, 7/28, 0, 0, 0, 0, 0, 0, 0, 1], # Non
                     [80/200.1, 6/28, 0, 0, 0, 0, 0, 0, 0, 1], # Non
                     [84.6/200.1, 5/28, 0, 0, 0, 0, 0, 0, 0, 1]]) # Non
pred = model.predict(wind_vec)
print(pred)

"""Intervals Testing:
Avg. HR > 125 should predict >50%
(F-I) HR > 12 should predict >50%
CrowdConv || Stimuli should predict >50%
"""

random_testing = np.array([[125/200.1, 6/28, 0, 0, 1, 0, 0, 0, 0, 0],
                           [89/200.1, 13/28, 0, 0, 0, 1, 0, 0, 0, 0],
                           [89/200.1, 5/28, 1, 0, 0, 0, 0, 0, 0, 0]])

pred = model.predict(random_testing)
print(pred)