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
con=pyodbc.connect('Driver={SQL Server};'
                   'SERVER=TRIEUAN\MASTERSQL;'
                   'Database=KhoaLuan;'
                   'Trusted_connection=yes')
cursor=con.cursor()
face_detector =MTCNN()
class frm_AnhSV(QMainWindow):
    def __init__(self,ID_TK,Quyen):
        super().__init__()
        self.ID_TK=ID_TK
        self.Quyen=Quyen
        uic.loadUi('LayAnhSV.ui',self)
        self.setWindowFlags(QtCore.Qt.CustomizeWindowHint)
        self.setFixedSize(1324, 729)
        self.lstAvatar = []
        self.lstAvatar.append(self.lbl_Anh1)
        self.lstAvatar.append(self.lbl_Anh2)
        self.lstAvatar.append(self.lbl_Anh3)
        self.lstAvatar.append(self.lbl_Anh4)
        self.lstAvatar.append(self.lbl_Anh5)
        self.lstAvatar.append(self.lbl_Anh6)
        self.lstAvatar.append(self.lbl_Anh7)
        self.lstAvatar.append(self.lbl_Anh8)
        self.lstAvatar.append(self.lbl_Anh9)
        self.lstAvatar.append(self.lbl_Anh10)
        self.lstAvatar.append(self.lbl_Anh11)
        self.lstAvatar.append(self.lbl_Anh12)
        self.lstAvatar.append(self.lbl_Anh13)
        self.lstAvatar.append(self.lbl_Anh14)
        self.lstAvatar.append(self.lbl_Anh15)
        self.lstAvatar.append(self.lbl_Anh16)
        self.lstAvatar.append(self.lbl_Anh17)
        self.lstAvatar.append(self.lbl_Anh18)
        self.lstAvatar.append(self.lbl_Anh19)
        self.lstAvatar.append(self.lbl_Anh20)
        self.Slider_brightness.setEnabled(False)
        self.fi_ID.setEnabled(False)
        self.fi_HoTen.setEnabled(False)
        self.fi_ChuyenNganh.setEnabled(False)
        self.fi_Lop.setEnabled(False)
        self.btnCapture.setEnabled(False)
        self.btnAvatar.setEnabled(False)
        self.btnSaveDB.setEnabled(False)
        self.btnWebCam.clicked.connect(self.OpenCam)
        self.btnCapture.clicked.connect(self.GetFace)
        self.btn_Exit.clicked.connect(self.Exit)
        self.btnSaveDB.clicked.connect(self.SaveDB)
        self.btnAvatar.clicked.connect(self.GetAvatar)
        self.Slider_brightness.valueChanged['int'].connect(self.brightness_value)
    def GetAvatar(self):
        image = cv2.resize(self.frame, (133, 166))
        img = QtGui.QImage(image, image.shape[1], image.shape[0], image.strides[0],
                           QtGui.QImage.Format_RGB888)
        self.lbl_Avatar.setPixmap(QtGui.QPixmap.fromImage(img))
        self.imgAvatar = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

    def SaveDB(self):
        try:
            for i in range(20):
                imagepath=f"Data/raw/{self.fi_ID.text()}/"
                if not os.path.isdir(imagepath):
                    os.mkdir(imagepath)
                cv2.imwrite("Data/raw/"f"{self.fi_ID.text()}/"  + f"{self.fi_ID.text()}" + f"_{i}.jpg",self.lstImage[i])
                whatelse_path="Data/raw/"f"{self.fi_ID.text()}/"
                if not os.path.isdir(whatelse_path.replace('raw', 'processed')):
                    os.mkdir(whatelse_path.replace('raw', 'processed'))
                if not os.path.isdir(whatelse_path.replace('raw', 'final')):
                    os.mkdir(whatelse_path.replace('raw', 'final'))
                # faces = face_detector.detectMultiScale(self.lstImage[i], 1.3, 4)
                # for (x, y, w, h) in faces:
                #     # vẽ khung
                #     cv2.rectangle(self.lstImage[i], (x, y), (x + w, y + h), (0, 255, 0), 3)
                #     # cắt gương mặt
                #     img_face = cv2.resize(self.lstImage[i][y + 3:y + h - 3, x + 3:x + w - 3], (224, 224))
                faces = face_detector.detect_faces(self.lstImage[i])
                for face in faces:
                    bounding_box = face['box']
                    img_face = self.lstImage[i][bounding_box[1]:bounding_box[1] + bounding_box[3],
                            bounding_box[0]:bounding_box[0] + bounding_box[2]]
                    img_face = cv2.resize(img_face, (224, 224))
                    cv2.imwrite("Data/processed/"f"{self.fi_ID.text()}/"  + f"{self.fi_ID.text()}" + f"_{i}.jpg", img_face)
                    cv2.imwrite("Data/final/"f"{self.fi_ID.text()}/" + f"{self.fi_ID.text()}" + f"_{i}.jpg",
                                img_face)
            cv2.imwrite('Avatar/'+f'{self.fi_ID.text()}.png', self.imgAvatar)
            cursor.execute(f"update SINHVIEN SET HINHANH='{self.fi_ID.text()}.png' Where MASV='{self.fi_ID.text()}'")
            con.commit()
            msg = QMessageBox()
            msg.setIcon(QMessageBox.NoIcon)
            msg.setWindowTitle("Thông báo")
            msg.setText("Lưu thành công")
            result = msg.exec_()
        except:
            msg = QMessageBox()
            msg.setIcon(QMessageBox.Warning)
            msg.setWindowTitle("Thông báo")
            msg.setText("Lưu không thành công")
            msg.setStandardButtons(QMessageBox.Ok )
            result = msg.exec_()

    def ktTonTai(self):
        try:
            image = np.array(Image.open(f"Avatar/{self.fi_ID.text()}.png"))
            return  True
        except:
            return  False
    def Exit(self):
        if self.ktTonTai()==False:
            msg = QMessageBox()
            msg.setIcon(QMessageBox.Warning)
            msg.setWindowTitle("Thông báo")
            msg.setText("Bạn có muốn lưu hình ảnh không??")
            msg.setStandardButtons(QMessageBox.Ok | QMessageBox.No)
            result = msg.exec_()
            if result==QMessageBox.No:
                self.t=0
                from main import MAIN
                fr = MAIN(self.ID_TK,self.Quyen)
                fr.show()
                self.hide()
                self.t=0
            elif result==QMessageBox.Ok:
                try:
                    self.SaveDB()
                except:
                    pass
                from main import MAIN
                fr = MAIN(self.ID_TK, self.Quyen)
                fr.show()
                self.hide()
                self.t = 0
        else:
            from main import MAIN
            fr = MAIN(self.ID_TK, self.Quyen)
            fr.show()
            self.hide()
            self.t = 0


    def GetFace(self):
        if self.countAvatar < 20:
            self.cutFace(self.frame, self.countAvatar)
            self.countAvatar+=1


    def cutFace(self,image,i):
        imageluu = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        self.lstImage[i] = imageluu
        image = cv2.resize(image, (143, 97))

        img = QtGui.QImage(image, image.shape[1], image.shape[0], image.strides[0],
                                   QtGui.QImage.Format_RGB888)
        self.lstAvatar[i].setPixmap(QtGui.QPixmap.fromImage(img))


    def brightness_value(self,value):
        self.brightness_value_now=value
        self.changeBrightness(self.brightness_value_now)
    def changeBrightness(self,value):
        self.cam.set(cv2.CAP_PROP_BRIGHTNESS,value)
    def OpenCam(self):
        self.Slider_brightness.setEnabled(True)
        self.brightness_value_now=0
        self.btnWebCam.setEnabled(False)
        self.btnCapture.setEnabled(True)
        self.btnAvatar.setEnabled(True)
        self.btnSaveDB.setEnabled(True)
        self.lstImage=[[9]]*20
        self.countAvatar = 0
        self.cam=cv2.VideoCapture(0)
        while True:
            Ok,self.frame=self.cam.read()
            self.frame = cv2.cvtColor(self.frame, cv2.COLOR_BGR2RGB)

            self.update()
            self.t=1
            if cv2.waitKey(1)==ord('q') or self.t==0:
                break
        self.cam.release()
        cv2.destroyAllWindows()
    def update(self):
        self.setPhoto(self.frame)

    def setPhoto(self,image):
        image = cv2.resize(image, (554, 518))
        img = QtGui.QImage(image, image.shape[1], image.shape[0], image.strides[0],
                           QtGui.QImage.Format_RGB888)  # tổng số pixel quét của ảnh
        self.lbl_Cam.setPixmap(QtGui.QPixmap.fromImage(img))


