import sys
from PyQt5 import QtWidgets,uic,QtGui,QtCore
from  PyQt5.QtWidgets import  QMainWindow,QMessageBox
from  cv2 import  cv2
import pyshine as ps
import numpy as np
from  PIL import  Image
import  time
import pyodbc
import os
from mtcnn_cv2 import MTCNN
face_detector =MTCNN()
demdt=0
demanh=0
imagepath = f"Data/raw/"
for path in os.listdir(imagepath):
    whatelse_path=os.path.join(imagepath,path)
    demdt+=1
    for sub_whatelse in os.listdir(whatelse_path):
        image_path2 = os.path.join(whatelse_path, sub_whatelse)
        if not os.path.isdir(whatelse_path.replace('raw', 'processed')):
            os.mkdir(whatelse_path.replace('raw', 'processed'))
        if image_path2.endswith('.jpg') or image_path2.endswith('.png') or image_path2.endswith('.jpeg') or image_path2.endswith('.JPG'):
            demanh+=1
            img = cv2.imread(image_path2)
            faces = face_detector.detect_faces(img)
            for face in faces:
                bounding_box = face['box']
                img_face = img[bounding_box[1]:bounding_box[1] + bounding_box[3],
                   bounding_box[0]:bounding_box[0] + bounding_box[2]]
                img_face = cv2.resize(img_face, (224, 224))
                cv2.imwrite(image_path2.replace('raw', 'processed').split('.jpg')[0]+f'.png', img_face)
print(demdt)
print(demanh)