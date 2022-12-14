# -*- coding: utf-8 -*-
"""AcousticClassifier.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1RXEPfMBJQAMmnaFIcLl02gwTDCl2b_ot
"""

pip install pydub

mkdir melspec_files

mkdir audio_files

mkdir saved_model_data/

mkdir saved_model_data/MarkusModel/

mkdir saved_model_data/MarkusModel/variables

"""# 1. Python Libraries"""

import tensorflow as tf
import tensorflow.keras as keras
from flask import Flask, request, jsonify
import requests
import numpy as np
from PIL import Image
from pathlib import Path
import matplotlib.pyplot as plt
from pydub import AudioSegment
import librosa
import librosa.display
import os
from google.colab import drive
#drive.mount('/content/gdrive')
os.environ["TF_CPP_MIN_LOG_LEVEL"] = "2"
physical_devices = tf.config.list_physical_devices("GPU")
tf.config.allow_growth = True

"""# 2. Function Definitions"""

# will load the model and return it. One time setup only
def load(modelPath):
    global model
    model = keras.models.load_model(modelPath)
    return model

def makeMelSpec(filename):
    test = "melspec_files/" + filename + ".png"  # where mel-spectrogram file is saved
    my_file = Path(test)
    # check if a mel-spec has already been created
    if not my_file.is_file():
        y, sr = librosa.load("audio_files/" + filename + ".wav")  # load .wav audio file from where it is stored

        whale_song, _ = librosa.effects.trim(y) # trim silent edges
        n_fft = 2048
        hop_length = 100
        D = np.abs(librosa.stft(whale_song, n_fft=n_fft, hop_length=hop_length + 1))
        DB = librosa.amplitude_to_db(D, ref=np.max)
        librosa.display.specshow(DB, sr=sr, hop_length=hop_length)
        plt.gca().set_axis_off()
        plt.subplots_adjust(top=1, bottom=0, right=1, left=0,
                            hspace=0, wspace=0)
        plt.margins(0, 0)
        plt.gca().xaxis.set_major_locator(plt.NullLocator())
        plt.gca().yaxis.set_major_locator(plt.NullLocator())
        # plt.show()
        plt.savefig(test, bbox_inches='tight', pad_inches=0)
        plt.close()
        print(filename)
    else:
        print("mel-spec file already exists")

# Cut audio recording and save
def cutSong(song, st, en, count, file_name, type, path):
    extract = song[st:en]
    # Saving
    print(path + file_name + str(count) + "WAV......")
    extract.export(path + file_name + str(count) + type, format="wav")
    return extract

# Cut audio recording into 1.5 second chunks
# Convert each chunk into a mel-spec
def cutAll(files_path, file_name, type):
    song = AudioSegment.from_wav(files_path + file_name)
    secs = song.duration_seconds
    samples = secs / 1.5
    samples = round(samples)
    if (samples >= 1):
        for i in range(samples - 1):
            d = i * 1.5
            startMin = 0
            startSec = d
            endMin = 0
            endSec = d + 1.5
            # Time to miliseconds
            startTime = startMin * 60 * 1000 + startSec * 1000
            endTime = endMin * 60 * 1000 + endSec * 1000
            name = file_name.replace(type, "")
            try:
                cutSong(song, startTime, endTime, i, name.replace(".WAV", ""), type, "audio_files/")
                makeMelSpec(name.replace(".WAV", "") + str(i))
            except Exception as error:
                print(error)

# Will predict the outcome of a target image.
# path must be like: ZOOM0011204.png
def predictOutcome(model, imagePath):
    img = keras.preprocessing.image.load_img(
        imagePath, target_size=(314, 235)
    )
    img_array = keras.preprocessing.image.img_to_array(img)
    img_array = tf.expand_dims(img_array, 0)  # Create a batch
    predictions = model.predict(img_array)
    score = tf.nn.softmax(predictions[0])
    labeled = {'Crowd_Conversation': score[0], 'Large_Conversation': score[1], "Noise": score[2], "Quiet": score[3],
               "Small_Conversation": score[4], "Stimuli": score[5], "Unknown": score[6], "Wind": score[7]}

    return labeled

"""# 3. Mel-Spec Conversion - Testing"""

# Load in sample audio file and convert to mel-spec using the above function
makeMelSpec("ZOOM000850")
# CrowdConv
makeMelSpec("ZOOM000968")
makeMelSpec("ZOOM0008393") # Predicts small first, crowd second
makeMelSpec("ZOOM00082458")
makeMelSpec("ZOOM00081699")
makeMelSpec("ZOOM00061039") 
# LargeConv
makeMelSpec("ZOOM0013198")
makeMelSpec("ZOOM00128")
makeMelSpec("ZOOM001388")
makeMelSpec("ZOOM00088")
makeMelSpec("ZOOM00081001") # Could argue this is a crowd conv
# Noise
makeMelSpec("ZOOM0006152")
makeMelSpec("ZOOM0006189")
makeMelSpec("ZOOM0006289") # Predicts small first, noise second
makeMelSpec("ZOOM0006325")
makeMelSpec("ZOOM0006326")
makeMelSpec("ZOOM0006334") 
makeMelSpec("ZOOM00082372")
# Quiet
makeMelSpec("ZOOM00062113")
makeMelSpec("ZOOM0006191") # Predicts small conv - not a huge deal
makeMelSpec("ZOOM0006859")
# SmallConv
makeMelSpec("ZOOM0006481")
makeMelSpec("ZOOM00061214")
makeMelSpec("ZOOM00082578")
makeMelSpec("ZOOM0006940")
makeMelSpec("ZOOM00061858")
# Stimuli
makeMelSpec("ZOOM0011122")
makeMelSpec("ZOOM001084")
makeMelSpec("ZOOM001057")
makeMelSpec("ZOOM0011296")
makeMelSpec("ZOOM0011241")
# Wind
makeMelSpec("ZOOM00082571")
makeMelSpec("ZOOM00082575")
makeMelSpec("ZOOM00082577") # Predicts stimuli first, wind second
makeMelSpec("ZOOM0008686") # Predicts stimuli first, wind second

"""# 4. Acoustic Classification - Testing"""

# Load model data from path
filePath = "saved_model_data/MarkusModel/"
# Restore Keras model capable of prediction
model = keras.models.load_model(filePath)
# Make sure variable files do not get corrupted during uploading
# This will cause an 'IndexError: Read less bytes than expected'

"""Acoustic Class 0 : CrowdConv"""

# Correct prediction
label = predictOutcome(model, "melspec_files/" + "ZOOM000968.png")
prediction = ""
for key, value in label.items():
    prediction += str(key) + ":" + str(value) + "\n"
print(prediction)

# Predicts smallConv first, crowdConv second
label = predictOutcome(model, "melspec_files/" + "ZOOM0008393.png")
prediction = ""
for key, value in label.items():
    prediction += str(key) + ":" + str(value) + "\n"
print(prediction)

# Correct prediction
label = predictOutcome(model, "melspec_files/" + "ZOOM00082458.png")
prediction = ""
for key, value in label.items():
    prediction += str(key) + ":" + str(value) + "\n"
print(prediction)

# Correct prediction
label = predictOutcome(model, "melspec_files/" + "ZOOM00081699.png")
prediction = ""
for key, value in label.items():
    prediction += str(key) + ":" + str(value) + "\n"
print(prediction)

# Correct prediction
label = predictOutcome(model, "melspec_files/" + "ZOOM00061039.png")
prediction = ""
for key, value in label.items():
    prediction += str(key) + ":" + str(value) + "\n"
print(prediction)

"""Acoustic Class 1 : LargeConv"""

# Correct prediction
label = predictOutcome(model, "melspec_files/" + "ZOOM0013198.png")
prediction = ""
for key, value in label.items():
    prediction += str(key) + ":" + str(value) + "\n"
print(prediction)

# Correct prediction
label = predictOutcome(model, "melspec_files/" + "ZOOM00128.png")
prediction = ""
for key, value in label.items():
    prediction += str(key) + ":" + str(value) + "\n"
print(prediction)

# Correct prediction
label = predictOutcome(model, "melspec_files/" + "ZOOM001388.png")
prediction = ""
for key, value in label.items():
    prediction += str(key) + ":" + str(value) + "\n"
print(prediction)

# Correct prediction
label = predictOutcome(model, "melspec_files/" + "ZOOM00088.png")
prediction = ""
for key, value in label.items():
    prediction += str(key) + ":" + str(value) + "\n"
print(prediction)

# Correct prediction
label = predictOutcome(model, "melspec_files/" + "ZOOM00081001.png")
prediction = ""
for key, value in label.items():
    prediction += str(key) + ":" + str(value) + "\n"
print(prediction)

"""Acoustic Class 2 : Noise"""

# Incorrect prediction - Stimuli over Noise
label = predictOutcome(model, "melspec_files/" + "ZOOM0006152.png")
prediction = ""
for key, value in label.items():
    prediction += str(key) + ":" + str(value) + "\n"
print(prediction)

# Incorrect prediction - Crowd conv; should have been noise
label = predictOutcome(model, "melspec_files/" + "ZOOM0006189.png")
prediction = ""
for key, value in label.items():
    prediction += str(key) + ":" + str(value) + "\n"
print(prediction)

# Incorrect prediction - noise is overshadowed by some talking
label = predictOutcome(model, "melspec_files/" + "ZOOM0006289.png")
prediction = ""
for key, value in label.items():
    prediction += str(key) + ":" + str(value) + "\n"
print(prediction)

# Incorrect prediction
label = predictOutcome(model, "melspec_files/" + "ZOOM0006325.png")
prediction = ""
for key, value in label.items():
    prediction += str(key) + ":" + str(value) + "\n"
print(prediction)

# Incorrect prediction
label = predictOutcome(model, "melspec_files/" + "ZOOM0006326.png")
prediction = ""
for key, value in label.items():
    prediction += str(key) + ":" + str(value) + "\n"
print(prediction)

# Correct prediction
label = predictOutcome(model, "melspec_files/" + "ZOOM0006334.png")
prediction = ""
for key, value in label.items():
    prediction += str(key) + ":" + str(value) + "\n"
print(prediction)

# Correct prediction
label = predictOutcome(model, "melspec_files/" + "ZOOM00082372.png")
prediction = ""
for key, value in label.items():
    prediction += str(key) + ":" + str(value) + "\n"
print(prediction)

"""Acoustic Class 3 : Quiet"""

# Correct prediction
label = predictOutcome(model, "melspec_files/" + "ZOOM00062113.png")
prediction = ""
for key, value in label.items():
    prediction += str(key) + ":" + str(value) + "\n"
print(prediction)

# Incorrect - Predicts small conv first, which isn't a huge deal
label = predictOutcome(model, "melspec_files/" + "ZOOM0006191.png")
prediction = ""
for key, value in label.items():
    prediction += str(key) + ":" + str(value) + "\n"
print(prediction)

# Correct prediction
label = predictOutcome(model, "melspec_files/" + "ZOOM0006859.png")
prediction = ""
for key, value in label.items():
    prediction += str(key) + ":" + str(value) + "\n"
print(prediction)

"""Acoustic Class 4 : Small Conv"""

# Correct prediction
label = predictOutcome(model, "melspec_files/" + "ZOOM0006481.png")
prediction = ""
for key, value in label.items():
    prediction += str(key) + ":" + str(value) + "\n"
print(prediction)

# Correct prediction
label = predictOutcome(model, "melspec_files/" + "ZOOM00061214.png")
prediction = ""
for key, value in label.items():
    prediction += str(key) + ":" + str(value) + "\n"
print(prediction)

# Correct prediction
label = predictOutcome(model, "melspec_files/" + "ZOOM00082578.png")
prediction = ""
for key, value in label.items():
    prediction += str(key) + ":" + str(value) + "\n"
print(prediction)

# Correct prediction
label = predictOutcome(model, "melspec_files/" + "ZOOM0006940.png")
prediction = ""
for key, value in label.items():
    prediction += str(key) + ":" + str(value) + "\n"
print(prediction)

# Correct prediction
label = predictOutcome(model, "melspec_files/" + "ZOOM00061858.png")
prediction = ""
for key, value in label.items():
    prediction += str(key) + ":" + str(value) + "\n"
print(prediction)

"""Acoustic Class 5 : Stimuli"""

# Correct prediction
label = predictOutcome(model, "melspec_files/" + "ZOOM0011122.png")
prediction = ""
for key, value in label.items():
    prediction += str(key) + ":" + str(value) + "\n"
print(prediction)

# Correct prediction
label = predictOutcome(model, "melspec_files/" + "ZOOM001084.png")
prediction = ""
for key, value in label.items():
    prediction += str(key) + ":" + str(value) + "\n"
print(prediction)

# Correct prediction
label = predictOutcome(model, "melspec_files/" + "ZOOM001057.png")
prediction = ""
for key, value in label.items():
    prediction += str(key) + ":" + str(value) + "\n"
print(prediction)

# Correct prediction
label = predictOutcome(model, "melspec_files/" + "ZOOM0011296.png")
prediction = ""
for key, value in label.items():
    prediction += str(key) + ":" + str(value) + "\n"
print(prediction)

# Correct prediction
label = predictOutcome(model, "melspec_files/" + "ZOOM0011241.png")
prediction = ""
for key, value in label.items():
    prediction += str(key) + ":" + str(value) + "\n"
print(prediction)

"""Acoustic Class 7 : Wind"""

# Correct prediction
label = predictOutcome(model, "melspec_files/" + "ZOOM00082571.png")
prediction = ""
for key, value in label.items():
    prediction += str(key) + ":" + str(value) + "\n"
print(prediction)

# Correct prediction
label = predictOutcome(model, "melspec_files/" + "ZOOM00082575.png")
prediction = ""
for key, value in label.items():
    prediction += str(key) + ":" + str(value) + "\n"
print(prediction)

# Incorrect prediction - Stimuli first, wind second
label = predictOutcome(model, "melspec_files/" + "ZOOM00082577.png")
prediction = ""
for key, value in label.items():
    prediction += str(key) + ":" + str(value) + "\n"
print(prediction)

# Incorrect prediction - Stimuli first, wind second
label = predictOutcome(model, "melspec_files/" + "ZOOM0008686.png")
prediction = ""
for key, value in label.items():
    prediction += str(key) + ":" + str(value) + "\n"
print(prediction)

# Correct prediction
label = predictOutcome(model, "melspec_files/" + "ZOOM0011349.png")
prediction = ""
for key, value in label.items():
    prediction += str(key) + ":" + str(value) + "\n"
print(prediction)

# Make a prediction on a precut audio file
label = predictOutcome(model, "melspec_files/" + "ZOOM0008393.png")
prediction = ""
for key, value in label.items():
    prediction += str(key) + ":" + str(value) + "\n"
print(prediction)

# Testing against recorded microphone data
#mytype = '.wav'
#files_path = "audio_files/"
#file_name = "ZOOM0011204.wav"
#cutAll(files_path, file_name, mytype)

#v0 = predictOutcome(model, "melspec_files/ZOOM0011204.png")
#prediction = ""
#for key, value in v0.items():
#    prediction += str(key) + ":" + str(value) + "\n"
#print(prediction)
