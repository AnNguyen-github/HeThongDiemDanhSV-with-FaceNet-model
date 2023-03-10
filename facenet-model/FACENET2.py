import shutil
#GIAO DIỆN

#tính toán đại số
import  numpy as np
from numpy import expand_dims
#thao tác với CSDL
import os
from PIL import Image
import pickle
from cv2 import cv2
from keras.models import load_model
import time
# import tensorflow as tf
# import keras
import  matplotlib.pyplot as plt
folder = ('processed/')
database = {}
MyFaceNet = load_model("facenet_keras.h5")
# for filename in os.listdir(folder):
#     path = folder +"/"+ filename
#     for filename2 in os.listdir(path):
#         gbr1 = cv2.imread(path + "/" + filename2)
#         face = cv2.resize(gbr1, (160, 160))
#         face = face.astype('float32')
#         mean, std = face.mean(), face.std()
#         face = (face - mean) / std
#         face = expand_dims(face, axis=0)
#         signature = MyFaceNet.predict(face)
#         database[os.path.splitext(filename)[0]] = signature
# myfile = open("data.pkl", "wb")
# pickle.dump(database, myfile)
# myfile.close()

myfile = open("data.pkl", "rb")
database = pickle.load(myfile)
myfile.close()
face=cv2.imread("processed/2001180069/2001180069_ngu1.png")
face=cv2.cvtColor(face,cv2.COLOR_BGR2RGB)
cuttedFace=face
cuttedFace = cv2.resize(cuttedFace, (160, 160))
mean, std = cuttedFace.mean(), cuttedFace.std()
cuttedFace= (cuttedFace - mean) / std
cuttedFace= expand_dims(cuttedFace, axis=0)
signature = MyFaceNet.predict(cuttedFace)
min_dist = 100
identity = ' '
for key, value in database.items():
    dist = np.linalg.norm(value - signature)
    if dist < min_dist:
        min_dist = dist
        identity = key

print(identity)
plt.subplot(1, 1, 1)
plt.imshow(face)
plt.title( identity )
plt.axis("off")
plt.show()
