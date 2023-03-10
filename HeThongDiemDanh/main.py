import shutil
#GIAO DIỆN
from  PyQt5.QtWidgets import QApplication,QMessageBox, QMainWindow
from  PyQt5 import  uic,QtWidgets,QtCore,QtGui
import  pyshine as ps
from PyQt5.QtCore import QTimer
# import  sys

#tính toán đại số
import  numpy as np
from numpy import expand_dims
#thao tác với CSDL
import pyodbc
import os
from PIL import Image
import pickle

import time

#GỌI CAM
from  cv2 import cv2

#PHÁT HIỆN KHUÔN MẶT
from mtcnn_cv2 import MTCNN
from keras.models import load_model

from PyQt5.QtGui import  QFont

from anhSV import frm_AnhSV
# import tensorflow as tf
# import keras
import  matplotlib.pyplot as plt
# from keras.models import Sequential
# from keras.layers import Conv2D,MaxPooling2D,Dense,Flatten,Dropout
# from tensorflow.keras.layers import BatchNormalization
# from keras.models import load_model
# from keras_preprocessing import image
# from tensorflow.keras.preprocessing.image import ImageDataGenerator

from login import  frm_Login

#KẾT NỐI CSDL
con=pyodbc.connect('Driver={SQL Server};'
                   'SERVER=TRIEUAN\MASTERSQL;'
                   'Database=KhoaLuan;'
                   'Trusted_connection=yes')
cursor=con.cursor()

#GỌI HÀM MTCNN
face_detector = MTCNN()

#LOAD MODEL FACENET
MyFaceNet = load_model("facenet_keras.h5")

tiet_gio={"1":"7:00","2":"7:45","3":"8:35","4":"9:25","5":"10:15","6":"11:00",
          "7":"12:30","8":"13:15","9":"13:50","10":"14:50","11":"15:35","12":"16:15",
          "13":"18:00","14":"18:45","15":"19:30","16":"20:10","17":"21:00"}

class MAIN(QMainWindow):
    def __init__(self,ID_TK,Quyen):
        super().__init__()
        uic.loadUi("main.ui",self)
        self.btnSinhVien.setIcon(QtGui.QIcon("Image_Gui/graduated.png"))
        self.btnMonHoc.setIcon(QtGui.QIcon("Image_Gui/education.png"))
        self.btnDiemDanh.setIcon(QtGui.QIcon("Image_Gui/checked.png"))
        self.btnGiangVien.setIcon(QtGui.QIcon("Image_Gui/presenter.png"))
        self.ID_TK=ID_TK
        self.Quyen=Quyen
        self.setFixedSize(1519,742)
        self.show()
        self.login=frm_Login()
        self.login.hide()
        self.TenTK =""
        self.font=QFont()
        if self.Quyen=="GV" or self.Quyen=="AD":
            cursor.execute(f"SELECT TENGV FROM GIANGVIEN WHERE MAGV='{self.ID_TK}'")
            data = cursor.fetchall()
            self.TenTK=data[0][0]
        else:
            cursor.execute(f"SELECT TENSV FROM SINHVIEN WHERE MASV='{self.ID_TK}'")
            data = cursor.fetchall()
            self.TenTK = data[0][0]
        self.label_25.setText(self.TenTK)
        if  self.Quyen=="AD":
            self.stackedWidget.setCurrentWidget(self.page_SinhVien)
            self.loadTKGV()
        elif self.Quyen=="SV":
            self.menuSaoLuu.menuAction().setVisible(False)
            self.stackedWidget.setCurrentWidget(self.page_TKSV)
            self.loadTKSV()
            self.btnGiangVien.setText("Lịch Học")
            self.loadTTDiemDanh()
            self.loadTKBSV()
            self.LoadMonHoc_SV()
        elif self.Quyen=="GV":
            self.menuSaoLuu.menuAction().setVisible(False)
            self.stackedWidget.setCurrentWidget(self.page_TKGV)
            self.btnSinhVien.setText("Lịch Dạy")
            self.loadTKGV()
        self.setStysheetBtn()
        self.btn_DangXuat.setIcon(QtGui.QIcon(f"Avatar/{self.ID_TK}.png"))
        self.mnu_DoiMatKhau.triggered.connect(self.Page_DoiMatKhau)
        self.mnu_DangXuat.triggered.connect(self.DangXuat)
        self.mnu_ThongTin.triggered.connect(self.XemTTTK)
        self.mnu_SaoLuu_2.triggered.connect(self.SaoLuu)
        self.mnu_KhoiPhuc_2.triggered.connect(self.KhoiPhuc)
        self.mnu_GioiThieu.triggered.connect(self.GioiThieu)
        self.btnSinhVien.clicked.connect(self.Page_SinhVien)
        self.btnMonHoc.clicked.connect(self.Page_MonHoc)
        self.btnDiemDanh.clicked.connect(self.loadPageDD)
        self.btnGiangVien.clicked.connect(self.Page_GiangVien)
        self.btn_DangXuat.clicked.connect(self.DangXuat)
        self.btn_KhoiPhuc.clicked.connect(self.XacNhanKP)
        self.progressBar_KhoiPhuc.setVisible(False)
        timer = QTimer(self)
        timer.timeout.connect(self.GetThoiGian)
        timer.start(100)

        ######################################################################################################
        # page môn học
        if self.Quyen == "GV":
            self.loadMonHocGV()
        else:
            self.KhoiTaoCboHK()
            self.loadMonHoc()
            self.KhoiTaoMH()
        self.themlhp=False
        self.themmh=False
        self.tbl_MonHoc_2.clicked.connect(self.GetMonHoc)
        self.tbl_LopHocPhan_2.clicked.connect(self.GetLopHocPhan)
        self.tbl_DSSV_2.clicked.connect(self.GetSV_MonHoc)
        self.btn_ThemMH_2.clicked.connect(self.ThemMH)
        self.btn_HuyLopHoc_2.clicked.connect(self.HuyMH)
        self.btn_SuaMH_2.clicked.connect(self.SuaMH)
        self.btn_LuuMH_2.clicked.connect(self.LuuMH)
        self.btn_XoaLopHoc_2.clicked.connect(self.XoaMH)
        self.btn_ThemLopHP_2.clicked.connect(self.ThemLHP)
        self.btn_HuyLHP_2.clicked.connect(self.HuyLHP)
        self.btn_SuaLopHP_2.clicked.connect(self.SuaLHP)
        self.btn_LuuLHP_2.clicked.connect(self.LuuLHP)
        self.btn_XoaLopHP_2.clicked.connect(self.XoaLHP)
        self.btn_TimSV_2.clicked.connect(self.TimSVThemLop)
        self.btn_ThemSV_2.clicked.connect(self.ThemSVVaoLop)
        self.btn_XoaSV_2.clicked.connect(self.XoaSVKhoiLop)
        self.btn_TimMH_2.clicked.connect(self.TimMonHoc)
        self.btn_AllMH_2.clicked.connect(self.AllMH)
        # self.btn_DatLichHoc_2.clicked.connect(lambda: self.stackedWidget.setCurrentWidget(self.page_LichHoc))
        self.btn_DatLichHoc_2.clicked.connect(self.DatLichHoc)
        self.btn_BackPageMH_4.clicked.connect(self.BackPageMH)
        self.cbo_hocki.currentIndexChanged.connect(self.ChangeHK)
        ######################################################################################################
        #page sinh viên
        self.anhSV = frm_AnhSV(self.ID_TK,self.Quyen)
        self.btn_LayAnhSV.clicked.connect(self.LayAnh)
        if self.Quyen == "GV":
            self.btn_ThemSV.setVisible(False)
            self.btnLuuSV.setVisible(False)
            self.btn_SuaSV.setVisible(False)
            self.btnHuySV.setVisible(False)
            self.btn_XoaSV.setVisible(False)
            self.btn_LamMoiSV.setVisible(False)
            self.btn_LayAnhSV.setVisible(False)
            self.groupBox_16.setVisible(False)
            self.btn_TrainingData.setVisible(False)
            # self.btn_SuaLop.setVisible(False)
            # self.btn_HuyLop.setVisible(False)
            # self.btn_XoaLop.setVisible(False)
            self.loadData()
            self.KhoiTaoCombobox()
        else:
            self.loadData()
            self.KhoiTao()
            self.KhoiTaoCombobox()
        self.them = False
        self.themlop = False
        self.tbl_SinhVien.clicked.connect(self.GetSV)
        self.tbl_Lop.clicked.connect(self.GetLop)
        self.btn_AllSV.clicked.connect(self.GetAllSV)
        self.btn_TimSV.clicked.connect(self.TimSV)
        self.btn_TimLop.clicked.connect(self.TimLop)
        self.btn_ThemSV.clicked.connect(self.themSV)
        self.btn_LamMoiSV.clicked.connect(self.LamMoiSV)
        self.btnLuuSV.clicked.connect(self.LuuSV)
        self.btnHuySV.clicked.connect(self.HuySV)
        self.btn_SuaSV.clicked.connect(self.SuaSV)
        self.btn_XoaSV.clicked.connect(self.XoaSV)
        self.btn_ThemLop.clicked.connect(self.ThemLop)
        self.btn_SuaLop.clicked.connect(self.SuaLop)
        self.btn_HuyLop.clicked.connect(self.HuyLop)
        self.btn_LuuLop.clicked.connect(self.LuuLop)
        self.btn_XoaLop.clicked.connect(self.XoaLop)
        self.btn_TrainingData.clicked.connect(self.Training)
        self.progressBar.setValue(0)
        self.progressBar.setVisible(False)
        ######################################################################################################
        # page buổi học
        self.KhoiTaoBH()
        self.btn_ThemBH_4.clicked.connect(self.ThemBH)
        self.thembh=False
        self.btn_HuyBH_4.clicked.connect(self.HuyBH)
        self.btn_SuaBH_4.clicked.connect(self.SuaBH)
        self.tbl_DSBuoiHoc_4.clicked.connect(self.GetBH)
        self.btn_LuuBH_4.clicked.connect(self.LuuBH)
        self.btn_XoaBH_4.clicked.connect(self.XoaBH)
        self.btn_ChiTietDD_4.clicked.connect(self.ChiTietDD)
        ######################################################################################################
        # page lịch dạy
        self.btn_DiemDanh_6.clicked.connect(self.OpenDiemDanh)
        self.loadThoiKhoaBieu()
        self.tbl_DSLopHP_6.clicked.connect(self.GetLopHPDD)
        self.tbl_DSBuoiHoc_6.clicked.connect(self.GetBuoiHocDD)
        ######################################################################################################
        # page điểm danh
        self.btn_MoCam_3.clicked.connect(self.OpenCamDiemDanh)
        self.btn_DongCam_3.clicked.connect(self.DongCam)
        self.btn_BackPageTKB_3.clicked.connect(self.BackLichDay)
        self.btn_SaveDD_3.clicked.connect(self.SaveDD)
        ######################################################################################################
        # page giảng viên
        self.loadPageGV()
        self.themgv=False
        self.tbl_DSGV_7.clicked.connect(self.GetGV_7)
        self.btn_ThemGV_7.clicked.connect(self.ThemGV)
        self.btn_SuaGV_7.clicked.connect(self.SuaGV)
        self.btn_HuyGV_7.clicked.connect(self.HuyGV)
        self.btn_TimGV_7.clicked.connect(self.TimGV)
        self.btn_ChonAnhGV_7.clicked.connect(self.ChonAnhGV)
        self.btn_LuuGV_7.clicked.connect(self.LuuGV)
        self.btn_XoaGV_7.clicked.connect(self.XoaGV)
        ######################################################################################################
        # page chi tiết điểm danh
        self.tbl_DSBuoiHoc_8.clicked.connect(self.GetDD)
        self.btn_BackPageBuoiHoc.clicked.connect(lambda: self.stackedWidget.setCurrentWidget(self.page_LichHoc))
        self.tbl_ChiTietDD_8.clicked.connect(self.GetHADD)
        ######################################################################################################
        #page tk sinh viên
        self.btn_SuaSV_9.clicked.connect(self.SuaTKSV)
        self.btn_HuySV_9.clicked.connect(self.HuyTKSV)
        self.btn_LuuSV_9.clicked.connect(self.LuuTKSV)
        self.btn_DoiMatKhau_9.clicked.connect(self.Page_DoiMatKhau)
        ######################################################################################################
        # page MÔN học sinh viên
        self.tbl_MonHoc_11.clicked.connect(self.GetMonHocSV)
        self.tbl_LopHocPhan_11.clicked.connect(self.GetTTLHPSV)
        self.btn_DatLichHoc_3.clicked.connect(self.GetLichHocLHP)
        self.btn_TimMH_11.clicked.connect(self.TimMonHoc_11)
        self.btn_AllMH_11.clicked.connect(self.AllMH_11)
        self.btn_DangKy_11.clicked.connect(self.DangKiMH_11)

        ######################################################################################################
        # page đổi mật khẩu
        self.btn_XacNhanMK.clicked.connect(self.DoiMatKhau)


        ######################################################################################################
        # page TKGV
        self.btn_SuaGV_10.clicked.connect(self.SuaTKGV)
        self.btn_HuyGV_10.clicked.connect(self.HuyTKGV)
        self.btn_LuuGV_10.clicked.connect(self.LuuTKGV)
        self.btn_DoiMatKhau_10.clicked.connect(self.Page_DoiMatKhau)
        ######################################################################################################
        # page MonHocGV
        self.cbo_hocki_13.currentIndexChanged.connect(self.changeHKGV)
        self.tbl_MonHoc_13.clicked.connect(self.GetMonHoc_GV)
        self.tbl_LopHocPhan_13.clicked.connect(self.GetLopHocPhan_GV)
        self.tbl_DSSV_13.clicked.connect(self.GetSV_MonHoc_GV)
        self.btn_TimSV_13.clicked.connect(self.TimSV_GV)
        self.btn_AllMH_13.clicked.connect(self.AllMH_GV)
        self.btn_TimMH_13.clicked.connect(self.TimMonHoc_GV)
        self.btn_DatLichHoc_13.clicked.connect(self.GetLichHoc_GV)
        self.cbo_hocki_11.currentIndexChanged.connect(self.ChangeHK_SV)
        self.KhoiTaoMHGV()
    ######################################################################################################
    ######################################################################################################
    #page MonHocGV
    def KhoiTaoMHGV(self):
        self.fi_IDMonHoc_13.setEnabled(False)
        self.fi_SoTC_13.setEnabled(False)
        self.fi_TietLT_13.setEnabled(False)
        self.fi_TenMonHoc_13.setEnabled(False)
        self.fi_TongSoTiet_13.setEnabled(False)
        self.fi_TietTH_13.setEnabled(False)
        self.fi_IDLop_13.setEnabled(False)
        self.fi_SiSo_13.setEnabled(False)
        self.fi_NgayBatDau_13.setEnabled(False)
        self.fi_NgayKetThuc_13.setEnabled(False)
        self.fi_IDSV_13.setEnabled(False)
        self.fi_HoTenSV_13.setEnabled(False)
        self.fi_LopSV_13.setEnabled(False)
        self.fi_KhoaSV_13.setEnabled(False)

    def GetLichHoc_GV(self):
        if self.fi_IDLop_13.text()=="":
            msg = QMessageBox()
            msg.setIcon(QMessageBox.Warning)
            msg.setWindowTitle("Thông báo")
            msg.setText("Vui lòng chọn lớp học muốn xem lịch học!!")
            msg.setStandardButtons(QMessageBox.Ok)
            msg.exec_()
        else:
            self.fi_IDLHP_4.setText(self.fi_IDLop_13.text())
            self.fi_MH_4.setText(self.fi_TenMonHoc_13.text())
            self.fi_GiangVien_4.setText(self.TenTK)
            self.stackedWidget.setCurrentWidget(self.page_LichHoc)
            self.loadBuoiHoc()
            if self.Quyen=="GV":
                self.btn_ThemBH_4.setVisible(False)
                self.btn_SuaBH_4.setVisible(False)
                self.btn_XoaBH_4.setVisible(False)
    def AllMH_GV(self):
        cursor.execute(f"SELECT MAHK FROM HOCKI WHERE TENHK='{self.cbo_hocki_13.currentText()}'")
        data = cursor.fetchall()
        row = 0
        lstMH = []
        for row1 in cursor.execute(
                f"select distinct MONHOC.MAMH,TENMH,SOTC from MONHOC,"
                f"LOPMONHOC,GIANGVIEN WHERE MONHOC.MAMH=LOPMONHOC.MAMH AND"
                f" LOPMONHOC.MAHK={data[0][0]} AND LOPMONHOC.MAGV=GIANGVIEN.MAGV AND GIANGVIEN.MAGV='{self.ID_TK}'"):
            MH = {}
            MH["ID"] = row1[0]
            MH["name"] = row1[1]
            MH["soTC"] = row1[2]
            lstMH.append(MH)
        self.tbl_MonHoc_13.setColumnWidth(0, 150)
        self.tbl_MonHoc_13.setColumnWidth(1, 280)
        self.tbl_MonHoc_13.setColumnWidth(2, 225)
        self.tbl_MonHoc_13.setRowCount(len(lstMH))
        for mh in lstMH:
            self.tbl_MonHoc_13.setItem(row, 0, QtWidgets.QTableWidgetItem(mh["ID"]))
            self.tbl_MonHoc_13.setItem(row, 1, QtWidgets.QTableWidgetItem(mh["name"]))
            self.tbl_MonHoc_13.setItem(row, 2, QtWidgets.QTableWidgetItem(str(mh["soTC"])))
            row += 1
    def TimMonHoc_GV(self):
        cursor.execute(f"SELECT MAHK FROM HOCKI WHERE TENHK='{self.cbo_hocki_13.currentText()}'")
        data = cursor.fetchall()
        if self.cbo_TimMH_13.currentText()=="ID":
            row = 0
            self.lstMH = []
            for row1 in cursor.execute(f"select distinct MONHOC.MAMH,TENMH,SOTC from MONHOC,"
                f"LOPMONHOC,GIANGVIEN WHERE MONHOC.MAMH=LOPMONHOC.MAMH AND"
                f" LOPMONHOC.MAHK={data[0][0]} AND LOPMONHOC.MAGV=GIANGVIEN.MAGV AND GIANGVIEN.MAGV='{self.ID_TK}' AND MONHOC.MAMH='{self.txt_TimMH_13.text()}'"):
                MH = {}
                MH["ID"] = row1[0]
                MH["name"] = row1[1]
                MH["soTC"] = row1[2]
                self.lstMH.append(MH)
            self.tbl_MonHoc_13.setColumnWidth(0, 150)
            self.tbl_MonHoc_13.setColumnWidth(1, 280)
            self.tbl_MonHoc_13.setColumnWidth(2, 225)
            self.tbl_MonHoc_13.setRowCount(len(self.lstMH))
            for mh in self.lstMH:
                self.tbl_MonHoc_13.setItem(row, 0, QtWidgets.QTableWidgetItem(mh["ID"]))
                self.tbl_MonHoc_13.setItem(row, 1, QtWidgets.QTableWidgetItem(mh["name"]))
                self.tbl_MonHoc_13.setItem(row, 2, QtWidgets.QTableWidgetItem(str(mh["soTC"])))
                row += 1
        elif self.cbo_TimMH_13.currentText()=="Tên Môn Học":
            row = 0
            self.lstMH = []
            for row1 in cursor.execute(f"select distinct MONHOC.MAMH,TENMH,SOTC from MONHOC,"
                f"LOPMONHOC,GIANGVIEN WHERE MONHOC.MAMH=LOPMONHOC.MAMH AND"
                f" LOPMONHOC.MAHK={data[0][0]} AND LOPMONHOC.MAGV=GIANGVIEN.MAGV AND GIANGVIEN.MAGV='{self.ID_TK}' AND TENMH LIKE N'%{self.txt_TimMH_13.text()}%'"):
                MH = {}
                MH["ID"] = row1[0]
                MH["name"] = row1[1]
                MH["soTC"] = row1[2]
                self.lstMH.append(MH)
            self.tbl_MonHoc_13.setColumnWidth(0, 150)
            self.tbl_MonHoc_13.setColumnWidth(1, 280)
            self.tbl_MonHoc_13.setColumnWidth(2, 225)
            self.tbl_MonHoc_13.setRowCount(len(self.lstMH))
            for mh in self.lstMH:
                self.tbl_MonHoc_13.setItem(row, 0, QtWidgets.QTableWidgetItem(mh["ID"]))
                self.tbl_MonHoc_13.setItem(row, 1, QtWidgets.QTableWidgetItem(mh["name"]))
                self.tbl_MonHoc_13.setItem(row, 2, QtWidgets.QTableWidgetItem(str(mh["soTC"])))
                row += 1
    def TimSV_GV(self):
        for row in cursor.execute(f"select * from SINHVIEN,KHOA,LOP WHERE SINHVIEN.MASV='{self.txt_TimSV_13.text()}' "
                                  f"AND SINHVIEN.MALOP=LOP.MALOP AND LOP.MAKHOA=KHOA.MAKHOA"):
            self.fi_IDSV_13.setText(row[0])
            self.fi_HoTenSV_13.setText(row[1])
            self.fi_LopSV_13.setText(row[10])
            self.fi_KhoaSV_13.setText(row[17])
    def GetSV_MonHoc_GV(self):
        row = self.tbl_DSSV_13.currentIndex().row()
        ms = self.tbl_DSSV_13.item(row, 0).text()
        for row in cursor.execute(f"select * from SINHVIEN,KHOA,LOP,CHUYENNGANH WHERE SINHVIEN.MASV='{ms}' "
                                  f"AND LOP.MAKHOA=KHOA.MAKHOA AND SINHVIEN.MALOP=LOP.MALOP AND SINHVIEN.MACN=CHUYENNGANH.MACN "):
            self.fi_IDSV_13.setText(row[0])
            self.fi_HoTenSV_13.setText(row[1])
            self.fi_LopSV_13.setText(row[10])
            self.fi_KhoaSV_13.setText(row[17])


    def GetLopHocPhan_GV(self):
        row = self.tbl_LopHocPhan_13.currentIndex().row()
        ms = self.tbl_LopHocPhan_13.item(row, 0).text()
        for row in cursor.execute(
                f"select * from LOPMONHOC,GIANGVIEN WHERE LOPMONHOC.MAGV=GIANGVIEN.MAGV AND MALOPMH='{ms}'"):
            self.fi_IDLop_13.setText(row[0])
            self.fi_SiSo_13.setText(str(row[5]))
            self.fi_NgayBatDau_13.setDate(
                QtCore.QDate(int(row[2].split('-')[0]), int(row[2].split('-')[1]), int(row[2].split('-')[2])))
            self.fi_NgayKetThuc_13.setDate(
            QtCore.QDate(int(row[3].split('-')[0]), int(row[3].split('-')[1]), int(row[3].split('-')[2])))
        # load sv trong lớp học phần
        row = 0
        self.lstSVLHP = []
        for row1 in cursor.execute(
                    f"select * from CHITIETLHP,SINHVIEN WHERE CHITIETLHP.MASV=SINHVIEN.MASV AND CHITIETLHP.MALOPMH='{ms}'"):
            LHP = {}
            LHP["ID"] = row1[2]
            LHP["name"] = row1[3]
            self.lstSVLHP.append(LHP)
        self.tbl_DSSV_13.setColumnWidth(0, 110)
        self.tbl_DSSV_13.setColumnWidth(1, 200)
        self.tbl_DSSV_13.setRowCount(len(self.lstSVLHP))
        for mh in self.lstSVLHP:
            self.tbl_DSSV_13.setItem(row, 0, QtWidgets.QTableWidgetItem(mh["ID"]))
            self.tbl_DSSV_13.setItem(row, 1, QtWidgets.QTableWidgetItem(mh["name"]))
            row += 1
    def GetMonHoc_GV(self):
        row = self.tbl_MonHoc_13.currentIndex().row()
        ms = self.tbl_MonHoc_13.item(row, 0).text()
        for row in cursor.execute(f"select * from MONHOC Where MAMH='{ms}'"):
            self.fi_IDMonHoc_13.setText(row[0])
            self.fi_TenMonHoc_13.setText(row[1])
            self.fi_SoTC_13.setText(str(row[2]))
            self.fi_TongSoTiet_13.setText(str(row[3]))
            self.fi_TietLT_13.setText(str(row[4]))
            self.fi_TietTH_13.setText(str(row[5]))

        #load các lớp học phần
        row = 0
        self.lstLHP = []
        for row1 in cursor.execute(f"select * from LOPMONHOC,GIANGVIEN WHERE LOPMONHOC.MAGV=GIANGVIEN.MAGV AND LOPMONHOC.MAMH='{ms}' AND GIANGVIEN.MAGV='{self.ID_TK}'"):
            LHP = {}
            LHP["ID"] = row1[0]
            LHP["name"] =str( row1[2])
            self.lstLHP.append(LHP)
        self.tbl_LopHocPhan_13.setColumnWidth(0, 90)
        self.tbl_LopHocPhan_13.setColumnWidth(1, 169)
        self.tbl_LopHocPhan_13.setRowCount(len(self.lstLHP))
        for mh in self.lstLHP:
            self.tbl_LopHocPhan_13.setItem(row, 0, QtWidgets.QTableWidgetItem(mh["ID"]))
            self.tbl_LopHocPhan_13.setItem(row, 1, QtWidgets.QTableWidgetItem(mh["name"]))
            row += 1
    def changeHKGV(self):
        cursor.execute(f"SELECT MAHK FROM HOCKI WHERE TENHK='{self.cbo_hocki_13.currentText()}'")
        data = cursor.fetchall()
        row = 0
        lstMH = []
        for row1 in cursor.execute(f"select distinct MONHOC.MAMH,TENMH,SOTC from MONHOC,LOPMONHOC,GIANGVIEN WHERE MONHOC.MAMH=LOPMONHOC.MAMH AND LOPMONHOC.MAHK={data[0][0]} AND LOPMONHOC.MAGV=GIANGVIEN.MAGV AND GIANGVIEN.MAGV='{self.ID_TK}'"):
            MH = {}
            MH["ID"] = row1[0]
            MH["name"] = row1[1]
            MH["soTC"] = row1[2]
            lstMH.append(MH)
        self.tbl_MonHoc_13.setColumnWidth(0, 150)
        self.tbl_MonHoc_13.setColumnWidth(1, 280)
        self.tbl_MonHoc_13.setColumnWidth(2, 225)
        self.tbl_MonHoc_13.setRowCount(len(lstMH))
        for mh in lstMH:
            self.tbl_MonHoc_13.setItem(row, 0, QtWidgets.QTableWidgetItem(mh["ID"]))
            self.tbl_MonHoc_13.setItem(row, 1, QtWidgets.QTableWidgetItem(mh["name"]))
            self.tbl_MonHoc_13.setItem(row, 2, QtWidgets.QTableWidgetItem(str(mh["soTC"])))
            row += 1
    def loadMonHocGV(self):
        self.cbo_hocki_13.clear()
        # Load combobox học kì
        for row1 in cursor.execute("select * from HOCKI ORDER BY  MAHK DESC"):
            self.cbo_hocki_13.addItem(row1[1])
        cursor.execute(f"SELECT MAHK FROM HOCKI WHERE TENHK='{self.cbo_hocki_13.currentText()}'")
        data = cursor.fetchall()
        #load môn học
        row = 0
        self.lstMH = []
        for row1 in cursor.execute(f"select distinct MONHOC.MAMH,TENMH,SOTC from MONHOC,LOPMONHOC,GIANGVIEN WHERE MONHOC.MAMH=LOPMONHOC.MAMH AND LOPMONHOC.MAHK={data[0][0]} AND LOPMONHOC.MAGV=GIANGVIEN.MAGV AND GIANGVIEN.MAGV='{self.ID_TK}'"):
            MH = {}
            MH["ID"] = row1[0]
            MH["name"] = row1[1]
            MH["soTC"] = row1[2]
            self.lstMH.append(MH)
        self.tbl_MonHoc_13.setColumnWidth(0, 150)
        self.tbl_MonHoc_13.setColumnWidth(1, 280)
        self.tbl_MonHoc_13.setColumnWidth(2, 225)
        self.tbl_MonHoc_13.setRowCount(len(self.lstMH))
        for mh in self.lstMH:
            self.tbl_MonHoc_13.setItem(row, 0, QtWidgets.QTableWidgetItem(mh["ID"]))
            self.tbl_MonHoc_13.setItem(row, 1, QtWidgets.QTableWidgetItem(mh["name"]))
            self.tbl_MonHoc_13.setItem(row, 2, QtWidgets.QTableWidgetItem(str(mh["soTC"])))
            row += 1
        self.cbo_TimMH_13.clear()
        self.cbo_TimMH_13.addItem("ID")
        self.cbo_TimMH_13.addItem("Tên Môn Học")

    ######################################################################################################
    # page lichDayGV
    def LoadLichDayGV(self):

        row = 0
        lstMH = []
        for row1 in cursor.execute(
                f"select TENMH,NGAYHOC,GIOBD,GIOKT,MAPH From BUOIHOC,CHITIETLHP,LOPMONHOC, MONHOC where BUOIHOC.MALOPMH=CHITIETLHP.MALOPMH "
                f"AND CHITIETLHP.MALOPMH=LOPMONHOC.MALOPMH AND LOPMONHOC.MAMH=MONHOC.MAMH "
                f"and LOPMONHOC.MAGV='{self.ID_TK}' group by TENMH,NGAYHOC,GIOBD,GIOKT,MAPH ORDER BY NGAYHOC"):
            MH = {}
            MH["mh"] = row1[0]
            y = str(row1[1]).split("-")[0]
            m = str(row1[1]).split("-")[1]
            d = str(row1[1]).split("-")[2]
            MH["ngay"] = d + "/" + m + "/" + y
            MH["bd"] = row1[2]
            MH["kt"] = row1[3]
            MH["phong"] = row1[4]
            lstMH.append(MH)
        self.tbl_LichDayGV.setColumnWidth(0, 280)
        self.tbl_LichDayGV.setColumnWidth(1, 150)
        self.tbl_LichDayGV.setColumnWidth(2, 225)
        self.tbl_LichDayGV.setColumnWidth(3, 280)
        self.tbl_LichDayGV.setColumnWidth(4, 235)
        self.tbl_LichDayGV.setRowCount(len(lstMH))
        for mh in lstMH:
            self.tbl_LichDayGV.setItem(row, 0, QtWidgets.QTableWidgetItem(mh["mh"]))
            self.tbl_LichDayGV.setItem(row, 1, QtWidgets.QTableWidgetItem(mh["ngay"]))
            self.tbl_LichDayGV.setItem(row, 2, QtWidgets.QTableWidgetItem(mh["bd"]))
            self.tbl_LichDayGV.setItem(row, 3, QtWidgets.QTableWidgetItem(mh["kt"]))
            self.tbl_LichDayGV.setItem(row, 4, QtWidgets.QTableWidgetItem(mh["phong"]))
            row += 1
    ######################################################################################################
    # page TKGV
    def LuuTKGV(self):

        if self.fi_HoTenGV_10.text() == "" or self.fi_SDT_10.text() == "" or self.fi_DDThuongTru_10.text() == "" or self.fi_DCTamTru_10.text() == ""  or self.fi_CMND_10.text() == "" or self.fi_DanToc_10.text() == "" or self.fi_TrinhDo_10.text() == "" or self.fi_Email_10.text() == "":
            msg = QMessageBox()
            msg.setIcon(QMessageBox.Warning)
            msg.setWindowTitle("Thông báo")
            msg.setText("Vui lòng nhập đầy đủ thông tin")
            msg.setStandardButtons(QMessageBox.Ok )
            result = msg.exec_()
        else:
            try:
                cursor.execute("SET DATEFORMAT DMY UPDATE GIANGVIEN "
                               "SET TENGV=?, SDT=?, NGAYSINH=?, CMND=?, DANTOC=?,TRINHDO=?,GIOITINH=?, EMAIL=?,DIACHITT=?, DCTAMTRU=? WHERE MAGV=?",
                               self.fi_HoTenGV_10.text(),
                               self.fi_SDT_10.text(), self.fi_NgaySinhGV_10.text(), self.fi_CMND_10.text(),
                               self.fi_DanToc_10.text(),
                               self.fi_TrinhDo_10.text(),
                               self.fi_GioiTinhGV_10.currentText(), self.fi_Email_10.text(), self.fi_DDThuongTru_10.text(),
                               self.fi_DCTamTru_10.text(),
                               self.fi_IDGV_10.text())
                con.commit()
                msg = QMessageBox()
                msg.setIcon(QMessageBox.NoIcon)
                msg.setWindowTitle("Thông báo")
                msg.setText("Cập nhật thông tin thành công")
                msg.setStandardButtons(QMessageBox.Ok)
                result = msg.exec_()
                self.loadTKGV()
            except:
                msg = QMessageBox()
                msg.setIcon(QMessageBox.Warning)
                msg.setWindowTitle("Thông báo")
                msg.setText("Lỗi")
                msg.setStandardButtons(QMessageBox.Ok)
                result = msg.exec_()
    def HuyTKGV(self):
        self.loadTKGV()
    def SuaTKGV(self):
        self.btn_LuuGV_10.setVisible(True)
        self.btn_HuyGV_10.setVisible(True)
        self.btn_SuaGV_10.setVisible(False)
        self.btn_DoiMatKhau_10.setVisible(False)
        self.fi_HoTenGV_10.setEnabled(True)
        self.fi_SDT_10.setEnabled(True)
        self.fi_DDThuongTru_10.setEnabled(True)
        self.fi_DCTamTru_10.setEnabled(True)
        self.fi_GioiTinhGV_10.setEnabled(True)
        self.fi_NgaySinhGV_10.setEnabled(True)
        self.fi_CMND_10.setEnabled(True)
        self.fi_DanToc_10.setEnabled(True)
        self.fi_TrinhDo_10.setEnabled(True)
        self.fi_Email_10.setEnabled(True)
    def loadTKGV(self):
        self.btn_LuuGV_10.setVisible(False)
        self.btn_HuyGV_10.setVisible(False)
        self.btn_SuaGV_10.setVisible(True)
        self.btn_DoiMatKhau_10.setVisible(True)
        self.fi_IDGV_10.setEnabled(False)
        self.fi_HoTenGV_10.setEnabled(False)
        self.fi_SDT_10.setEnabled(False)
        self.fi_Khoa_10.setEnabled(False)
        self.fi_DDThuongTru_10.setEnabled(False)
        self.fi_DCTamTru_10.setEnabled(False)
        self.fi_GioiTinhGV_10.setEnabled(False)
        self.fi_NgaySinhGV_10.setEnabled(False)
        self.fi_CMND_10.setEnabled(False)
        self.fi_DanToc_10.setEnabled(False)
        self.fi_TrinhDo_10.setEnabled(False)
        self.fi_Email_10.setEnabled(False)
        #load combobox giới tính
        self.fi_GioiTinhGV_10.clear()
        self.fi_GioiTinhGV_10.addItem("Nam")
        self.fi_GioiTinhGV_10.addItem("Nữ")
        self.fi_GioiTinhGV_10.addItem("Khác")
        for row in cursor.execute(f"select * from GIANGVIEN,KHOA WHERE MAGV='{self.ID_TK}' AND KHOA.MAKHOA=GIANGVIEN.MAKHOA"):
            self.fi_IDGV_10.setText(row[0])
            self.fi_HoTenGV_10.setText(row[1])
            self.fi_SDT_10.setText(row[2])
            self.fi_NgaySinhGV_10.setDate(
                QtCore.QDate(int(row[3].split('-')[0]), int(row[3].split('-')[1]), int(row[3].split('-')[2])))
            self.fi_CMND_10.setText(row[4])
            self.fi_DanToc_10.setText(row[5])
            self.fi_TrinhDo_10.setText(row[6])
            self.fi_GioiTinhGV_10.setCurrentText(row[7])
            self.fi_Email_10.setText(row[8])
            self.fi_DDThuongTru_10.setText(row[10])
            self.fi_DCTamTru_10.setText(row[11])
            self.fi_Khoa_10.setText(row[16])
            if row[12] == None:
                image = np.array(Image.open(f"Avatar/Who1.png"))
                self.image_GV = image
                image = cv2.resize(image, (171, 188))
                image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
                img = QtGui.QImage(image, image.shape[1], image.shape[0], image.strides[0],
                                   QtGui.QImage.Format_RGB888)  # tổng số pixel quét của ảnh
                self.lbl_AvatarGV_10.setPixmap(QtGui.QPixmap.fromImage(img))
            else:
                image = np.array(Image.open(f"Avatar/{row[12]}"))
                self.image_GV = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
                image = cv2.resize(image, (171, 188))
                img = QtGui.QImage(image, image.shape[1], image.shape[0], image.strides[0],
                                   QtGui.QImage.Format_RGB888)  # tổng số pixel quét của ảnh
                self.lbl_AvatarGV_10.setPixmap(QtGui.QPixmap.fromImage(img))
    ##########################################################################
    ############
    def loadTTDiemDanh(self):
        row = 0
        lstMH = []
        for row1 in cursor.execute(f"select MONHOC.TENMH,LOPMONHOC.MALOPMH from MONHOC,LOPMONHOC,CHITIETLHP Where MONHOC.MAMH=LOPMONHOC.MAMH"
                                   f" AND CHITIETLHP.MASV='{self.ID_TK}' AND CHITIETLHP.MALOPMH=LOPMONHOC.MALOPMH"):
            MH = {}
            MH["mh"] = row1[0]
            MH["lop"] = row1[1]
            lstMH.append(MH)
        self.tbl_ThongTinDDSV.setColumnWidth(0, 300)
        self.tbl_ThongTinDDSV.setColumnWidth(1, 450)
        self.tbl_ThongTinDDSV.setColumnWidth(2, 420)
        self.tbl_ThongTinDDSV.setRowCount(len(lstMH))
        for mh in lstMH:
            self.tbl_ThongTinDDSV.setItem(row, 0, QtWidgets.QTableWidgetItem(mh["mh"]))
            self.tbl_ThongTinDDSV.setItem(row, 1, QtWidgets.QTableWidgetItem(mh["lop"]))
            row += 1
        for i in range(self.tbl_ThongTinDDSV.rowCount()):
            cursor.execute(f"select LOPMONHOC.MALOPMH, COUNT(TINHTRANG) from LOPMONHOC,BUOIHOC,CHITIETDD WHERE LOPMONHOC.MALOPMH=BUOIHOC.MALOPMH"
                           f" AND BUOIHOC.MABH=CHITIETDD.MABH AND LOPMONHOC.MALOPMH='{self.tbl_ThongTinDDSV.item(i, 1).text()}' "
                           f"AND CHITIETDD.MASV='{self.ID_TK}' AND TINHTRANG=N'vắng' group by LOPMONHOC.MALOPMH")
            data=cursor.fetchall()
            if data!=[]:
                self.tbl_ThongTinDDSV.setItem(i, 2, QtWidgets.QTableWidgetItem(str(data[0][1])))
            else:
                self.tbl_ThongTinDDSV.setItem(i, 2, QtWidgets.QTableWidgetItem("0"))


    def loadTKBSV(self):
        row = 0
        lstMH = []
        for row1 in cursor.execute(f"select TENMH,NGAYHOC,GIOBD,GIOKT,MAPH From BUOIHOC,CHITIETLHP,LOPMONHOC, MONHOC where BUOIHOC.MALOPMH=CHITIETLHP.MALOPMH "
                                   f"AND CHITIETLHP.MALOPMH=LOPMONHOC.MALOPMH AND LOPMONHOC.MAMH=MONHOC.MAMH "
                                   f"and CHITIETLHP.MASV='{self.ID_TK}' group by TENMH,NGAYHOC,GIOBD,GIOKT,MAPH ORDER BY NGAYHOC"):
            MH = {}
            MH["mh"] = row1[0]
            y = str(row1[1]).split("-")[0]
            m = str(row1[1]).split("-")[1]
            d = str(row1[1]).split("-")[2]
            MH["ngay"] = d + "/" + m + "/" + y
            MH["bd"] = row1[2]
            MH["kt"] = row1[3]
            MH["phong"] = row1[4]
            lstMH.append(MH)
        self.tbl_ThoiKhoaBieuSV.setColumnWidth(0, 280)
        self.tbl_ThoiKhoaBieuSV.setColumnWidth(1, 150)
        self.tbl_ThoiKhoaBieuSV.setColumnWidth(2, 225)
        self.tbl_ThoiKhoaBieuSV.setColumnWidth(3, 280)
        self.tbl_ThoiKhoaBieuSV.setColumnWidth(4, 225)
        self.tbl_ThoiKhoaBieuSV.setRowCount(len(lstMH))
        for mh in lstMH:
            self.tbl_ThoiKhoaBieuSV.setItem(row, 0, QtWidgets.QTableWidgetItem(mh["mh"]))
            self.tbl_ThoiKhoaBieuSV.setItem(row, 1, QtWidgets.QTableWidgetItem(mh["ngay"]))
            self.tbl_ThoiKhoaBieuSV.setItem(row, 2, QtWidgets.QTableWidgetItem(mh["bd"]))
            self.tbl_ThoiKhoaBieuSV.setItem(row, 3, QtWidgets.QTableWidgetItem(mh["kt"]))
            self.tbl_ThoiKhoaBieuSV.setItem(row, 4, QtWidgets.QTableWidgetItem(mh["phong"]))
            row += 1

    ##############################################################
    ###page Đăng kí môn học sv
    def DangKiMH_11(self):
        if self.fi_IDLop_11.text()=="":
            msg = QMessageBox()
            msg.setIcon(QMessageBox.Warning)
            msg.setWindowTitle("Thông báo")
            msg.setText("Vui lòng chọn lớp học muốn đăng kí!!")
            msg.setStandardButtons(QMessageBox.Ok)
            msg.exec_()
        else:
            try:
                cursor.execute("INSERT INTO CHITIETLHP VALUES(?,?)",self.fi_IDLop_11.text(),self.ID_TK)
                con.commit()
                msg = QMessageBox()
                msg.setIcon(QMessageBox.NoIcon)
                msg.setWindowTitle("Thông báo")
                msg.setText("Đăng kí thành công")
                msg.setStandardButtons(QMessageBox.Ok)
                result = msg.exec_()
            except:
                msg = QMessageBox()
                msg.setIcon(QMessageBox.NoIcon)
                msg.setWindowTitle("Thông báo")
                msg.setText("Lỗi")
                msg.setStandardButtons(QMessageBox.Ok)
                result = msg.exec_()

    def AllMH_11(self):
        row = 0
        lstMH = []
        for row1 in cursor.execute(f"select * from MONHOC"):
            MH = {}
            MH["ID"] = row1[0]
            MH["name"] = row1[1]
            MH["soTC"] = row1[2]
            lstMH.append(MH)
        self.tbl_MonHoc_11.setColumnWidth(0, 150)
        self.tbl_MonHoc_11.setColumnWidth(1, 280)
        self.tbl_MonHoc_11.setColumnWidth(2, 225)
        self.tbl_MonHoc_11.setRowCount(len(lstMH))
        for mh in lstMH:
            self.tbl_MonHoc_11.setItem(row, 0, QtWidgets.QTableWidgetItem(mh["ID"]))
            self.tbl_MonHoc_11.setItem(row, 1, QtWidgets.QTableWidgetItem(mh["name"]))
            self.tbl_MonHoc_11.setItem(row, 2, QtWidgets.QTableWidgetItem(str(mh["soTC"])))
            row += 1
    def TimMonHoc_11(self):
        if self.cbo_TimMH_11.currentText()=="ID":
            row = 0
            lstMH = []
            for row1 in cursor.execute(f"select * from MONHOC Where MAMH='{self.txt_TimMH_11.text()}'"):
                MH = {}
                MH["ID"] = row1[0]
                MH["name"] = row1[1]
                MH["soTC"] = row1[2]
                lstMH.append(MH)
            self.tbl_MonHoc_11.setColumnWidth(0, 150)
            self.tbl_MonHoc_11.setColumnWidth(1, 280)
            self.tbl_MonHoc_11.setColumnWidth(2, 225)
            self.tbl_MonHoc_11.setRowCount(len(lstMH))
            for mh in lstMH:
                self.tbl_MonHoc_11.setItem(row, 0, QtWidgets.QTableWidgetItem(mh["ID"]))
                self.tbl_MonHoc_11.setItem(row, 1, QtWidgets.QTableWidgetItem(mh["name"]))
                self.tbl_MonHoc_11.setItem(row, 2, QtWidgets.QTableWidgetItem(str(mh["soTC"])))
                row += 1
        elif self.cbo_TimMH_11.currentText()=="Tên Môn Học":
            row = 0
            lstMH = []
            for row1 in cursor.execute(f"select * from MONHOC Where TENMH LIKE N'%{self.txt_TimMH_11.text()}%'"):
                MH = {}
                MH["ID"] = row1[0]
                MH["name"] = row1[1]
                MH["soTC"] = row1[2]
                lstMH.append(MH)
            self.tbl_MonHoc_11.setColumnWidth(0, 150)
            self.tbl_MonHoc_11.setColumnWidth(1, 280)
            self.tbl_MonHoc_11.setColumnWidth(2, 225)
            self.tbl_MonHoc_11.setRowCount(len(lstMH))
            for mh in lstMH:
                self.tbl_MonHoc_11.setItem(row, 0, QtWidgets.QTableWidgetItem(mh["ID"]))
                self.tbl_MonHoc_11.setItem(row, 1, QtWidgets.QTableWidgetItem(mh["name"]))
                self.tbl_MonHoc_11.setItem(row, 2, QtWidgets.QTableWidgetItem(str(mh["soTC"])))
                row += 1
    def GetLichHocLHP(self):
        if self.fi_IDLop_11.text()=="":
            msg = QMessageBox()
            msg.setIcon(QMessageBox.Warning)
            msg.setWindowTitle("Thông báo")
            msg.setText("Vui lòng chọn lớp học muốn xem lịch học!!")
            msg.setStandardButtons(QMessageBox.Ok)
            msg.exec_()
        else:
            self.fi_IDLHP_4.setText(self.fi_IDLop_11.text())
            self.fi_MH_4.setText(self.fi_TenMH_11.text())
            self.fi_GiangVien_4.setText(self.fi_GiangVien_11.text())
            self.stackedWidget.setCurrentWidget(self.page_LichHoc)
            self.btn_ChiTietDD_4.setVisible(False)
            self.loadBuoiHoc()
            if self.Quyen=="GV" or self.Quyen=="SV":
                self.btn_ThemBH_4.setVisible(False)
                self.btn_SuaBH_4.setVisible(False)
                self.btn_XoaBH_4.setVisible(False)
    def GetTTLHPSV(self):
        row = self.tbl_LopHocPhan_11.currentIndex().row()
        ms = self.tbl_LopHocPhan_11.item(row, 0).text()
        for row in cursor.execute(
                f"select * from LOPMONHOC,GIANGVIEN WHERE LOPMONHOC.MAGV=GIANGVIEN.MAGV AND MALOPMH='{ms}'"):
            self.fi_IDLop_11.setText(row[0])
            self.fi_GiangVien_11.setText(row[8])
            self.fi_SiSo_11.setText(str(row[5]))
            self.fi_NgayBatDau_11.setDate(
                QtCore.QDate(int(row[2].split('-')[0]), int(row[2].split('-')[1]), int(row[2].split('-')[2])))
            self.fi_NgayKetThuc_11.setDate(
                QtCore.QDate(int(row[3].split('-')[0]), int(row[3].split('-')[1]), int(row[3].split('-')[2])))
    def GetMonHocSV(self):
        cursor.execute(f"SELECT MAHK FROM HOCKI WHERE TENHK='{self.cbo_hocki_11.currentText()}'")
        data = cursor.fetchall()
        row = self.tbl_MonHoc_11.currentIndex().row()
        ms = self.tbl_MonHoc_11.item(row, 0).text()
        for row in cursor.execute(f"select * from MONHOC Where MAMH='{ms}'"):
            self.fi_IDMH_11.setText(row[0])
            self.fi_TenMH_11.setText(row[1])
            self.fi_SoTC_11.setText(str(row[2]))
            self.fi_TongSoTiet_11.setText(str(row[3]))
            self.fi_TietLiThuyet_11.setText(str(row[4]))
            self.fi_TietThucHanh_11.setText(str(row[5]))
        # load các lớp học phần
        row = 0
        lstLHP = []
        for row1 in cursor.execute(
                f"select * from LOPMONHOC,GIANGVIEN,HOCKI WHERE LOPMONHOC.MAGV=GIANGVIEN.MAGV "
                f"AND LOPMONHOC.MAMH='{ms}' AND LOPMONHOC.MAHK=HOCKI.MAHK AND HOCKI.MAHK='{data[0][0]}'"):
            LHP = {}
            LHP["ID"] = row1[0]
            LHP["name"] = row1[8]
            lstLHP.append(LHP)
        self.tbl_LopHocPhan_11.setColumnWidth(0, 100)
        self.tbl_LopHocPhan_11.setColumnWidth(1, 250)
        self.tbl_LopHocPhan_11.setRowCount(len(lstLHP))
        for mh in lstLHP:
            self.tbl_LopHocPhan_11.setItem(row, 0, QtWidgets.QTableWidgetItem(mh["ID"]))
            self.tbl_LopHocPhan_11.setItem(row, 1, QtWidgets.QTableWidgetItem(mh["name"]))
            row += 1


    def ChangeHK_SV(self):
        cursor.execute(f"SELECT MAHK FROM HOCKI WHERE TENHK='{self.cbo_hocki_11.currentText()}'")
        data = cursor.fetchall()
        cursor.execute(f"SELECT COUNT(*) FROM HOCKI")
        data1 = cursor.fetchall()
        str1=""
        print(data1)
        if(data[0][0]!=data1[0][0]):
             str1= f"select distinct MONHOC.MAMH,TENMH, SOTC from MONHOC,LOPMONHOC WHERE MONHOC.MAMH=LOPMONHOC.MAMH AND LOPMONHOC.MAHK={data[0][0]}"
             self.btn_DangKy_11.setEnabled(False)
        else:
            str1=(f"select*from MONHOC")
            self.btn_DangKy_11.setEnabled(True)
        row = 0
        lstMH = []
        for row1 in cursor.execute(str1):
            MH = {}
            MH["ID"] = row1[0]
            MH["name"] = row1[1]
            MH["soTC"] = row1[2]
            lstMH.append(MH)
        self.tbl_MonHoc_11.setColumnWidth(0, 150)
        self.tbl_MonHoc_11.setColumnWidth(1, 280)
        self.tbl_MonHoc_11.setColumnWidth(2, 225)
        self.tbl_MonHoc_11.setRowCount(len(lstMH))
        for mh in lstMH:
            self.tbl_MonHoc_11.setItem(row, 0, QtWidgets.QTableWidgetItem(mh["ID"]))
            self.tbl_MonHoc_11.setItem(row, 1, QtWidgets.QTableWidgetItem(mh["name"]))
            self.tbl_MonHoc_11.setItem(row, 2, QtWidgets.QTableWidgetItem(str(mh["soTC"])))
            row += 1
        # load các lớp học phần đã đăng kí
        row = 0
        lstMH = []
        for row1 in cursor.execute(
                    f"select LOPMONHOC.MALOPMH,TENMH,LOPMONHOC.NGAYBD from CHITIETLHP,MONHOC,SINHVIEN,LOPMONHOC,HOCKI "
                    f"WHERE CHITIETLHP.MALOPMH=LOPMONHOC.MALOPMH AND LOPMONHOC.MAMH=MONHOC.MAMH "
                    f"AND CHITIETLHP.MASV=SINHVIEN.MASV AND HOCKI.MAHK=LOPMONHOC.MAHK AND "
                    f"SINHVIEN.MASV='{self.ID_TK}' AND HOCKI.MAHK={data[0][0]}"):
            MH = {}
            MH["ID"] = row1[0]
            MH["name"] = row1[1]
            MH["soTC"] = str(row1[2])
            lstMH.append(MH)
        self.tbl_LopHocDK_11.setColumnWidth(0, 150)
        self.tbl_LopHocDK_11.setColumnWidth(1, 280)
        self.tbl_LopHocDK_11.setColumnWidth(2, 225)
        self.tbl_LopHocDK_11.setRowCount(len(lstMH))
        for mh in lstMH:
            self.tbl_LopHocDK_11.setItem(row, 0, QtWidgets.QTableWidgetItem(mh["ID"]))
            self.tbl_LopHocDK_11.setItem(row, 1, QtWidgets.QTableWidgetItem(mh["name"]))
            self.tbl_LopHocDK_11.setItem(row, 2, QtWidgets.QTableWidgetItem(mh["soTC"]))
            row += 1
    def LoadMonHoc_SV(self):
        # Load combobox học kì
        self.cbo_hocki_11.clear()
        for row1 in cursor.execute("select * from HOCKI ORDER BY  MAHK DESC"):
            self.cbo_hocki_11.addItem(row1[1])
        cursor.execute(f"SELECT MAHK FROM HOCKI WHERE TENHK='{self.cbo_hocki_11.currentText()}'")
        data = cursor.fetchall()
        #load môn học
        row = 0
        lstMH = []
        for row1 in cursor.execute("select * from MONHOC"):
            MH = {}
            MH["ID"] = row1[0]
            MH["name"] = row1[1]
            MH["soTC"] = row1[2]
            lstMH.append(MH)
        self.tbl_LopHocPhan_11.setColumnWidth(0, 100)
        self.tbl_LopHocPhan_11.setColumnWidth(1,250)
        self.tbl_MonHoc_11.setColumnWidth(0, 150)
        self.tbl_MonHoc_11.setColumnWidth(1, 280)
        self.tbl_MonHoc_11.setColumnWidth(2, 225)
        self.tbl_MonHoc_11.setRowCount(len(lstMH))
        for mh in lstMH:
            self.tbl_MonHoc_11.setItem(row, 0, QtWidgets.QTableWidgetItem(mh["ID"]))
            self.tbl_MonHoc_11.setItem(row, 1, QtWidgets.QTableWidgetItem(mh["name"]))
            self.tbl_MonHoc_11.setItem(row, 2, QtWidgets.QTableWidgetItem(str(mh["soTC"])))
            row += 1
        #load các lớp học phần đã đăng kí
        row = 0
        lstMH = []
        for row1 in cursor.execute(f"select LOPMONHOC.MALOPMH,TENMH,LOPMONHOC.NGAYBD from CHITIETLHP,MONHOC,SINHVIEN,LOPMONHOC,HOCKI "
                                   f"WHERE CHITIETLHP.MALOPMH=LOPMONHOC.MALOPMH AND LOPMONHOC.MAMH=MONHOC.MAMH "
                                   f"AND CHITIETLHP.MASV=SINHVIEN.MASV AND HOCKI.MAHK=LOPMONHOC.MAHK AND "
                                   f"SINHVIEN.MASV='{self.ID_TK}' AND HOCKI.MAHK={data[0][0]}"):
            MH = {}
            MH["ID"] = row1[0]
            MH["name"] = row1[1]
            MH["soTC"] = str(row1[2])
            lstMH.append(MH)
        self.tbl_LopHocDK_11.setColumnWidth(0, 80)
        self.tbl_LopHocDK_11.setColumnWidth(1, 150)
        self.tbl_LopHocDK_11.setColumnWidth(2, 115)
        self.tbl_LopHocDK_11.setRowCount(len(lstMH))
        for mh in lstMH:
            self.tbl_LopHocDK_11.setItem(row, 0, QtWidgets.QTableWidgetItem(mh["ID"]))
            self.tbl_LopHocDK_11.setItem(row, 1, QtWidgets.QTableWidgetItem(mh["name"]))
            self.tbl_LopHocDK_11.setItem(row, 2, QtWidgets.QTableWidgetItem(mh["soTC"]))
            row += 1
        self.cbo_TimMH_11.clear()
        self.cbo_TimMH_11.addItem("ID")
        self.cbo_TimMH_11.addItem("Tên Môn Học")



        self.fi_IDMH_11.setEnabled(False)
        self.fi_TenMH_11.setEnabled(False)
        self.fi_SoTC_11.setEnabled(False)
        self.fi_TongSoTiet_11.setEnabled(False)
        self.fi_TietLiThuyet_11.setEnabled(False)
        self.fi_TietThucHanh_11.setEnabled(False)
        self.fi_IDLop_11.setEnabled(False)
        self.fi_GiangVien_11.setEnabled(False)
        self.fi_SiSo_11.setEnabled(False)
        self.fi_NgayBatDau_11.setEnabled(False)
        self.fi_NgayKetThuc_11.setEnabled(False)
    ##############################################################
    ###page TKSV
    def LuuTKSV(self):
        if self.fi_HoTen_9.text() == "" or self.fi_CMND_9.text() == "" or self.fi_SDT_9.text() == "" or self.fi_DanToc_9.text() == ""  or self.fi_Email_9.text() == "" or self.fi_DCThuongTru_9.text() == "" or self.fi_DCTamTru_9.text() == "":
            msg = QMessageBox()
            msg.setIcon(QMessageBox.Warning)
            msg.setWindowTitle("Thông báo")
            msg.setText("Vui lòng nhập đầy đủ thông tin")
            msg.setStandardButtons(QMessageBox.Ok )
            result = msg.exec_()
        else:
            try:
                cursor.execute("set dateformat dmy "
                    "Update SINHVIEN set TENSV=?,SDT=?, NGAYSINH=? ,CMND=?,DANTOC=?,GIOITINH=?, EMAIL=?,DIACHITT=?,DCTAMTRU=? where MASV=? "
                                   , self.fi_HoTen_9.text(), self.fi_SDT_9.text(),
                                   self.fi_NgaySinh_9.text(), self.fi_CMND_9.text(), self.fi_DanToc_9.text(),
                                   self.fi_GioiTinh_9.currentText(),
                                   self.fi_Email_9.text(), self.fi_DCThuongTru_9.text(), self.fi_DCTamTru_9.text(),
                                    self.fi_IDSV_9.text())
                con.commit()
                msg = QMessageBox()
                msg.setIcon(QMessageBox.NoIcon)
                msg.setWindowTitle("Thông báo")
                msg.setText("Cập nhật sinh viên thành công")
                msg.setStandardButtons(QMessageBox.Ok)
                result = msg.exec_()
                self.loadTKSV()
            except:
                msg = QMessageBox()
                msg.setIcon(QMessageBox.Warning)
                msg.setWindowTitle("Thông báo")
                msg.setText("Lỗi")
                msg.setStandardButtons(QMessageBox.Ok)
                result = msg.exec_()
    def HuyTKSV(self):
        self.loadTKSV()
    def SuaTKSV(self):
        self.btn_LuuSV_9.setVisible(True)
        self.btn_HuySV_9.setVisible(True)
        self.btn_SuaSV_9.setVisible(False)
        self.btn_DoiMatKhau_9.setVisible(False)
        self.fi_GioiTinh_9.setEnabled(True)
        self.fi_DCThuongTru_9.setEnabled(True)
        self.fi_DCTamTru_9.setEnabled(True)
        self.fi_HoTen_9.setEnabled(True)
        self.fi_CMND_9.setEnabled(True)
        self.fi_NgaySinh_9.setEnabled(True)
        self.fi_SDT_9.setEnabled(True)
        self.fi_DanToc_9.setEnabled(True)
        self.fi_Email_9.setEnabled(True)
    def loadTKSV(self):
        self.btn_LuuSV_9.setVisible(False)
        self.btn_HuySV_9.setVisible(False)
        self.btn_SuaSV_9.setVisible(True)
        self.btn_DoiMatKhau_9.setVisible(True)
        self.fi_Khoa_9.setEnabled(False)
        self.fi_ChuyenNganh_9.setEnabled(False)
        self.fi_NienKhoa_9.setEnabled(False)
        self.fi_IDSV_9.setEnabled(False)
        self.fi_Lop_9.setEnabled(False)
        self.fi_GioiTinh_9.setEnabled(False)
        self.fi_DCThuongTru_9.setEnabled(False)
        self.fi_DCTamTru_9.setEnabled(False)
        self.fi_HoTen_9.setEnabled(False)
        self.fi_CMND_9.setEnabled(False)
        self.fi_NgaySinh_9.setEnabled(False)
        self.fi_SDT_9.setEnabled(False)
        self.fi_DanToc_9.setEnabled(False)
        self.fi_Email_9.setEnabled(False)
        #load combobox giới tính
        self.fi_GioiTinh_9.clear()
        self.fi_GioiTinh_9.addItem("Nam")
        self.fi_GioiTinh_9.addItem("Nữ")
        self.fi_GioiTinh_9.addItem("Khác")
        try:
            for row in cursor.execute(f"select * from SINHVIEN,KHOA,LOP,CHUYENNGANH,NIENKHOA WHERE SINHVIEN.MASV='{self.ID_TK} ' "
                                      f"AND LOP.MAKHOA=KHOA.MAKHOA AND SINHVIEN.MALOP=LOP.MALOP AND SINHVIEN.MACN=CHUYENNGANH.MACN "
                                      f"AND NIENKHOA.MANK=SINHVIEN.MANK"):
                self.fi_IDSV_9.setText(row[0])
                self.fi_Khoa_9.setText(row[17])
                self.fi_ChuyenNganh_9.setText(row[21])
                self.fi_NienKhoa_9.setText(row[24] )
                self.fi_Lop_9.setText(row[10])
                self.fi_GioiTinh_9.setCurrentText(row[6])
                self.fi_Email_9.setText(row[7])
                self.fi_DCTamTru_9.setText(row[9])
                self.fi_DCThuongTru_9.setText(row[8])
                self.fi_DanToc_9.setText(row[5])
                self.fi_HoTen_9.setText(row[1])
                self.fi_CMND_9.setText(row[4])
                self.fi_SDT_9.setText(row[2])
                self.fi_NgaySinh_9.setDate(
                QtCore.QDate(int(row[3].split('-')[0]), int(row[3].split('-')[1]), int(row[3].split('-')[2])))
                if row[11] == None:
                    image = np.array(Image.open(f"Avatar/Who1.png"))
                    image = cv2.resize(image, (212, 137))
                    image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
                    img = QtGui.QImage(image, image.shape[1], image.shape[0], image.strides[0],
                                       QtGui.QImage.Format_RGB888)  # tổng số pixel quét của ảnh
                    self.lbl_Avatar_9.setPixmap(QtGui.QPixmap.fromImage(img))
                else:
                    image = np.array(Image.open(f"Avatar/{row[11]}"))

                    image = cv2.resize(image, (212, 137))
                    img = QtGui.QImage(image, image.shape[1], image.shape[0], image.strides[0],
                                       QtGui.QImage.Format_RGB888)  # tổng số pixel quét của ảnh
                    self.lbl_Avatar_9.setPixmap(QtGui.QPixmap.fromImage(img))
        except:
            pass

    ###########################################################################################3
    ###chung
    def XacNhanKP(self):
        ms=""
        cnt=0
        try:
            row = self.tbl_DSBanSaoLuu.currentIndex().row()
            ms = self.tbl_DSBanSaoLuu.item(row, 0).text()
        except:
            pass
        if ms=="":
            msg = QMessageBox()
            msg.setIcon(QMessageBox.Warning)
            msg.setWindowTitle("Thông báo")
            msg.setText("Vui lòng chọn bản sao lưu!!!")
            msg.setStandardButtons(QMessageBox.Ok)
            msg.exec_()
        else:
            self.progressBar_KhoiPhuc.setVisible(True)
            path = os.getcwd() + "\\" + "Backup\\"+ms
            try:
                con.autocommit = True
                QApplication.processEvents()
                cursor.execute(f"Use master; ALTER DATABASE KhoaLuan SET SINGLE_USER WITH ROLLBACK IMMEDIATE "
                               f"Use master; RESTORE DATABASE KhoaLuan FROM DISK = '{path}' WITH REPLACE "
                               f"Use master; ALTER DATABASE KhoaLuan SET MULTI_USER WITH ROLLBACK IMMEDIATE")
                while cursor.nextset():
                    if cnt<=88:
                        cnt+=10
                    else:
                        cnt=88

                    self.progressBar_KhoiPhuc.setValue(cnt)
                    pass
                self.progressBar_KhoiPhuc.setValue(100)
                msg = QMessageBox()
                msg.setIcon(QMessageBox.NoIcon)
                msg.setWindowTitle("Thông báo")
                msg.setText("Khôi phục dữ liệu thành công")
                msg.setStandardButtons(QMessageBox.Ok)
                msg.exec_()
                self.progressBar_KhoiPhuc.setVisible(False)
            except:
                msg = QMessageBox()
                msg.setIcon(QMessageBox.Warning)
                msg.setWindowTitle("Thông báo")
                msg.setText("Lỗi")
                msg.setStandardButtons(QMessageBox.Ok)
                msg.exec_()
        cursor.execute(" Use KhoaLuan")
    def KhoiPhuc(self):
        self.setStysheetBtn()
        self.stackedWidget.setCurrentWidget(self.page_KhoiPhuc)
        row = 0
        lst=[]
        self.tbl_DSBanSaoLuu.setColumnWidth(0, 1177)
        for row1 in os.listdir("Backup/"):
            SV= row1
            lst.append(SV)
        self.tbl_DSBanSaoLuu.setRowCount(len(lst))
        for sv in lst:
            self.tbl_DSBanSaoLuu.setItem(row, 0, QtWidgets.QTableWidgetItem(sv))
            row += 1
    def SaoLuu(self):
        try:
            str=time.strftime("Ngay_%d_%m_20%y__%H_%M_%p")+"_data.bak"
            path = os.getcwd() + "\\" + "Backup\\"+str
            con.autocommit = True
            cursor.execute(f"backup database KhoaLuan to disk = '{path}'")
            while cursor.nextset():
                pass
            msg = QMessageBox()
            msg.setIcon(QMessageBox.NoIcon)
            msg.setWindowTitle("Thông báo")
            msg.setText("Sao lưu thành công")
            msg.setStandardButtons(QMessageBox.Ok)
            msg.exec_()
        except:
            msg = QMessageBox()
            msg.setIcon(QMessageBox.Warning)
            msg.setWindowTitle("Thông báo")
            msg.setText("Lỗi")
            msg.setStandardButtons(QMessageBox.Ok)
            msg.exec_()
    def setStysheetBtn(self):
        self.btnSinhVien.setStyleSheet("background-color: rgb(0, 255, 127);")
        self.btnMonHoc.setStyleSheet("background-color: rgb(0, 255, 127);")
        self.btnDiemDanh.setStyleSheet("background-color: rgb(0, 255, 127);")
        self.btnGiangVien.setStyleSheet("background-color: rgb(0, 255, 127);")
    def GioiThieu(self):
        self.setStysheetBtn()
        self.stackedWidget.setCurrentWidget(self.page_GioiThieu)
    def XemTTTK(self):
        self.setStysheetBtn()
        if self.Quyen == "GV" or self.Quyen == "AD":
            self.stackedWidget.setCurrentWidget(self.page_TKGV)
        elif self.Quyen == "SV":
            self.stackedWidget.setCurrentWidget(self.page_TKSV)
    def DangXuat(self):
        self.DongCam()
        self.login.show()
        self.hide()
    def ktMatKhauSV(self):
        cursor.execute(f"select *from SINHVIEN WHERE MASV='{self.ID_TK}' and MATKHAU='{self.txtMatKhauCu.text()}'")
        data=cursor.fetchall()
        if data!=[]:
            return True
        return False
    def ktMatKhauGV(self):
        cursor.execute(f"select *from GIANGVIEN WHERE MAGV='{self.ID_TK}' and MATKHAU='{self.txtMatKhauCu.text()}'")
        data=cursor.fetchall()
        if data!=[]:
            return True
        return False
    def DoiMatKhau(self):
        if self.Quyen=="SV":
            if self.txtMatKhauCu.text()=="" or self.txtMatKhauMoi.text()=="" or self.txtXacNhanMK.text()=="":
                msg = QMessageBox()
                msg.setIcon(QMessageBox.Warning)
                msg.setWindowTitle("Thông báo")
                msg.setText("Vui lòng nhập đầy đủ thông tin")
                msg.setStandardButtons(QMessageBox.Ok)
                msg.exec_()
            elif self.txtMatKhauMoi.text()!=self.txtXacNhanMK.text():
                msg = QMessageBox()
                msg.setIcon(QMessageBox.Warning)
                msg.setWindowTitle("Thông báo")
                msg.setText("Mật khẩu mới không trùng khớp")
                msg.setStandardButtons(QMessageBox.Ok)
                msg.exec_()
            elif self.ktMatKhauSV()==False:
                msg = QMessageBox()
                msg.setIcon(QMessageBox.Warning)
                msg.setWindowTitle("Thông báo")
                msg.setText("Mật khẩu cũ không chính xác")
                msg.setStandardButtons(QMessageBox.Ok)
                msg.exec_()
            else:
                try:
                    cursor.execute("set dateformat dmy "
                                   "Update SINHVIEN set MATKHAU=?  where MASV=? "
                                   ,self.txtMatKhauMoi.text() ,self.ID_TK)
                    con.commit()
                    msg = QMessageBox()
                    msg.setIcon(QMessageBox.NoIcon)
                    msg.setWindowTitle("Thông báo")
                    msg.setText("Cập nhật mật khẩu thành công")
                    msg.setStandardButtons(QMessageBox.Ok)
                    result = msg.exec_()
                    self.loadTKSV()
                except:
                    msg = QMessageBox()
                    msg.setIcon(QMessageBox.Warning)
                    msg.setWindowTitle("Thông báo")
                    msg.setText("Lỗi")
                    msg.setStandardButtons(QMessageBox.Ok)
                    result = msg.exec_()
        else:
            if self.txtMatKhauCu.text()=="" or self.txtMatKhauMoi.text()=="" or self.txtXacNhanMK.text()=="":
                msg = QMessageBox()
                msg.setIcon(QMessageBox.Warning)
                msg.setWindowTitle("Thông báo")
                msg.setText("Vui lòng nhập đầy đủ thông tin")
                msg.setStandardButtons(QMessageBox.Ok)
                msg.exec_()
            elif self.txtMatKhauMoi.text()!=self.txtXacNhanMK.text():
                msg = QMessageBox()
                msg.setIcon(QMessageBox.Warning)
                msg.setWindowTitle("Thông báo")
                msg.setText("Mật khẩu mới không trùng khớp")
                msg.setStandardButtons(QMessageBox.Ok)
                msg.exec_()
            elif self.ktMatKhauGV()==False:
                msg = QMessageBox()
                msg.setIcon(QMessageBox.Warning)
                msg.setWindowTitle("Thông báo")
                msg.setText("Mật khẩu cũ không chính xác")
                msg.setStandardButtons(QMessageBox.Ok)
                msg.exec_()
            else:
                try:
                    cursor.execute("set dateformat dmy "
                                   "Update GIANGVIEN set MATKHAU=?  where MAGV=? "
                                   ,self.txtMatKhauMoi.text() ,self.ID_TK)
                    con.commit()
                    msg = QMessageBox()
                    msg.setIcon(QMessageBox.NoIcon)
                    msg.setWindowTitle("Thông báo")
                    msg.setText("Cập nhật mật khẩu thành công")
                    msg.setStandardButtons(QMessageBox.Ok)
                    result = msg.exec_()
                    self.loadTKSV()
                except:
                    msg = QMessageBox()
                    msg.setIcon(QMessageBox.Warning)
                    msg.setWindowTitle("Thông báo")
                    msg.setText("Lỗi")
                    msg.setStandardButtons(QMessageBox.Ok)
                    result = msg.exec_()
    def Page_DoiMatKhau(self):
        self.setStysheetBtn()
        self.stackedWidget.setCurrentWidget(self.page_DoiMatKhau)


    def GetThoiGian(self):
        string = time.strftime('%H:%M:%S %p')
        self.lbl_time.setText(string)
    def chuyenGio(self,str):
        h=int(str.split(":")[0])
        m=str.split(":")[1].split(" ")[0]
        s=str.split(":")[1].split(" ")[1]
        if s=="CH" and h!=12:
            h+=12
        kq = f"{h}:{m} "
        return kq
    ################################################################################################
    #Phân Quyền
    def Page_MonHoc(self):
        self.setStysheetBtn()
        self.btnMonHoc.setStyleSheet("background-color: rgb(117, 117, 117);")
        self.DongCam()
        if self.Quyen == "AD":
            self.stackedWidget.setCurrentWidget(self.page_MonHoc)
        elif self.Quyen == "GV":
            self.stackedWidget.setCurrentWidget(self.page_MonHocGV)
        elif self.Quyen == "SV":
            self.stackedWidget.setCurrentWidget(self.page_MonHocSV)

    def Page_GiangVien(self):
        self.DongCam()
        self.setStysheetBtn()
        self.btnGiangVien.setStyleSheet("background-color: rgb(117, 117, 117);")
        if self.Quyen=="AD":
            self.stackedWidget.setCurrentWidget(self.page_GiangVien)
        elif self.Quyen=="GV":
            self.stackedWidget.setCurrentWidget(self.page_TKGV)
        elif self.Quyen=="SV":
            self.stackedWidget.setCurrentWidget(self.page_LHSV)
            self.loadTKBSV()
    def Page_SinhVien(self):
        self.DongCam()
        self.setStysheetBtn()
        self.btnSinhVien.setStyleSheet("background-color: rgb(117, 117, 117);")
        if  self.Quyen=="AD":
            self.stackedWidget.setCurrentWidget(self.page_SinhVien)
            self.loadData()
            self.KhoiTaoCombobox()
        elif self.Quyen=="SV":
            self.stackedWidget.setCurrentWidget(self.page_TKSV)
        elif self.Quyen=="GV":
            self.stackedWidget.setCurrentWidget(self.page_LichDayGV)
            self.LoadLichDayGV()
    ######################################################################################################
    # page chi tiết điểm danh
    def GetHADD(self):
        row = self.tbl_ChiTietDD_8.currentIndex().row()
        ms = self.tbl_ChiTietDD_8.item(row, 0).text()
        masv=self.ID_BuoiHoc+"_"+ms+".png"
        # print(masv)
        if(self.tbl_ChiTietDD_8.item(row,2).text()=="có mặt"):
            img=cv2.imread("AnhDiemDanh/"+masv)
            img=cv2.cvtColor(img,cv2.COLOR_BGR2RGB)
            plt.subplot(1, 1, 1)  # tạo frame gồm 3 dòng 3 cột, đặt hình vào ô thứ iS
            plt.imshow(img)
            plt.axis("off")  # ko vẽ trục x,y
            plt.show()

    def GetDD(self):
        row = self.tbl_DSBuoiHoc_8.currentIndex().row()
        ms = self.tbl_DSBuoiHoc_8.item(row, 0).text()
        self.ID_BuoiHoc = ms
        lstBH = []
        for row1 in cursor.execute(f"select * from CHITIETDD,SINHVIEN WHERE CHITIETDD.MASV=SINHVIEN.MASV AND MABH='{ms}'"):
            LHP = {}
            LHP["ID"] = row1[6]
            LHP["name"] = row1[7]
            LHP["tt"] = row1[5]
            LHP["time"] = row1[3]
            LHP["ghichu"] = row1[4]
            LHP["hinhanh"] = row1[2]
            lstBH.append(LHP)
        self.tbl_ChiTietDD_8.setColumnWidth(0, 120)
        self.tbl_ChiTietDD_8.setColumnWidth(1, 200)
        self.tbl_ChiTietDD_8.setColumnWidth(2, 100)
        self.tbl_ChiTietDD_8.setColumnWidth(3, 120)
        self.tbl_ChiTietDD_8.setColumnWidth(4, 120)
        self.tbl_ChiTietDD_8.setColumnWidth(5, 150)
        # self.tbl_ChiTietDD_8.verticalHeader().setDefaultSectionSize(100)
        self.tbl_ChiTietDD_8.setRowCount(len(lstBH))
        row1=0
        for mh in lstBH:
            self.tbl_ChiTietDD_8.setItem(row1, 0, QtWidgets.QTableWidgetItem(mh["ID"]))
            self.tbl_ChiTietDD_8.setItem(row1, 1, QtWidgets.QTableWidgetItem(mh["name"]))

            self.tbl_ChiTietDD_8.setItem(row1, 2, QtWidgets.QTableWidgetItem(mh["tt"]))
            if mh["tt"]=='vắng':
                self.tbl_ChiTietDD_8.item(row1,2).setBackground(QtGui.QColor(255,0,0))
            elif mh["tt"]=="có mặt":
                self.tbl_ChiTietDD_8.item(row1, 2).setBackground(QtGui.QColor(0, 255, 0))
            self.tbl_ChiTietDD_8.setItem(row1, 3, QtWidgets.QTableWidgetItem(mh["time"]))
            self.tbl_ChiTietDD_8.setItem(row1, 4, QtWidgets.QTableWidgetItem(mh["ghichu"]))
            if mh["hinhanh"]!=None:
                # image = np.array(Image.open(f"AnhDiemDanh/{mh['hinhanh']}"))
                # img = QtGui.QImage(image, image.shape[1], image.shape[0], image.strides[0],
                #                    QtGui.QImage.Format_RGB888)
                # imglabel = QtWidgets.QLabel("Image")
                # imglabel.setPixmap(QtGui.QPixmap.fromImage(img))
                self.tbl_ChiTietDD_8.setItem(row1, 5,QtWidgets.QTableWidgetItem("Xem ảnh"))

                self.font.setUnderline(True)
                self.tbl_ChiTietDD_8.item(row1,5).setFont(self.font)
                self.tbl_ChiTietDD_8.item(row1,5).setForeground(QtGui.QColor(0, 0,255))
            else:
                # image = np.array(Image.open(f"Avatar/pic.png"))
                # image=cv2.resize(image,(170,150))
                # img = QtGui.QImage(image, image.shape[1], image.shape[0], image.strides[0],
                #                    QtGui.QImage.Format_RGB888)
                # imglabel = QtWidgets.QLabel("Image")
                # imglabel.setPixmap(QtGui.QPixmap.fromImage(img))
                # self.tbl_ChiTietDD_8.setCellWidget(row1, 5, imglabel)
                pass
            row1 += 1


    ######################################################################################################
    # page giảng viên

    def XoaGV(self):
        if self.fi_IDGV_7.text()=="":
            msg = QMessageBox()
            msg.setIcon(QMessageBox.Warning)
            msg.setWindowTitle("Thông báo")
            msg.setText("Vui lòng chọn giảng viên muốn xóa")
            msg.setStandardButtons(QMessageBox.Ok)
            msg.exec_()
        else:
            try:
                cursor.execute("DELETE GIANGVIEN "
                               "WHERE MAGV=?", self.fi_IDGV_7.text())
                con.commit()
                msg = QMessageBox()
                msg.setIcon(QMessageBox.NoIcon)
                msg.setWindowTitle("Thông báo")
                msg.setText("Xóa thành công")
                msg.setStandardButtons(QMessageBox.Ok)
                result = msg.exec_()
                self.loadPageGV()
            except:
                msg = QMessageBox()
                msg.setIcon(QMessageBox.NoIcon)
                msg.setWindowTitle("Thông báo")
                msg.setText("Lỗi")
                msg.setStandardButtons(QMessageBox.Ok)
                result = msg.exec_()
    def LuuGV(self):
        if self.fi_HoTenGV_7.text()=="" or self.fi_SDT_7.text()=="" or self.fi_Khoa_7.currentText()==-1 \
                or self.fi_DDThuongTru_7.text()=="" or self.fi_DCTamTru_7.text()=="" or self.fi_GioiTinhGV_7.currentText()==-1 \
                or self.fi_CMND_7.text()=="" or self.fi_DanToc_7.text()=="" or self.fi_TrinhDo_7.text()=="" \
                or self.fi_Email_7.text()=="":
            msg = QMessageBox()
            msg.setIcon(QMessageBox.Warning)
            msg.setWindowTitle("Thông báo")
            msg.setText("Vui lòng nhập đầy đủ thông tin")
            msg.setStandardButtons(QMessageBox.Ok)
            msg.exec_()
        else:
            if self.themgv==True:
                try:
                    hinhanh=self.fi_IDGV_7.text()+".png"
                    mk=(self.fi_NgaySinhGV_7.text().split("/")[0]+self.fi_NgaySinhGV_7.text().split("/")[1]+self.fi_NgaySinhGV_7.text().split("/")[2])
                    cursor.execute("SET DATEFORMAT DMY INSERT INTO GIANGVIEN "
                                   "Values(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)", self.fi_IDGV_7.text(), self.fi_HoTenGV_7.text(),
                                   self.fi_SDT_7.text(), self.fi_NgaySinhGV_7.text(), self.fi_CMND_7.text(),self.fi_DanToc_7.text(),
                                   self.fi_TrinhDo_7.text(),
                                   self.fi_GioiTinhGV_7.currentText(),self.fi_Email_7.text(),mk,self.fi_DDThuongTru_7.text(),
                                   self.fi_DCTamTru_7.text(),hinhanh,self.fi_Khoa_7.currentText().split('-')[1],"GV")
                    cv2.imwrite("Avatar/"+f"{self.fi_IDGV_7.text()}.png",self.image_GV)
                    con.commit()
                    msg = QMessageBox()
                    msg.setIcon(QMessageBox.NoIcon)
                    msg.setWindowTitle("Thông báo")
                    msg.setText("Thêm giảng viên thành công")
                    msg.setStandardButtons(QMessageBox.Ok)
                    result = msg.exec_()
                    self.loadPageGV()
                except:
                    msg = QMessageBox()
                    msg.setIcon(QMessageBox.Warning)
                    msg.setWindowTitle("Thông báo")
                    msg.setText("Lỗi")
                    msg.setStandardButtons(QMessageBox.Ok)
                    result = msg.exec_()
            elif self.themgv == False:
                try:
                    hinhanh=self.fi_IDGV_7.text()+".png"
                    cursor.execute("SET DATEFORMAT DMY UPDATE GIANGVIEN "
                                   "SET TENGV=?, SDT=?, NGAYSINH=?, CMND=?, DANTOC=?,TRINHDO=?,GIOITINH=?, EMAIL=?,DIACHITT=?, DCTAMTRU=?, MAKHOA=? WHERE MAGV=?", self.fi_HoTenGV_7.text(),
                                   self.fi_SDT_7.text(), self.fi_NgaySinhGV_7.text(), self.fi_CMND_7.text(),self.fi_DanToc_7.text(),
                                   self.fi_TrinhDo_7.text(),
                                   self.fi_GioiTinhGV_7.currentText(),self.fi_Email_7.text(),self.fi_DDThuongTru_7.text(),
                                   self.fi_DCTamTru_7.text(),self.fi_Khoa_7.currentText().split('-')[1],self.fi_IDGV_7.text())
                    cv2.imwrite("Avatar/"+f"{self.fi_IDGV_7.text()}.png",self.image_GV)
                    con.commit()
                    msg = QMessageBox()
                    msg.setIcon(QMessageBox.NoIcon)
                    msg.setWindowTitle("Thông báo")
                    msg.setText("Cập nhật thông tin thành công")
                    msg.setStandardButtons(QMessageBox.Ok)
                    result = msg.exec_()
                    self.loadPageGV()
                except:
                    msg = QMessageBox()
                    msg.setIcon(QMessageBox.Warning)
                    msg.setWindowTitle("Thông báo")
                    msg.setText("Lỗi")
                    msg.setStandardButtons(QMessageBox.Ok)
                    result = msg.exec_()

    def ChonAnhGV(self):
        folder_path = QtWidgets.QFileDialog.getOpenFileName(self, 'Open file','c:\'', "Image files (*.jpg *.png)")
        self.image_GV = np.array(Image.open(folder_path[0]))
        self.image_GV=cv2.cvtColor(self.image_GV,cv2.COLOR_BGR2RGB)
        image= cv2.resize(self.image_GV, (157, 115),3)
        img = QtGui.QImage(image, image.shape[1], image.shape[0], image.strides[0],
                           QtGui.QImage.Format_RGB888)  # tổng số pixel quét của ảnh
        self.lbl_AvatarGV_7.setPixmap(QtGui.QPixmap.fromImage(img))
    def TimGV(self):
        lstTimGV = []
        row = 0
        if self.txt_TimGV_7.text() == "":
            for row1 in cursor.execute(
                    f"select * from GIANGVIEN"):
                SV = {}
                SV["ID"] = row1[0]
                SV["name"] = row1[1]
                lstTimGV.append(SV)

            self.tbl_DSGV_7.setColumnWidth(0, 200)
            self.tbl_DSGV_7.setColumnWidth(1, 250)
            self.tbl_DSGV_7.setRowCount(len(lstTimGV))
            for sv in lstTimGV:
                self.tbl_DSGV_7.setItem(row, 0, QtWidgets.QTableWidgetItem(sv["ID"]))
                self.tbl_DSGV_7.setItem(row, 1, QtWidgets.QTableWidgetItem(sv["name"]))
                row += 1
        elif self.cbo_TimKiemGV_7.currentText() == "ID":
            for row1 in cursor.execute(f"select * from GIANGVIEN WHERE GIANGVIEN.MAGV='{self.txt_TimGV_7.text()}'"):
                SV = {}
                SV["ID"] = row1[0]
                SV["name"] = row1[1]
                lstTimGV.append(SV)

            self.tbl_DSGV_7.setColumnWidth(0, 200)
            self.tbl_DSGV_7.setColumnWidth(1, 250)
            self.tbl_DSGV_7.setRowCount(len(lstTimGV))
            for sv in lstTimGV:
                self.tbl_DSGV_7.setItem(row, 0, QtWidgets.QTableWidgetItem(sv["ID"]))
                self.tbl_DSGV_7.setItem(row, 1, QtWidgets.QTableWidgetItem(sv["name"]))
                row += 1


        elif self.cbo_TimKiemGV_7.currentText() == "Họ Tên":
            for row1 in cursor.execute(f"select * from GIANGVIEN WHERE  GIANGVIEN.TENGV LIKE N'%{self.txt_TimGV_7.text()}%'"):
                SV = {}
                SV["ID"] = row1[0]
                SV["name"] = row1[1]
                lstTimGV.append(SV)

            self.tbl_DSGV_7.setColumnWidth(0, 200)
            self.tbl_DSGV_7.setColumnWidth(1, 250)
            self.tbl_DSGV_7.setRowCount(len(lstTimGV))
            for sv in lstTimGV:
                self.tbl_DSGV_7.setItem(row, 0, QtWidgets.QTableWidgetItem(sv["ID"]))
                self.tbl_DSGV_7.setItem(row, 1, QtWidgets.QTableWidgetItem(sv["name"]))
                row += 1

    def HuyGV(self):
        self.KhoiTaoPageGV()
        self.fi_IDGV_7.setText("")
        self.fi_HoTenGV_7.setText("")
        self.fi_SDT_7.setText("")
        self.fi_DCTamTru_7.setText("")
        self.fi_DDThuongTru_7.setText("")
        self.fi_CMND_7.setText("")
        self.fi_DanToc_7.setText("")
        self.fi_TrinhDo_7.setText("")
        self.fi_Email_7.setText("")

    def SuaGV(self):
        if self.fi_IDGV_7.text()=="":
            msg = QMessageBox()
            msg.setIcon(QMessageBox.NoIcon)
            msg.setWindowTitle("Thông báo")
            msg.setText("Vui lòng chọn giáo viên cần cập nhật thông tin!!")
            msg.setStandardButtons(QMessageBox.Ok)
            result = msg.exec_()
            self.loadPageGV()
        else:
            self.themgv = False
            self.btn_ThemGV_7.setVisible(False)
            self.btn_SuaGV_7.setVisible(False)
            self.btn_XoaGV_7.setVisible(False)
            self.btn_LuuGV_7.setVisible(True)
            self.btn_HuyGV_7.setVisible(True)
            self.fi_HoTenGV_7.setEnabled(True)
            self.fi_SDT_7.setEnabled(True)
            self.fi_Khoa_7.setEnabled(True)
            self.fi_DCTamTru_7.setEnabled(True)
            self.fi_DDThuongTru_7.setEnabled(True)
            self.fi_GioiTinhGV_7.setEnabled(True)
            self.fi_CMND_7.setEnabled(True)
            self.fi_DanToc_7.setEnabled(True)
            self.fi_TrinhDo_7.setEnabled(True)
            self.fi_Email_7.setEnabled(True)
            self.btn_ChonAnhGV_7.setVisible(True)
    def ThemGV(self):
        self.themgv=True
        self.btn_ThemGV_7.setVisible(False)
        self.btn_SuaGV_7.setVisible(False)
        self.btn_XoaGV_7.setVisible(False)
        self.btn_LuuGV_7.setVisible(True)
        self.btn_HuyGV_7.setVisible(True)
        self.fi_HoTenGV_7.setEnabled(True)
        self.fi_SDT_7.setEnabled(True)
        self.fi_Khoa_7.setEnabled(True)
        self.fi_DCTamTru_7.setEnabled(True)
        self.fi_DDThuongTru_7.setEnabled(True)
        self.fi_GioiTinhGV_7.setEnabled(True)
        self.fi_CMND_7.setEnabled(True)
        self.fi_DanToc_7.setEnabled(True)
        self.fi_TrinhDo_7.setEnabled(True)
        self.fi_Email_7.setEnabled(True)
        self.fi_Khoa_7.setCurrentIndex(-1)
        self.fi_GioiTinhGV_7.setCurrentIndex(-1)
        self.btn_ChonAnhGV_7.setVisible(True)
        self.fi_NgaySinhGV_7.setDate(QtCore.QDate(2000, 1, 1))
        sql = " EXEC GIANGVIEN_ID "
        cursor.execute(sql)
        data = cursor.fetchall()
        self.fi_IDGV_7.setText(data[0][0])
        self.fi_HoTenGV_7.setText("")
        self.fi_SDT_7.setText("")
        self.fi_DCTamTru_7.setText("")
        self.fi_DDThuongTru_7.setText("")
        self.fi_CMND_7.setText("")
        self.fi_DanToc_7.setText("")
        self.fi_TrinhDo_7.setText("")
        self.fi_Email_7.setText("")
        image = np.array(Image.open(f"Avatar/Who1.png"))
        image = cv2.resize(image, (157, 150))
        image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        img = QtGui.QImage(image, image.shape[1], image.shape[0], image.strides[0],
                           QtGui.QImage.Format_RGB888)  # tổng số pixel quét của ảnh
        self.lbl_AvatarGV_7.setPixmap(QtGui.QPixmap.fromImage(img))
    def GetGV_7(self):

        row = self.tbl_DSGV_7.currentIndex().row()
        ms = self.tbl_DSGV_7.item(row, 0).text()
        for row in cursor.execute(f"select * from GIANGVIEN,KHOA WHERE MAGV='{ms}' AND KHOA.MAKHOA=GIANGVIEN.MAKHOA"):
            self.fi_IDGV_7.setText(row[0])
            self.fi_HoTenGV_7.setText(row[1])
            self.fi_SDT_7.setText(row[2])
            self.fi_NgaySinhGV_7.setDate(
                QtCore.QDate(int(row[3].split('-')[0]), int(row[3].split('-')[1]), int(row[3].split('-')[2])))
            self.fi_CMND_7.setText(row[4])
            self.fi_DanToc_7.setText(row[5])
            self.fi_TrinhDo_7.setText(row[6])
            self.fi_GioiTinhGV_7.setCurrentText(row[7])
            self.fi_Email_7.setText(row[8])
            self.fi_DDThuongTru_7.setText(row[10])
            self.fi_DCTamTru_7.setText(row[11])
            self.fi_Khoa_7.setCurrentText(row[16]+"-"+row[15])
            if row[12] == None:
                image = np.array(Image.open(f"Avatar/Who1.png"))
                self.image_GV=image
                image = cv2.resize(image, (157, 150))
                image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
                img = QtGui.QImage(image, image.shape[1], image.shape[0], image.strides[0],
                                   QtGui.QImage.Format_RGB888)  # tổng số pixel quét của ảnh
                self.lbl_AvatarGV_7.setPixmap(QtGui.QPixmap.fromImage(img))
            else:
                image = np.array(Image.open(f"Avatar/{row[12]}"))
                self.image_GV = cv2.cvtColor(image,cv2.COLOR_BGR2RGB)
                image = cv2.resize(image, (157, 150))
                img = QtGui.QImage(image, image.shape[1], image.shape[0], image.strides[0],
                                   QtGui.QImage.Format_RGB888)  # tổng số pixel quét của ảnh
                self.lbl_AvatarGV_7.setPixmap(QtGui.QPixmap.fromImage(img))
    def loadPageGV(self):

        #load table giảng viên
        row = 0
        lstGV = []
        for row1 in cursor.execute(f"select * from GIANGVIEN"):
            LHP = {}
            LHP["ID"] = row1[0]
            LHP["name"] = row1[1]
            lstGV.append(LHP)

        self.tbl_DSGV_7.setColumnWidth(0, 200)
        self.tbl_DSGV_7.setColumnWidth(1, 250)
        self.tbl_DSGV_7.setRowCount(len(lstGV))
        for mh in lstGV:
            self.tbl_DSGV_7.setItem(row, 0, QtWidgets.QTableWidgetItem(mh["ID"]))
            self.tbl_DSGV_7.setItem(row, 1, QtWidgets.QTableWidgetItem(mh["name"]))
            row += 1
        #load combobox tìm kiếm giảng viên
        self.cbo_TimKiemGV_7.clear()
        self.cbo_TimKiemGV_7.addItem("ID")
        self.cbo_TimKiemGV_7.addItem("Họ Tên")
        # load combobox khoa
        self.fi_Khoa_7.clear()
        for row1 in cursor.execute(f"select * from KHOA"):
            self.fi_Khoa_7.addItem(row1[1]+"-"+row1[0])

        self.fi_GioiTinhGV_7.clear()

        self.fi_GioiTinhGV_7.addItem("Nam")
        self.fi_GioiTinhGV_7.addItem("Nữ")
        self.fi_GioiTinhGV_7.addItem("Khác")
        self.KhoiTaoPageGV()

    def KhoiTaoPageGV(self):
        self.btn_ThemGV_7.setVisible(True)
        self.btn_SuaGV_7.setVisible(True)
        self.btn_XoaGV_7.setVisible(True)
        self.btn_LuuGV_7.setVisible(False)
        self.btn_HuyGV_7.setVisible(False)
        self.fi_IDGV_7.setEnabled(False)
        self.fi_HoTenGV_7.setEnabled(False)
        self.fi_SDT_7.setEnabled(False)
        self.fi_Khoa_7.setEnabled(False)
        self.fi_DCTamTru_7.setEnabled(False)
        self.fi_DDThuongTru_7.setEnabled(False)
        self.fi_GioiTinhGV_7.setEnabled(False)
        self.fi_CMND_7.setEnabled(False)
        self.fi_DanToc_7.setEnabled(False)
        self.fi_TrinhDo_7.setEnabled(False)
        self.fi_Email_7.setEnabled(False)
        self.fi_Khoa_7.setCurrentIndex(-1)
        self.fi_GioiTinhGV_7.setCurrentIndex(-1)
        self.btn_ChonAnhGV_7.setVisible(False)
        self.fi_NgaySinhGV_7.setDate(QtCore.QDate(2000,1,1))
        image = np.array(Image.open(f"Avatar/Who1.png"))
        image = cv2.resize(image, (157, 150))
        image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        img = QtGui.QImage(image, image.shape[1], image.shape[0], image.strides[0],
                           QtGui.QImage.Format_RGB888)  # tổng số pixel quét của ảnh
        self.lbl_AvatarGV_7.setPixmap(QtGui.QPixmap.fromImage(img))

    ######################################################################################################
    # page lịch dạy
    def loadPageDD(self):

        self.setStysheetBtn()
        self.btnDiemDanh.setStyleSheet("background-color: rgb(117, 117, 117);")
        if self.Quyen=="GV" or self.Quyen=="AD":
            self.stackedWidget.setCurrentWidget(self.page_LichDay)
            self.loadThoiKhoaBieu()
        elif self.Quyen=="SV":
            self.stackedWidget.setCurrentWidget(self.page_DDSV)
            self.loadTTDiemDanh()

    def GetBuoiHocDD(self):

        row = self.tbl_DSBuoiHoc_6.currentIndex().row()
        ms = self.tbl_DSBuoiHoc_6.item(row, 0).text()
        for row in cursor.execute(f"select * from BUOIHOC WHERE MABH='{ms}'"):
            self.fi_IDBH_6.setText(row[0])
            self.fi_Ngay_6.setDate(
                QtCore.QDate(int(row[2].split('-')[0]), int(row[2].split('-')[1]), int(row[2].split('-')[2])))
            self.fi_GioBD_6.setTime(QtCore.QTime(int(tiet_gio[row[3]].split(":")[0]), int(tiet_gio[row[3]].split(":")[1])))
            self.fi_GioKT_6.setTime(QtCore.QTime(int(tiet_gio[row[4]].split(":")[0]), int(tiet_gio[row[4]].split(":")[1])))
            self.fi_Phong_6.setText(row[5])

    def GetLopHPDD(self):

        row = self.tbl_DSLopHP_6.currentIndex().row()
        ms = self.tbl_DSLopHP_6.item(row, 0).text()
        for row in cursor.execute(f"select * from LOPMONHOC,MONHOC, GIANGVIEN WHERE LOPMONHOC.MALOPMH='{ms}' "
                                  f"AND LOPMONHOC.MAMH=MONHOC.MAMH AND LOPMONHOC.MAGV=GIANGVIEN.MAGV "):
            self.fi_MonHoc_6.setText(row[7])
            self.fi_IDLop_6.setText(row[0])
            self.fi_GiaoVien_6.setText(row[14])
            self.fi_SiSo_6.setText(str(row[5]))
            self.fi_NgayBD_6.setDate(
                QtCore.QDate(int(row[2].split('-')[0]), int(row[2].split('-')[1]), int(row[2].split('-')[2])))
            self.fi_NgayKT_6.setDate(
                QtCore.QDate(int(row[3].split('-')[0]), int(row[3].split('-')[1]), int(row[3].split('-')[2])))

        row = 0
        lstBuoiHoc = []
        for row1 in cursor.execute(f"select * from BUOIHOC WHERE MALOPMH='{ms}' ORDER BY BUOIHOC.NGAYHOC"):
            LHP = {}
            LHP["ID"] = row1[0]
            y = str(row1[2]).split("-")[0]
            m = str(row1[2]).split("-")[1]
            d = str(row1[2]).split("-")[2]
            LHP["date"] = d + "/" + m + "/" + y
            lstBuoiHoc.append(LHP)

        self.tbl_DSBuoiHoc_6.setColumnWidth(0, 150)
        self.tbl_DSBuoiHoc_6.setColumnWidth(1, 150)
        self.tbl_DSBuoiHoc_6.setRowCount(len(lstBuoiHoc))
        for mh in lstBuoiHoc:
            self.tbl_DSBuoiHoc_6.setItem(row, 0, QtWidgets.QTableWidgetItem(mh["ID"]))
            self.tbl_DSBuoiHoc_6.setItem(row, 1, QtWidgets.QTableWidgetItem(mh["date"]))
            row += 1

    def loadThoiKhoaBieu(self):
        cursor.execute(f"SELECT COUNT(*) FROM HOCKI")
        data = cursor.fetchall()
        str=""
        if self.Quyen=="SV":
            return
        elif self.Quyen=="AD":
            str=f"select LOPMONHOC.MALOPMH ,MONHOC.TENMH from LOPMONHOC, MONHOC,HOCKI WHERE MONHOC.MAMH=LOPMONHOC.MAMH AND LOPMONHOC.MAHK=HOCKI.MAHK AND HOCKI.MAHK='{data[0][0]}'"
        elif self.Quyen=="GV":
            str=f"select LOPMONHOC.MALOPMH ,MONHOC.TENMH from LOPMONHOC, MONHOC, HOCKI WHERE MONHOC.MAMH=LOPMONHOC.MAMH AND LOPMONHOC.MAGV='{self.ID_TK}' AND LOPMONHOC.MAHK=HOCKI.MAHK AND HOCKI.MAHK='{data[0][0]}'"
        row = 0
        self.lstTKB = []
        for row1 in cursor.execute(str):
            LHP = {}
            LHP["ID"] = row1[0]
            LHP["MH"] = row1[1]
            self.lstTKB.append(LHP)
        self.tbl_DSLopHP_6.setColumnWidth(0, 150)
        self.tbl_DSLopHP_6.setColumnWidth(1, 250)
        self.tbl_DSLopHP_6.setRowCount(len(self.lstTKB))
        for mh in self.lstTKB:
            self.tbl_DSLopHP_6.setItem(row, 0, QtWidgets.QTableWidgetItem(mh["ID"]))
            self.tbl_DSLopHP_6.setItem(row, 1, QtWidgets.QTableWidgetItem(mh["MH"]))
            row += 1
        self.fi_MonHoc_6.setEnabled(False)
        self.fi_GiaoVien_6.setEnabled(False)
        self.fi_NgayBD_6.setEnabled(False)
        self.fi_IDLop_6.setEnabled(False)
        self.fi_SiSo_6.setEnabled(False)
        self.fi_NgayKT_6.setEnabled(False)
        self.fi_IDBH_6.setEnabled(False)
        self.fi_Ngay_6.setEnabled(False)
        self.fi_GioBD_6.setEnabled(False)
        self.fi_GioKT_6.setEnabled(False)
        self.fi_Phong_6.setEnabled(False)

    def ktDiemDanh(self):

        cursor.execute(f"select *from CHITIETDD WHERE MABH='{self.fi_IDBH_6.text()}'")
        data = cursor.fetchall()
        if data != []:
            return True
        return False
    def ktNgayDD(self):
        str=time.strftime("%d/%m/20%y")
        if str==self.fi_Ngay_6.text():
            return True
        return  False
    def ktGioDD(self):
        ht=time.strftime("%H:%M")
        bd=self.chuyenGio(self.fi_GioBD_6.text())
        t=int(ht.split(":")[0])*60+int(ht.split(":")[1])
        b=int(bd.split(":")[0])*60+int(bd.split(":")[1])
        a=0
        if(t>b):
            a=t-b
        else:
            a=b-t
        if a>30:
            return False
        return True
    def OpenDiemDanh(self):

        if self.fi_IDBH_6.text() == "":
            msg = QMessageBox()
            msg.setIcon(QMessageBox.Warning)
            msg.setWindowTitle("Thông báo")
            msg.setText("Vui lòng chọn buổi học ")
            msg.setStandardButtons(QMessageBox.Ok)
            msg.exec_()
        elif self.ktDiemDanh()==True:
            msg = QMessageBox()
            msg.setIcon(QMessageBox.Warning)
            msg.setWindowTitle("Thông báo")
            msg.setText("Buổi học đã được điểm danh. Bạn không thể thực hiện điểm danh lại")
            msg.setStandardButtons(QMessageBox.Ok)
            msg.exec_()
        elif self.ktNgayDD()==False:
            msg = QMessageBox()
            msg.setIcon(QMessageBox.Warning)
            msg.setWindowTitle("Thông báo")
            msg.setText("Bạn chưa được phép điểm danh buổi học này!!!(ngày chưa hợp lệ)")
            msg.setStandardButtons(QMessageBox.Ok)
            msg.exec_()
        elif self.ktGioDD() == False:
            msg = QMessageBox()
            msg.setIcon(QMessageBox.Warning)
            msg.setWindowTitle("Thông báo")
            msg.setText("Bạn không được phép điểm danh buổi học này!!!(giờ chưa hợp lệ)")
            msg.setStandardButtons(QMessageBox.Ok)
            msg.exec_()
        else:


                self.fi_MonHoc_33.setText(self.fi_MonHoc_6.text())
                self.fi_IDBH_33.setText(self.fi_IDBH_6.text())
                self.fi_SiSo_3.setText(self.fi_SiSo_6.text())
                self.fi_LopHoc_3.setText(self.fi_IDLop_6.text())
                self.fi_GiangVien_3.setText(self.fi_GiaoVien_6.text())
                self.fi_Phong_3.setText(self.fi_Phong_6.text())
                h = int(self.fi_GioBD_6.text().split(":")[0])
                m = int(self.fi_GioBD_6.text().split(":")[1].split(" ")[0])
                s = self.fi_GioBD_6.text().split(":")[1].split(" ")[1]
                if(s=='CH'):
                    h+=12
                self.fi_GioBD_3.setTime(QtCore.QTime(h,m))
                h1 = int(self.fi_GioKT_6.text().split(":")[0])
                m1 = int(self.fi_GioKT_6.text().split(":")[1].split(" ")[0])
                s1 = self.fi_GioKT_6.text().split(":")[1].split(" ")[1]
                if (s1 == 'CH'):
                    h1 += 12
                self.fi_GioKT_3.setTime(QtCore.QTime(h1, m1))
                self.stackedWidget.setCurrentWidget(self.page_DiemDanh)
                self.fi_MonHoc_33.setEnabled(False)
                self.fi_IDBH_33.setEnabled(False)
                self.fi_SiSo_3.setEnabled(False)
                self.fi_LopHoc_3.setEnabled(False)
                self.fi_GiangVien_3.setEnabled(False)
                self.fi_Phong_3.setEnabled(False)
                self.fi_GioKT_3.setEnabled(False)
                self.fi_GioBD_3.setEnabled(False)
                self.fi_IDSV_3.setEnabled(False)
                self.fi_HoTenSV_3.setEnabled(False)
                self.fi_ThoiGianDD_3.setEnabled(False)
                self.fi_IDSV_3.setText("")
                self.fi_HoTenSV_3.setText("")
                self.fi_ThoiGianDD_3.setTime(QtCore.QTime(12,0))
                #load sinh viên trong lớp
                row = 0
                lstSVBH = []
                for row1 in cursor.execute(f"select * from CHITIETLHP,SINHVIEN WHERE SINHVIEN.MASV=CHITIETLHP.MASV AND MALOPMH='{self.fi_IDLop_6.text()}'"):
                    LHP = {}
                    LHP["ID"] = row1[1]
                    LHP["name"]=row1[3]
                    LHP["dd"] = "vắng"
                    LHP["ghichu"] = ""
                    LHP["tg"] = ""
                    lstSVBH.append(LHP)
                self.tbl_DSSV_3.setColumnWidth(0, 120)
                self.tbl_DSSV_3.setColumnWidth(1, 180)
                self.tbl_DSSV_3.setColumnWidth(2, 120)
                self.tbl_DSSV_3.setColumnWidth(3, 120)
                self.tbl_DSSV_3.setColumnWidth(4, 120)
                self.tbl_DSSV_3.setRowCount(len(lstSVBH))
                for mh in lstSVBH:
                    self.tbl_DSSV_3.setItem(row, 0, QtWidgets.QTableWidgetItem(mh["ID"]))
                    self.tbl_DSSV_3.setItem(row, 1, QtWidgets.QTableWidgetItem(mh["name"]))
                    self.tbl_DSSV_3.setItem(row, 2, QtWidgets.QTableWidgetItem(mh["dd"]))
                    self.tbl_DSSV_3.setItem(row, 3, QtWidgets.QTableWidgetItem(mh["tg"]))
                    self.tbl_DSSV_3.setItem(row, 4, QtWidgets.QTableWidgetItem(mh["ghichu"]))

                    row += 1
    ######################################################################################################
    # page điểm danh
    def SaveDD(self):

        try:
            for i in range(self.tbl_DSSV_3.rowCount()):
                hinhanh=self.fi_IDBH_33.text()+"_"+self.tbl_DSSV_3.item(i, 0).text()+".png"
                if self.tbl_DSSV_3.item(i, 2).text() == "có mặt":
                    cursor.execute("INSERT INTO CHITIETDD "
                                       "Values(?,?,?,?,?,?)", self.fi_IDBH_33.text()
                                   , self.tbl_DSSV_3.item(i, 0).text(),hinhanh,self.tbl_DSSV_3.item(i, 3).text(),
                                   self.tbl_DSSV_3.item(i, 4).text(), self.tbl_DSSV_3.item(i, 2).text())
                    con.commit()
                elif self.tbl_DSSV_3.item(i, 2).text() == "vắng":
                    cursor.execute("INSERT INTO CHITIETDD(MABH,MASV,GHICHU, TINHTRANG) "
                                   "Values(?,?,?,?)", self.fi_IDBH_33.text()
                                   , self.tbl_DSSV_3.item(i, 0).text(), self.tbl_DSSV_3.item(i, 4).text(),
                                   self.tbl_DSSV_3.item(i, 2).text())
                    con.commit()
            msg = QMessageBox()
            msg.setIcon(QMessageBox.NoIcon)
            msg.setWindowTitle("Thông báo")
            msg.setText("Thành công")
            msg.setStandardButtons(QMessageBox.Ok)
            result = msg.exec_()
        except:
            msg = QMessageBox()
            msg.setIcon(QMessageBox.Warning)
            msg.setWindowTitle("Thông báo")
            msg.setText("Lỗi")
            msg.setStandardButtons(QMessageBox.Ok)
            result = msg.exec_()

    def BackLichDay(self):
        self.stackedWidget.setCurrentWidget(self.page_LichDay)
        self.DongCam()
    def DongCam(self):
        self.t = 0
        image = cv2.imread("Avatar/pic.png")
        image = cv2.resize(image, (721, 401))
        img = QtGui.QImage(image, image.shape[1], image.shape[0], image.strides[0],
                               QtGui.QImage.Format_RGB888)
        self.lbl_Cam_3.setPixmap(QtGui.QPixmap.fromImage(img))
        image = np.array(Image.open(f"Avatar/Who1.png"))
        image = cv2.resize(image, (173, 120))
        image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        img = QtGui.QImage(image, image.shape[1], image.shape[0], image.strides[0],
                           QtGui.QImage.Format_RGB888)  # tổng số pixel quét của ảnh
        self.lbl_AvatarDD_3.setPixmap(QtGui.QPixmap.fromImage(img))
        self.fi_IDSV_3.setText("")
        self.fi_HoTenSV_3.setText("")
        self.fi_ThoiGianDD_3.setTime(QtCore.QTime(12,0))
    def ThucHienDD(self):

        if self.fi_IDSV_3.text()!="":
            for row in cursor.execute(f"select * from SINHVIEN Where MASV='{self.fi_IDSV_3.text()}'"):
                self.fi_HoTenSV_3.setText(row[1])
                if row[11] == None:
                    image = np.array(Image.open(f"Avatar/Who1.png"))
                    image = cv2.resize(image, (205, 109))
                    image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
                    img = QtGui.QImage(image, image.shape[1], image.shape[0], image.strides[0],
                                       QtGui.QImage.Format_RGB888)  # tổng số pixel quét của ảnh
                    self.lbl_AvatarDD_3.setPixmap(QtGui.QPixmap.fromImage(img))
                else:
                    image = np.array(Image.open(f"Avatar/{row[11]}"))
                    image = cv2.resize(image, (173, 120))

                    img = QtGui.QImage(image, image.shape[1], image.shape[0], image.strides[0],
                                       QtGui.QImage.Format_RGB888)  # tổng số pixel quét của ảnh
                    self.lbl_AvatarDD_3.setPixmap(QtGui.QPixmap.fromImage(img))
                    string = time.strftime('%H:%M:%S %p')
                    self.fi_ThoiGianDD_3.setTime(QtCore.QTime(int(string.split(":")[0]),int(string.split(":")[1])))
                    for i in range(self.tbl_DSSV_3.rowCount()):
                        if self.tbl_DSSV_3.item(i,0).text() ==self.fi_IDSV_3.text():
                            self.tbl_DSSV_3.setItem(i, 2, QtWidgets.QTableWidgetItem("có mặt"))
                            self.tbl_DSSV_3.setItem(i, 3, QtWidgets.QTableWidgetItem(self.fi_ThoiGianDD_3.text()))
                            h1=self.chuyenGio(self.fi_GioBD_3.text())
                            h2=self.chuyenGio(self.fi_ThoiGianDD_3.text())
                            bd=int(h1.split(":")[0])*60+int(h1.split(":")[1])
                            dd = int(h2.split(":")[0])*60 + int(h2.split(":")[1])
                            if (dd-bd)>30 and dd>bd:
                                self.tbl_DSSV_3.setItem(i, 4, QtWidgets.QTableWidgetItem("quá trễ"))
                            elif (dd-bd)>0 and dd>bd:
                                self.tbl_DSSV_3.setItem(i, 4, QtWidgets.QTableWidgetItem("trễ "+str(dd-bd)+" phút"))



    def OpenCamDiemDanh(self):
        self.FPS = 0
        st = 0
        self.cam = cv2.VideoCapture(0)
        database = {}
        myfile = open("data.pkl", "rb")
        database = pickle.load(myfile)
        myfile.close()
        while True:
            Ok, self.frame = self.cam.read()
            self.frame = cv2.cvtColor(self.frame, cv2.COLOR_BGR2RGB)
            faces = face_detector.detect_faces(self.frame)  # cắt gương mặt
            for face in faces:
                bounding_box = face['box']
                try:
                    self.cuttedFace = self.frame[bounding_box[1]:bounding_box[1] + bounding_box[3],
                         bounding_box[0]:bounding_box[0] + bounding_box[2]]

                    cv2.rectangle(self.frame,
                      (bounding_box[0], bounding_box[1]),
                      (bounding_box[0]+bounding_box[2], bounding_box[1] + bounding_box[3]),
                      (0,155,255),
                      2)
                    try:
                        self.cuttedFace = cv2.resize(self.cuttedFace, (160, 160))
                        faceDD=cv2.cvtColor(self.frame,cv2.COLOR_RGB2BGR)
                        faceDD = cv2.resize(faceDD, (160, 160))
                        mean, std = self.cuttedFace.mean(), self.cuttedFace.std()
                        self.cuttedFace= (self.cuttedFace - mean) / std
                        self.cuttedFace= expand_dims(self.cuttedFace, axis=0)
                        signature = MyFaceNet.predict(self.cuttedFace)
                        min_dist = 100
                        identity = ' '
                        for key, value in database.items():
                            dist = np.linalg.norm(value - signature)
                            if dist < min_dist:
                                min_dist = dist
                                identity = key
                        x=False
                        print(identity)
                        for i in range(self.tbl_DSSV_3.rowCount()):
                            if self.tbl_DSSV_3.item(i, 0).text() == identity:
                                self.fi_IDSV_3.setText(identity)

                                cv2.putText(self.frame, identity, (bounding_box[0], bounding_box[1] - 10),
                                            cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 0), 1,
                                            cv2.LINE_AA)
                                cv2.imwrite("AnhDiemDanh/"+f"{self.fi_IDBH_33.text()}_{self.fi_IDSV_3.text()}.png",
                                            faceDD)
                                x=True
                                self.ThucHienDD()
                        if x==False:
                            cv2.putText(self.frame, "unknown", (bounding_box[0], bounding_box[1] - 10),
                                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 0), 1,
                                        cv2.LINE_AA)
                    except:
                        pass
                except:
                    pass
            self.update()
            self.t = 1
            if cv2.waitKey(1) == ord('q') or self.t == 0:
                break
        self.cam.release()
        cv2.destroyAllWindows()

    def update(self):

        text = "Time:" + str(time.strftime(("%H:%M %p")))
        ps.putBText(self.frame, text, text_offset_x=10, text_offset_y=10, vspace=10, hspace=10, font_scale=0.8,
                        background_RGB=(100, 100, 100), text_RGB=(199, 150, 255))
        self.setPhoto(self.frame)


    def setPhoto(self, image):
        image = cv2.resize(image, (721, 401))
        img = QtGui.QImage(image, image.shape[1], image.shape[0], image.strides[0],
                               QtGui.QImage.Format_RGB888)  # tổng số pixel quét của ảnh
        self.lbl_Cam_3.setPixmap(QtGui.QPixmap.fromImage(img))
    ######################################################################################################
    # page buổi học
    def ChiTietDD(self):

        self.stackedWidget.setCurrentWidget(self.page_ChiTietDD)
        row = 0
        lstBH = []
        for row1 in cursor.execute(f"select * from BUOIHOC WHERE MALOPMH='{self.fi_IDLHP_4.text()}' ORDER BY BUOIHOC.NGAYHOC"):
            LHP = {}
            LHP["ID"] = row1[0]
            y = str(row1[2]).split("-")[0]
            m = str(row1[2]).split("-")[1]
            d = str(row1[2]).split("-")[2]
            LHP["date"] = d + "/" + m + "/" + y
            lstBH.append(LHP)
        self.tbl_DSBuoiHoc_8.setColumnWidth(0, 150)
        self.tbl_DSBuoiHoc_8.setColumnWidth(1, 150)
        self.tbl_DSBuoiHoc_8.setRowCount(len(lstBH))
        for mh in lstBH:
            self.tbl_DSBuoiHoc_8.setItem(row, 0, QtWidgets.QTableWidgetItem(mh["ID"]))
            self.tbl_DSBuoiHoc_8.setItem(row, 1, QtWidgets.QTableWidgetItem(mh["date"]))
            row += 1
    def XoaBH(self):

        if self.fi_IDBH_4.text()=="":
            msg = QMessageBox()
            msg.setIcon(QMessageBox.Warning)
            msg.setWindowTitle("Thông báo")
            msg.setText("Vui lòng buổi học muốn xóa")
            msg.setStandardButtons(QMessageBox.Ok)
            msg.exec_()
        else:
            try:
                cursor.execute("DELETE BUOIHOC "
                               "WHERE MABH=?", self.fi_IDBH_4.text())
                con.commit()
                msg = QMessageBox()
                msg.setIcon(QMessageBox.NoIcon)
                msg.setWindowTitle("Thông báo")
                msg.setText("Xóa thành công")
                msg.setStandardButtons(QMessageBox.Ok)
                result = msg.exec_()
                self.KhoiTaoBH()
                row = 0
                self.lstBH = []
                for row1 in cursor.execute(f"select * from BUOIHOC WHERE MALOPMH='{self.fi_IDLHP_4.text()}'"):
                    LHP = {}
                    LHP["ID"] = row1[0]
                    y = str(row1[2]).split("-")[0]
                    m = str(row1[2]).split("-")[1]
                    d = str(row1[2]).split("-")[2]
                    LHP["date"] = d + "/" + m + "/" + y
                    LHP["room"] = row1[5]
                    self.lstBH.append(LHP)
                self.tbl_DSBuoiHoc_4.setColumnWidth(0, 150)
                self.tbl_DSBuoiHoc_4.setColumnWidth(1, 150)
                self.tbl_DSBuoiHoc_4.setColumnWidth(2, 110)
                self.tbl_DSBuoiHoc_4.setRowCount(len(self.lstBH))
                for mh in self.lstBH:
                    self.tbl_DSBuoiHoc_4.setItem(row, 0, QtWidgets.QTableWidgetItem(mh["ID"]))
                    self.tbl_DSBuoiHoc_4.setItem(row, 1, QtWidgets.QTableWidgetItem(mh["date"]))
                    self.tbl_DSBuoiHoc_4.setItem(row, 2, QtWidgets.QTableWidgetItem(mh["room"]))
                    row += 1
            except:
                msg = QMessageBox()
                msg.setIcon(QMessageBox.Warning)
                msg.setWindowTitle("Thông báo")
                msg.setText("Lỗi")
                msg.setStandardButtons(QMessageBox.Ok)
                result = msg.exec_()
    def LuuBH(self):

        if self.thembh == True:
            if self.fi_PhongHoc_4.currentIndex == -1:
                msg = QMessageBox()
                msg.setIcon(QMessageBox.Warning)
                msg.setWindowTitle("Thông báo")
                msg.setText("Vui lòng nhập đầy đủ thông tin!!")
                msg.setStandardButtons(QMessageBox.Ok)
                msg.exec_()
            else:
                try:
                    # bd=self.chuyenGio(self.fi_GioBD_4.text())
                    # kt = self.chuyenGio(self.fi_GioKT_4.text())
                    cursor.execute("SET DATEFORMAT DMY INSERT INTO BUOIHOC "
                                       "Values(?,?,?,?,?,?)", self.fi_IDBH_4.text(), self.fi_IDLHP_4.text(),
                                       self.fi_NgayHoc_4.text(),
                                       self.fi_GioBD_4.currentText(), self.fi_GioKT_4.currentText(),self.fi_PhongHoc_4.currentText())
                    con.commit()
                    msg = QMessageBox()
                    msg.setIcon(QMessageBox.NoIcon)
                    msg.setWindowTitle("Thông báo")
                    msg.setText("Thêm buổi học thành công")
                    msg.setStandardButtons(QMessageBox.Ok)
                    result = msg.exec_()
                    self.KhoiTaoBH()
                    row = 0
                    self.lstBH = []
                    for row1 in cursor.execute(f"select * from BUOIHOC WHERE MALOPMH='{self.fi_IDLHP_4.text()}' ORDER BY NGAYHOC"):
                        LHP = {}
                        LHP["ID"] = row1[0]
                        y = str(row1[2]).split("-")[0]
                        m = str(row1[2]).split("-")[1]
                        d = str(row1[2]).split("-")[2]
                        LHP["date"] = d + "/" + m + "/" + y
                        LHP["room"] = row1[5]
                        self.lstBH.append(LHP)
                    self.tbl_DSBuoiHoc_4.setColumnWidth(0, 150)
                    self.tbl_DSBuoiHoc_4.setColumnWidth(1, 150)
                    self.tbl_DSBuoiHoc_4.setColumnWidth(2, 110)
                    self.tbl_DSBuoiHoc_4.setRowCount(len(self.lstBH))
                    for mh in self.lstBH:
                        self.tbl_DSBuoiHoc_4.setItem(row, 0, QtWidgets.QTableWidgetItem(mh["ID"]))
                        self.tbl_DSBuoiHoc_4.setItem(row, 1, QtWidgets.QTableWidgetItem(mh["date"]))
                        self.tbl_DSBuoiHoc_4.setItem(row, 2, QtWidgets.QTableWidgetItem(mh["room"]))
                        row += 1
                except:
                    msg = QMessageBox()
                    msg.setIcon(QMessageBox.Warning)
                    msg.setWindowTitle("Thông báo")
                    msg.setText("Lỗi")
                    msg.setStandardButtons(QMessageBox.Ok)
                    result = msg.exec_()
        elif self.thembh == False:
            try:
                # bd = self.chuyenGio(self.fi_GioBD_4.text())
                # kt = self.chuyenGio(self.fi_GioKT_4.text())
                cursor.execute("SET DATEFORMAT DMY UPDATE BUOIHOC "
                                       "SET NGAYHOC=?,GIOBD=?,GIOKT=?, MAPH=? WHERE MABH=?",self.fi_NgayHoc_4.text(),
                                       self.fi_GioBD_4.currentText(), self.fi_GioKT_4.currentText(), self.fi_PhongHoc_4.currentText(), self.fi_IDBH_4.text())
                con.commit()
                msg = QMessageBox()
                msg.setIcon(QMessageBox.NoIcon)
                msg.setWindowTitle("Thông báo")
                msg.setText("Cập nhật buổi học thành công")
                msg.setStandardButtons(QMessageBox.Ok)
                result = msg.exec_()
                self.KhoiTaoBH()
                row = 0
                self.lstBH = []
                for row1 in cursor.execute(f"select * from BUOIHOC WHERE MALOPMH='{self.fi_IDLHP_4.text()}' ORDER BY NGAYHOC"):
                    LHP = {}
                    LHP["ID"] = row1[0]
                    y = str(row1[2]).split("-")[0]
                    m = str(row1[2]).split("-")[1]
                    d = str(row1[2]).split("-")[2]
                    LHP["date"] = d + "/" + m + "/" + y
                    LHP["room"] = row1[5]
                    self.lstBH.append(LHP)
                self.tbl_DSBuoiHoc_4.setColumnWidth(0, 150)
                self.tbl_DSBuoiHoc_4.setColumnWidth(1, 150)
                self.tbl_DSBuoiHoc_4.setColumnWidth(2, 110)
                self.tbl_DSBuoiHoc_4.setRowCount(len(self.lstBH))
                for mh in self.lstBH:
                    self.tbl_DSBuoiHoc_4.setItem(row, 0, QtWidgets.QTableWidgetItem(mh["ID"]))
                    self.tbl_DSBuoiHoc_4.setItem(row, 1, QtWidgets.QTableWidgetItem(mh["date"]))
                    self.tbl_DSBuoiHoc_4.setItem(row, 2, QtWidgets.QTableWidgetItem(mh["room"]))
                    row += 1
            except:
                msg = QMessageBox()
                msg.setIcon(QMessageBox.Warning)
                msg.setWindowTitle("Thông báo")
                msg.setText("Lỗi")
                msg.setStandardButtons(QMessageBox.Ok)
                result = msg.exec_()
    def GetBH(self):

        row = self.tbl_DSBuoiHoc_4.currentIndex().row()
        ms = self.tbl_DSBuoiHoc_4.item(row, 0).text()
        for row in cursor.execute(f"select * from BUOIHOC WHERE BUOIHOC.MABH='{ms}' "):
            self.fi_IDBH_4.setText(ms)
            self.fi_NgayHoc_4.setDate(
                QtCore.QDate(int(row[2].split('-')[0]), int(row[2].split('-')[1]), int(row[2].split('-')[2])))
            self.fi_PhongHoc_4.setCurrentText(row[5])
            self.fi_GioBD_4.setCurrentText(row[3])
            self.fi_GioKT_4.setCurrentText(row[4])
    def SuaBH(self):
        if self.fi_IDBH_4.text()=="":
            msg = QMessageBox()
            msg.setIcon(QMessageBox.NoIcon)
            msg.setWindowTitle("Thông báo")
            msg.setText("Vui lòng chọn buổi học cần cập nhật thông tin!!")
            msg.setStandardButtons(QMessageBox.Ok)
            result = msg.exec_()
            self.loadPageGV()
        else:
            self.thembh = False
            self.btn_ThemBH_4.setVisible(False)
            self.btn_SuaBH_4.setVisible(False)
            self.btn_XoaBH_4.setVisible(False)
            self.btn_LuuBH_4.setVisible(True)
            self.btn_HuyBH_4.setVisible(True)
            self.fi_GioBD_4.setEnabled(True)
            self.fi_GioKT_4.setEnabled(True)
            self.fi_PhongHoc_4.setEnabled(True)
            self.fi_NgayHoc_4.setEnabled(True)
    def HuyBH(self):
        self.KhoiTaoBH()
    def ThemBH(self):
        self.thembh=True
        self.btn_ThemBH_4.setVisible(False)
        self.btn_SuaBH_4.setVisible(False)
        self.btn_XoaBH_4.setVisible(False)
        self.btn_LuuBH_4.setVisible(True)
        self.btn_HuyBH_4.setVisible(True)
        mabh=self.taoMaBH(self.fi_IDLHP_4.text())
        self.fi_IDBH_4.setText(mabh)
        self.fi_NgayHoc_4.setDate(QtCore.QDate(2000,1,1))
        self.fi_PhongHoc_4.setCurrentIndex(-1)
        self.fi_GioBD_4.setCurrentIndex(-1)
        self.fi_GioKT_4.setCurrentIndex(-1)
        self.fi_GioBD_4.setEnabled(True)
        self.fi_GioKT_4.setEnabled(True)
        self.fi_PhongHoc_4.setEnabled(True)
        self.fi_NgayHoc_4.setEnabled(True)
    def KhoiTaoBH(self):
        self.btn_ThemBH_4.setVisible(True)
        self.btn_SuaBH_4.setVisible(True)
        self.btn_XoaBH_4.setVisible(True)
        self.btn_LuuBH_4.setVisible(False)
        self.btn_HuyBH_4.setVisible(False)
        self.fi_IDLHP_4.setEnabled(False)
        self.fi_IDBH_4.setEnabled(False)
        self.fi_NgayHoc_4.setEnabled(False)
        self.fi_GioBD_4.setEnabled(False)
        self.fi_MH_4.setEnabled(False)
        self.fi_GiangVien_4.setEnabled(False)
        self.fi_PhongHoc_4.setEnabled(False)
        self.fi_GioKT_4.setEnabled(False)
        self.fi_PhongHoc_4.setCurrentIndex(-1)
        self.fi_IDBH_4.setText("")
    def loadBuoiHoc(self):

        #load phòng
        self.fi_PhongHoc_4.clear()
        for row1 in cursor.execute(f"select * from PHONGHOC"):
            self.fi_PhongHoc_4.addItem(row1[0])
        #load table buổi học
        row=0
        self.lstBH=[]
        for row1 in cursor.execute(f"select * from BUOIHOC WHERE MALOPMH='{self.fi_IDLHP_4.text()}' ORDER BY BUOIHOC.NGAYHOC"):
            LHP = {}
            LHP["ID"] = row1[0]
            y=str(row1[2]).split("-")[0]
            m = str(row1[2]).split("-")[1]
            d = str(row1[2]).split("-")[2]
            LHP["date"] = d+"/"+m+"/"+y
            LHP["room"]=row1[5]
            self.lstBH.append(LHP)
        self.tbl_DSBuoiHoc_4.setColumnWidth(0, 150)
        self.tbl_DSBuoiHoc_4.setColumnWidth(1, 150)
        self.tbl_DSBuoiHoc_4.setColumnWidth(2, 110)
        self.tbl_DSBuoiHoc_4.setRowCount(len(self.lstBH))
        for mh in self.lstBH:
            self.tbl_DSBuoiHoc_4.setItem(row, 0, QtWidgets.QTableWidgetItem(mh["ID"]))
            self.tbl_DSBuoiHoc_4.setItem(row, 1, QtWidgets.QTableWidgetItem(mh["date"]))
            self.tbl_DSBuoiHoc_4.setItem(row, 2, QtWidgets.QTableWidgetItem(mh["room"]))
            row += 1
        #load combobox tiết
        self.fi_GioBD_4.clear()
        self.fi_GioKT_4.clear()
        for i in range(1,18):
            self.fi_GioBD_4.addItem(str(i))
        for i in range(1,18):
            self.fi_GioKT_4.addItem(str(i))
    def taoMaBH(self,malhp):
        cursor.execute(f"select count(MABH)+1 from BUOIHOC WHERE MALOPMH='{malhp}'")
        count= int(cursor.fetchall()[0][0])
        ma="Buoi_"+str(count)+"_"+malhp
        b=False
        while b==False:
            cursor.execute(f"select * from BUOIHOC WHERE MABH='{ma}'")
            bh = cursor.fetchall()
            if bh==[]:
                return ma
            else:
                count+=1
                ma = "Buoi_" + str(count) + "_" + malhp






    ######################################################################################################
    # page môn học
    def BackPageMH(self):
        if self.Quyen=="SV":
            self.stackedWidget.setCurrentWidget(self.page_MonHocSV)
        elif self.Quyen=='AD':
            self.stackedWidget.setCurrentWidget(self.page_MonHoc)
        elif self.Quyen == 'GV':
            self.stackedWidget.setCurrentWidget(self.page_MonHocGV)

    def DatLichHoc(self):
        if self.fi_IDLop_2.text()=="":
            msg = QMessageBox()
            msg.setIcon(QMessageBox.Warning)
            msg.setWindowTitle("Thông báo")
            msg.setText("Vui lòng chọn lớp học muốn xem lịch học!!")
            msg.setStandardButtons(QMessageBox.Ok)
            msg.exec_()
        else:
            self.fi_IDLHP_4.setText(self.fi_IDLop_2.text())
            self.fi_MH_4.setText(self.fi_TenMonHoc_2.text())
            self.fi_GiangVien_4.setText(self.fi_GiangVien_2.currentText().split("-")[0])
            self.stackedWidget.setCurrentWidget(self.page_LichHoc)
            self.loadBuoiHoc()
            if self.Quyen=="GV":
                self.btn_ThemBH_4.setVisible(False)
                self.btn_SuaBH_4.setVisible(False)
                self.btn_XoaBH_4.setVisible(False)

    def AllMH(self):
        row = 0
        self.lstMH = []
        for row1 in cursor.execute(f"select * from MONHOC"):
            MH = {}
            MH["ID"] = row1[0]
            MH["name"] = row1[1]
            MH["soTC"] = row1[2]
            self.lstMH.append(MH)
        self.tbl_MonHoc_2.setColumnWidth(0, 150)
        self.tbl_MonHoc_2.setColumnWidth(1, 280)
        self.tbl_MonHoc_2.setColumnWidth(2, 225)
        self.tbl_MonHoc_2.setRowCount(len(self.lstMH))
        for mh in self.lstMH:
            self.tbl_MonHoc_2.setItem(row, 0, QtWidgets.QTableWidgetItem(mh["ID"]))
            self.tbl_MonHoc_2.setItem(row, 1, QtWidgets.QTableWidgetItem(mh["name"]))
            self.tbl_MonHoc_2.setItem(row, 2, QtWidgets.QTableWidgetItem(str(mh["soTC"])))
            row += 1
    def TimMonHoc(self):
        if self.cbo_TimMH_2.currentText()=="ID":
            row = 0
            self.lstMH = []
            for row1 in cursor.execute(f"select * from MONHOC Where MAMH='{self.txt_TimMH_2.text()}'"):
                MH = {}
                MH["ID"] = row1[0]
                MH["name"] = row1[1]
                MH["soTC"] = row1[2]
                self.lstMH.append(MH)
            self.tbl_MonHoc_2.setColumnWidth(0, 150)
            self.tbl_MonHoc_2.setColumnWidth(1, 280)
            self.tbl_MonHoc_2.setColumnWidth(2, 225)
            self.tbl_MonHoc_2.setRowCount(len(self.lstMH))
            for mh in self.lstMH:
                self.tbl_MonHoc_2.setItem(row, 0, QtWidgets.QTableWidgetItem(mh["ID"]))
                self.tbl_MonHoc_2.setItem(row, 1, QtWidgets.QTableWidgetItem(mh["name"]))
                self.tbl_MonHoc_2.setItem(row, 2, QtWidgets.QTableWidgetItem(str(mh["soTC"])))
                row += 1
        elif self.cbo_TimMH_2.currentText()=="Tên Môn Học":
            row = 0
            self.lstMH = []
            for row1 in cursor.execute(f"select * from MONHOC Where TENMH LIKE N'%{self.txt_TimMH_2.text()}%'"):
                MH = {}
                MH["ID"] = row1[0]
                MH["name"] = row1[1]
                MH["soTC"] = row1[2]
                self.lstMH.append(MH)
            self.tbl_MonHoc_2.setColumnWidth(0, 150)
            self.tbl_MonHoc_2.setColumnWidth(1, 280)
            self.tbl_MonHoc_2.setColumnWidth(2, 225)
            self.tbl_MonHoc_2.setRowCount(len(self.lstMH))
            for mh in self.lstMH:
                self.tbl_MonHoc_2.setItem(row, 0, QtWidgets.QTableWidgetItem(mh["ID"]))
                self.tbl_MonHoc_2.setItem(row, 1, QtWidgets.QTableWidgetItem(mh["name"]))
                self.tbl_MonHoc_2.setItem(row, 2, QtWidgets.QTableWidgetItem(str(mh["soTC"])))
                row += 1
    def XoaSVKhoiLop(self):
        if self.fi_IDSV_2.text()=="":
            msg = QMessageBox()
            msg.setIcon(QMessageBox.Warning)
            msg.setWindowTitle("Thông báo")
            msg.setText("Vui lòng chọn học sinh xóa khỏi lớp")
            msg.setStandardButtons(QMessageBox.Ok)
            msg.exec_()
        elif self.fi_IDLop_2.text()=="":
            msg = QMessageBox()
            msg.setIcon(QMessageBox.Warning)
            msg.setWindowTitle("Thông báo")
            msg.setText("Vui lòng chọn lớp học phần")
            msg.setStandardButtons(QMessageBox.Ok)
            msg.exec_()
        else:
            try:
                cursor.execute("DELETE CHITIETLHP "
                               "WHERE MALOPMH=? AND MASV=?", self.fi_IDLop_2.text(), self.fi_IDSV_2.text())
                con.commit()
                msg = QMessageBox()
                msg.setIcon(QMessageBox.NoIcon)
                msg.setWindowTitle("Thông báo")
                msg.setText("Xóa thành công")
                msg.setStandardButtons(QMessageBox.Ok)
                result = msg.exec_()
                row = 0
                self.fi_IDSV_2.setText("")
                self.fi_HoTenSV_2.setText("")
                self.fi_LopSV_2.setText("")
                self.fi_KhoaSV_2.setText("")
                self.lstSVLHP = []
                for row1 in cursor.execute(f"select * from CHITIETLHP,SINHVIEN WHERE CHITIETLHP.MASV=SINHVIEN.MASV AND CHITIETLHP.MALOPMH='{self.fi_IDLop_2.text()}'"):
                    LHP = {}
                    LHP["ID"] = row1[2]
                    LHP["name"] = row1[3]
                    self.lstSVLHP.append(LHP)
                self.tbl_DSSV_2.setColumnWidth(0, 110)
                self.tbl_DSSV_2.setColumnWidth(1, 200)
                self.tbl_DSSV_2.setRowCount(len(self.lstSVLHP))
                for mh in self.lstSVLHP:
                    self.tbl_DSSV_2.setItem(row, 0, QtWidgets.QTableWidgetItem(mh["ID"]))
                    self.tbl_DSSV_2.setItem(row, 1, QtWidgets.QTableWidgetItem(mh["name"]))
                    row += 1
            except:
                msg = QMessageBox()
                msg.setIcon(QMessageBox.Warning)
                msg.setWindowTitle("Thông báo")
                msg.setText("Lỗi")
                msg.setStandardButtons(QMessageBox.Ok)
                result = msg.exec_()
    def ThemSVVaoLop(self):
        if self.fi_IDSV_2.text()=="":
            msg = QMessageBox()
            msg.setIcon(QMessageBox.Warning)
            msg.setWindowTitle("Thông báo")
            msg.setText("Vui lòng chọn học sinh muốn thêm vào lớp")
            msg.setStandardButtons(QMessageBox.Ok)
            msg.exec_()
        elif self.fi_IDLop_2.text()=="":
            msg = QMessageBox()
            msg.setIcon(QMessageBox.Warning)
            msg.setWindowTitle("Thông báo")
            msg.setText("Vui lòng chọn lớp học phần")
            msg.setStandardButtons(QMessageBox.Ok)
            msg.exec_()
        else:
            try:
                cursor.execute("INSERT INTO CHITIETLHP "
                               "Values(?,?)", self.fi_IDLop_2.text(), self.fi_IDSV_2.text())
                con.commit()
                msg = QMessageBox()
                msg.setIcon(QMessageBox.NoIcon)
                msg.setWindowTitle("Thông báo")
                msg.setText("Thêm thành công")
                msg.setStandardButtons(QMessageBox.Ok)
                result = msg.exec_()
                row = 0
                self.fi_IDSV_2.setText("")
                self.fi_HoTenSV_2.setText("")
                self.fi_LopSV_2.setText("")
                self.fi_KhoaSV_2.setText("")
                self.lstSVLHP = []
                for row1 in cursor.execute(
                        f"select * from CHITIETLHP,SINHVIEN WHERE CHITIETLHP.MASV=SINHVIEN.MASV AND CHITIETLHP.MALOPMH='{self.fi_IDLop_2.text()}'"):
                    LHP = {}
                    LHP["ID"] = row1[2]
                    LHP["name"] = row1[3]
                    self.lstSVLHP.append(LHP)
                self.tbl_DSSV_2.setColumnWidth(0, 110)
                self.tbl_DSSV_2.setColumnWidth(1, 200)
                self.tbl_DSSV_2.setRowCount(len(self.lstSVLHP))
                for mh in self.lstSVLHP:
                    self.tbl_DSSV_2.setItem(row, 0, QtWidgets.QTableWidgetItem(mh["ID"]))
                    self.tbl_DSSV_2.setItem(row, 1, QtWidgets.QTableWidgetItem(mh["name"]))
                    row += 1
            except:
                msg = QMessageBox()
                msg.setIcon(QMessageBox.Warning)
                msg.setWindowTitle("Thông báo")
                msg.setText("Lỗi")
                msg.setStandardButtons(QMessageBox.Ok)
                result = msg.exec_()
    def TimSVThemLop(self):
        for row in cursor.execute(f"select * from SINHVIEN,KHOA,LOP WHERE SINHVIEN.MASV='{self.txt_TimSV_2.text()}' "
                                  f"AND SINHVIEN.MALOP=LOP.MALOP AND LOP.MAKHOA=KHOA.MAKHOA"):
            self.fi_IDSV_2.setText(row[0])
            self.fi_HoTenSV_2.setText(row[1])
            self.fi_LopSV_2.setText(row[10])
            self.fi_KhoaSV_2.setText(row[17])
    def XoaLHP(self):
        if self.fi_IDLop_2.text()=="":
            msg = QMessageBox()
            msg.setIcon(QMessageBox.Warning)
            msg.setWindowTitle("Thông báo")
            msg.setText("Vui lòng chọn lớp muốn xóa??")
            msg.setStandardButtons(QMessageBox.Ok)
            msg.exec_()
        else:
            dssv = []
            for row in cursor.execute(f"select * from CHITIETLHP Where MALOPMH='{self.fi_IDLop_2.text()}'"):
                dssv.append(row[1])
            try:
                for i in dssv:
                    cursor.execute("DELETE CHITIETLHP WHERE MASV=?",i)
                    con.commit()
                cursor.execute("DELETE LOPMONHOC WHERE MALOPMH=?",self.fi_IDLop_2.text())
                con.commit()
                msg = QMessageBox()
                msg.setIcon(QMessageBox.NoIcon)
                msg.setWindowTitle("Thông báo")
                msg.setText("Xóa thành công")
                msg.setStandardButtons(QMessageBox.Ok)
                result = msg.exec_()
                self.loadLHP1(self.fi_IDMonHoc_2.text())
                self.loadMonHoc()
                self.KhoiTaoMH()
            except:
                msg = QMessageBox()
                msg.setIcon(QMessageBox.NoIcon)
                msg.setWindowTitle("Thông báo")
                msg.setText("Lỗi!!!")
                msg.setStandardButtons(QMessageBox.Ok)
                result = msg.exec_()



    def loadLHP1(self,str):
        cursor.execute(f"SELECT MAHK FROM HOCKI WHERE TENHK='{self.cbo_hocki.currentText()}'")
        data = cursor.fetchall()
        # load các lớp học phần
        row = 0
        self.lstLHP = []
        for row1 in cursor.execute(f"select * from LOPMONHOC,GIANGVIEN,HOCKI WHERE LOPMONHOC.MAGV=GIANGVIEN.MAGV "
                                   f"AND LOPMONHOC.MAMH='{str}' AND HOCKI.MAHK=LOPMONHOC.MAHK AND HOCKI.MAHK='{data[0][0]}'"):
            LHP = {}
            LHP["ID"] = row1[0]
            LHP["name"] = row1[8]
            self.lstLHP.append(LHP)
        self.tbl_LopHocPhan_2.setColumnWidth(0, 90)
        self.tbl_LopHocPhan_2.setColumnWidth(1, 169)
        self.tbl_LopHocPhan_2.setRowCount(len(self.lstLHP))
        for mh in self.lstLHP:
            self.tbl_LopHocPhan_2.setItem(row, 0, QtWidgets.QTableWidgetItem(mh["ID"]))
            self.tbl_LopHocPhan_2.setItem(row, 1, QtWidgets.QTableWidgetItem(mh["name"]))
            row += 1
    def LuuLHP(self):
        if self.themlhp==True:
            if self.fi_IDLop_2.text()=="" or self.fi_SiSo_2.text()==""  or self.fi_GiangVien_2.currentIndex==-1:
                msg = QMessageBox()
                msg.setIcon(QMessageBox.Warning)
                msg.setWindowTitle("Thông báo")
                msg.setText("Vui lòng nhập đầy đủ thông tin!!")
                msg.setStandardButtons(QMessageBox.Ok)
                msg.exec_()
            else:
                if self.fi_IDMonHoc_2.text()=="":
                    msg = QMessageBox()
                    msg.setIcon(QMessageBox.Warning)
                    msg.setWindowTitle("Thông báo")
                    msg.setText("Vui lòng chọn môn học muốn thêm lớp")
                    msg.setStandardButtons(QMessageBox.Ok)
                    msg.exec_()
                else:
                    try:
                        # bd=self.chuyenGio(self.fi_GioBD_22.text())
                        # kt = self.chuyenGio(self.fi_GioKT_22.text())
                        cursor.execute("SET DATEFORMAT DMY INSERT INTO LOPMONHOC "
                                       "Values(?,?,?,?,?,?,?)", self.fi_IDLop_2.text(),self.fi_IDMonHoc_2.text(),self.fi_NgayBatDau_2.text(),
                                       self.fi_NgayKetThuc_2.text(),self.fi_GiangVien_2.currentText().split("-")[1],self.fi_SiSo_2.text(),self.HK)
                        con.commit()
                        msg = QMessageBox()
                        msg.setIcon(QMessageBox.NoIcon)
                        msg.setWindowTitle("Thông báo")
                        msg.setText("Thêm lớp thành công")
                        msg.setStandardButtons(QMessageBox.Ok)
                        result = msg.exec_()
                        self.loadLHP1(self.fi_IDMonHoc_2.text())
                        self.loadMonHoc()
                        self.KhoiTaoMH()

                    except:
                        msg = QMessageBox()
                        msg.setIcon(QMessageBox.Warning)
                        msg.setWindowTitle("Thông báo")
                        msg.setText("Lỗi")
                        msg.setStandardButtons(QMessageBox.Ok)
                        result = msg.exec_()
        elif self.themlhp==False:
            if self.fi_IDLop_2.text()=="" or self.fi_SiSo_2.text()==""  or self.fi_GiangVien_2.currentIndex==-1:
                msg = QMessageBox()
                msg.setIcon(QMessageBox.Warning)
                msg.setWindowTitle("Thông báo")
                msg.setText("Vui lòng nhập đầy đủ thông tin!!")
                msg.setStandardButtons(QMessageBox.Ok)
                msg.exec_()
            else:
                if self.fi_IDMonHoc_2.text()=="":
                    msg = QMessageBox()
                    msg.setIcon(QMessageBox.Warning)
                    msg.setWindowTitle("Thông báo")
                    msg.setText("Vui lòng chọn môn học muốn lớp muốn cập nhật")
                    msg.setStandardButtons(QMessageBox.Ok)
                    msg.exec_()
                else:
                    try:
                        # bd=self.chuyenGio(self.fi_GioBD_22.text())
                        # kt = self.chuyenGio(self.fi_GioKT_22.text())
                        cursor.execute("SET DATEFORMAT DMY UPDATE LOPMONHOC "
                                       "SET MAMH=?,NGAYBD=?,NGAYKT=?,MAGV=?, SISO=? WHERE MALOPMH=?",self.fi_IDMonHoc_2.text(),self.fi_NgayBatDau_2.text(),
                                       self.fi_NgayKetThuc_2.text(),
                                       self.fi_GiangVien_2.currentText().split("-")[1],self.fi_SiSo_2.text(),
                                       self.fi_IDLop_2.text())
                        con.commit()
                        msg = QMessageBox()
                        msg.setIcon(QMessageBox.NoIcon)
                        msg.setWindowTitle("Thông báo")
                        msg.setText("Cập nhật lớp thành công")
                        msg.setStandardButtons(QMessageBox.Ok)
                        result = msg.exec_()
                        self.loadLHP1(self.fi_IDMonHoc_2.text())
                        self.loadMonHoc()
                        self.KhoiTaoMH()

                    except:
                        msg = QMessageBox()
                        msg.setIcon(QMessageBox.Warning)
                        msg.setWindowTitle("Thông báo")
                        msg.setText("Lỗi")
                        msg.setStandardButtons(QMessageBox.Ok)
                        result = msg.exec_()
    def SuaLHP(self):
        if self.fi_IDLop_2.text()=="":
            msg = QMessageBox()
            msg.setIcon(QMessageBox.NoIcon)
            msg.setWindowTitle("Thông báo")
            msg.setText("Vui lòng chọn lớp học cần cập nhật thông tin!!")
            msg.setStandardButtons(QMessageBox.Ok)
            result = msg.exec_()
        else:
            self.themlhp = False
            self.btn_DatLichHoc_2.setVisible(False)
            self.fi_GiangVien_2.setEnabled(True)
            self.fi_SiSo_2.setEnabled(True)
            self.fi_NgayBatDau_2.setEnabled(True)
            self.fi_NgayKetThuc_2.setEnabled(True)
            # self.fi_GioBD_22.setEnabled(True)
            # self.fi_GioKT_22.setEnabled(True)
            # self.fi_PhongHoc_2.setEnabled(True)
            self.btn_ThemLopHP_2.setVisible(False)
            self.btn_SuaLopHP_2.setVisible(False)
            self.btn_XoaLopHP_2.setVisible(False)
            self.btn_LuuLHP_2.setVisible(True)
            self.btn_HuyLHP_2.setVisible(True)
    def HuyLHP(self):
        self.KhoiTaoMH()
    def ThemLHP(self):
        self.themlhp=True
        self.btn_DatLichHoc_2.setVisible(False)
        self.fi_GiangVien_2.setEnabled(True)
        self.fi_SiSo_2.setEnabled(True)
        self.fi_NgayBatDau_2.setEnabled(True)
        self.fi_NgayKetThuc_2.setEnabled(True)
        # self.fi_GioBD_22.setEnabled(True)
        # self.fi_GioKT_22.setEnabled(True)
        # self.fi_PhongHoc_2.setEnabled(True)
        self.btn_ThemLopHP_2.setVisible(False)
        self.btn_SuaLopHP_2.setVisible(False)
        self.btn_XoaLopHP_2.setVisible(False)
        self.btn_LuuLHP_2.setVisible(True)
        self.btn_HuyLHP_2.setVisible(True)
        self.fi_GiangVien_2.setCurrentIndex(-1)
        self.fi_GiangVien_2.setCurrentIndex(-1)
        self.fi_SiSo_2.setText("")
        # self.fi_PhongHoc_2.setCurrentIndex(-1)
        self.fi_NgayBatDau_2.setDate(QtCore.QDate(2000, 1, 1))
        self.fi_NgayKetThuc_2.setDate(QtCore.QDate(2000, 1, 1))
        # self.fi_GioBD_22.setTime(QtCore.QTime(12,0))
        # self.fi_GioKT_22.setTime(QtCore.QTime(12,0))

        sql = " EXEC LOPHP_ID "
        cursor.execute(sql)
        data = cursor.fetchall()
        self.fi_IDLop_2.setText(data[0][0])
    def kTXoaMH(self):
        cursor.execute(f'Select *from LOPMONHOC WHERE MAMH=?',self.fi_IDMonHoc_2.text())
        data = cursor.fetchall()
        if data==[]:
            return False
        else:
            return True
    def XoaMH(self):
        if self.fi_IDMonHoc_2.text()=="":
            msg = QMessageBox()
            msg.setIcon(QMessageBox.Warning)
            msg.setWindowTitle("Thông báo")
            msg.setText("Vui lòng chọn môn học muốn xóa??")
            msg.setStandardButtons(QMessageBox.Ok)
            msg.exec_()
        else:
            if self.kTXoaMH()==True:
                msg = QMessageBox()
                msg.setIcon(QMessageBox.Warning)
                msg.setWindowTitle("Thông báo")
                msg.setText("Không thể xóa!!")
                msg.setStandardButtons(QMessageBox.Ok)
                msg.exec_()
            elif self.kTXoaMH()==False:
                try:
                    print("n")
                    cursor.execute("DELETE MONHOC WHERE MAMH=?",self.fi_IDMonHoc_2.text())
                    con.commit()
                    msg = QMessageBox()
                    msg.setIcon(QMessageBox.NoIcon)
                    msg.setWindowTitle("Thông báo")
                    msg.setText("Xóa thành công")
                    msg.setStandardButtons(QMessageBox.Ok)
                    result = msg.exec_()
                    self.loadMonHoc()
                    self.KhoiTaoMH()
                    self.fi_SoTC_2.setText("")
                    self.fi_TietLT_2.setText("")
                    self.fi_TenMonHoc_2.setText("")
                    self.fi_TongSoTiet_2.setText("")
                    self.fi_TietTH_2.setText("")
                    self.fi_IDMonHoc_2.setText("")
                except:
                    msg = QMessageBox()
                    msg.setIcon(QMessageBox.NoIcon)
                    msg.setWindowTitle("Thông báo")
                    msg.setText("Lỗi!!!")
                    msg.setStandardButtons(QMessageBox.Ok)
                    result = msg.exec_()



    def LuuMH(self):
        if self.themmh==True:
            if self.fi_SoTC_2.text()=="" or self.fi_TietLT_2.text()=="" or self.fi_TenMonHoc_2.text()=="" or self.fi_TongSoTiet_2.text()==""or self.fi_TietTH_2.text()=="":
                msg = QMessageBox()
                msg.setIcon(QMessageBox.Warning)
                msg.setWindowTitle("Thông báo")
                msg.setText("Vui lòng nhập đầy đủ thông tin")
                msg.setStandardButtons(QMessageBox.Ok)
                msg.exec_()
            else:
                try:
                    cursor.execute("INSERT INTO MONHOC "
                                   "Values(?,?,?,?,?,?)", self.fi_IDMonHoc_2.text(), self.fi_TenMonHoc_2.text(),
                                   self.fi_SoTC_2.text(), self.fi_TongSoTiet_2.text(), self.fi_TietLT_2.text(),self.fi_TietTH_2.text())
                    con.commit()
                    msg = QMessageBox()
                    msg.setIcon(QMessageBox.NoIcon)
                    msg.setWindowTitle("Thông báo")
                    msg.setText("Thêm môn học thành công")
                    msg.setStandardButtons(QMessageBox.Ok)
                    result = msg.exec_()
                    self.loadMonHoc()
                    self.KhoiTaoMH()
                except:
                    msg = QMessageBox()
                    msg.setIcon(QMessageBox.Warning)
                    msg.setWindowTitle("Thông báo")
                    msg.setText("Lỗi")
                    msg.setStandardButtons(QMessageBox.Ok)
                    result = msg.exec_()
        elif self.themmh==False:
            if self.fi_SoTC_2.text()=="" or self.fi_TietLT_2.text()=="" or self.fi_TenMonHoc_2.text()=="" or self.fi_TongSoTiet_2.text()==""or self.fi_TietTH_2.text()=="":
                msg = QMessageBox()
                msg.setIcon(QMessageBox.Warning)
                msg.setWindowTitle("Thông báo")
                msg.setText("Vui lòng nhập đầy đủ thông tin")
                msg.setStandardButtons(QMessageBox.Ok)
                msg.exec_()
            else:
                try:
                    cursor.execute("UPDATE MONHOC "
                                   "SET TENMH=?, SOTC=?, TONGSOTIET=?, SOTIETLITHUYET=?,SOTIETTHUCHANH=? WHERE MONHOC.MAMH=?",  self.fi_TenMonHoc_2.text(),
                                   self.fi_SoTC_2.text(), self.fi_TongSoTiet_2.text(), self.fi_TietLT_2.text(),self.fi_TietTH_2.text(),self.fi_IDMonHoc_2.text())
                    con.commit()
                    msg = QMessageBox()
                    msg.setIcon(QMessageBox.NoIcon)
                    msg.setWindowTitle("Thông báo")
                    msg.setText("Cập nhật học thành công")
                    msg.setStandardButtons(QMessageBox.Ok)
                    result = msg.exec_()
                    self.loadMonHoc()
                    self.KhoiTaoMH()
                except:
                    con.commit()
                    msg = QMessageBox()
                    msg.setIcon(QMessageBox.Warning)
                    msg.setWindowTitle("Thông báo")
                    msg.setText("Lỗi")
                    msg.setStandardButtons(QMessageBox.Ok)
                    result = msg.exec_()
    def SuaMH(self):
        if self.fi_IDMonHoc_2.text()=="":
            msg = QMessageBox()
            msg.setIcon(QMessageBox.NoIcon)
            msg.setWindowTitle("Thông báo")
            msg.setText("Vui lòng chọn  môn học cần cập nhật thông tin!!")
            msg.setStandardButtons(QMessageBox.Ok)
            result = msg.exec_()
            self.loadPageGV()
        else:
            self.themmh = False
            self.fi_SoTC_2.setEnabled(True)
            self.fi_TietLT_2.setEnabled(True)
            self.fi_TenMonHoc_2.setEnabled(True)
            self.fi_TongSoTiet_2.setEnabled(True)
            self.fi_TietTH_2.setEnabled(True)
            self.btn_LuuMH_2.setVisible(True)
            self.btn_HuyLopHoc_2.setVisible(True)
            self.btn_ThemMH_2.setVisible(False)
            self.btn_SuaMH_2.setVisible(False)
            self.btn_XoaLopHoc_2.setVisible(False)
    def HuyMH(self):
        self.KhoiTaoMH()
        self.fi_SoTC_2.setText("")
        self.fi_TietLT_2.setText("")
        self.fi_TenMonHoc_2.setText("")
        self.fi_TongSoTiet_2.setText("")
        self.fi_TietTH_2.setText("")
        self.fi_IDMonHoc_2.setText("")
    def ThemMH(self):
        self.themmh=True
        self.fi_SoTC_2.setEnabled(True)
        self.fi_TietLT_2.setEnabled(True)
        self.fi_TenMonHoc_2.setEnabled(True)
        self.fi_TongSoTiet_2.setEnabled(True)
        self.fi_TietTH_2.setEnabled(True)
        self.btn_LuuMH_2.setVisible(True)
        self.btn_HuyLopHoc_2.setVisible(True)
        self.btn_ThemMH_2.setVisible(False)
        self.btn_SuaMH_2.setVisible(False)
        self.btn_XoaLopHoc_2.setVisible(False)

        self.fi_SoTC_2.setText("")
        self.fi_TietLT_2.setText("")
        self.fi_TenMonHoc_2.setText("")
        self.fi_TongSoTiet_2.setText("")
        self.fi_TietTH_2.setText("")
        sql = " EXEC MONHOC_ID "
        cursor.execute(sql)
        data = cursor.fetchall()
        self.fi_IDMonHoc_2.setText(data[0][0])
    def KhoiTaoMH(self):
        self.btn_DatLichHoc_2.setVisible(True)
        self.fi_IDMonHoc_2.setEnabled(False)
        self.fi_SoTC_2.setEnabled(False)
        self.fi_TietLT_2.setEnabled(False)
        self.fi_TenMonHoc_2.setEnabled(False)
        self.fi_TongSoTiet_2.setEnabled(False)
        self.fi_TietTH_2.setEnabled(False)
        self.btn_LuuMH_2.setVisible(False)
        self.btn_HuyLopHoc_2.setVisible(False)
        self.fi_IDLop_2.setEnabled(False)
        self.fi_GiangVien_2.setEnabled(False)
        self.fi_GiangVien_2.setCurrentIndex(-1)
        self.fi_SiSo_2.setEnabled(False)
        self.fi_NgayBatDau_2.setEnabled(False)
        self.fi_NgayKetThuc_2.setEnabled(False)
        # self.fi_GioBD_22.setEnabled(False)
        # self.fi_GioKT_22.setEnabled(False)
        # self.fi_PhongHoc_2.setEnabled(False)
        self.fi_IDSV_2.setEnabled(False)
        self.fi_HoTenSV_2.setEnabled(False)
        self.fi_LopSV_2.setEnabled(False)
        self.fi_KhoaSV_2.setEnabled(False)
        self.btn_ThemMH_2.setVisible(True)
        self.btn_SuaMH_2.setVisible(True)
        self.btn_XoaLopHoc_2.setVisible(True)
        self.btn_XoaLopHP_2.setVisible(True)
        self.btn_SuaLopHP_2.setVisible(True)
        self.btn_ThemLopHP_2.setVisible(True)
        self.btn_LuuLHP_2.setVisible(False)
        self.btn_HuyLHP_2.setVisible(False)
        self.fi_IDLop_2.setText("")
        self.fi_GiangVien_2.setCurrentIndex(-1)
        self.fi_GiangVien_2.setCurrentIndex(-1)
        self.fi_SiSo_2.setText("")
        # self.fi_PhongHoc_2.setCurrentIndex(-1)
        self.fi_NgayBatDau_2.setDate(QtCore.QDate(2000, 1, 1))
        self.fi_NgayKetThuc_2.setDate(QtCore.QDate(2000, 1, 1))
        # self.fi_GioBD_22.setTime(QtCore.QTime(12, 0))
        # self.fi_GioKT_22.setTime(QtCore.QTime(12, 0))


    def GetSV_MonHoc(self):
        row = self.tbl_DSSV_2.currentIndex().row()
        ms = self.tbl_DSSV_2.item(row, 0).text()
        for row in cursor.execute(f"select * from SINHVIEN,KHOA,LOP,CHUYENNGANH WHERE SINHVIEN.MASV='{ms}' "
                                  f"AND LOP.MAKHOA=KHOA.MAKHOA AND SINHVIEN.MALOP=LOP.MALOP AND SINHVIEN.MACN=CHUYENNGANH.MACN "):
            self.fi_IDSV_2.setText(row[0])
            self.fi_HoTenSV_2.setText(row[1])
            self.fi_LopSV_2.setText(row[10])
            self.fi_KhoaSV_2.setText(row[17])
    def GetLopHocPhan(self):
        row = self.tbl_LopHocPhan_2.currentIndex().row()
        ms = self.tbl_LopHocPhan_2.item(row, 0).text()
        for row in cursor.execute(f"select * from LOPMONHOC,GIANGVIEN WHERE LOPMONHOC.MAGV=GIANGVIEN.MAGV AND MALOPMH='{ms}'"):
            self.fi_IDLop_2.setText(row[0])
            self.fi_GiangVien_2.setCurrentText(row[8]+"-"+row[7])
            self.fi_SiSo_2.setText(str(row[5]))
            self.fi_NgayBatDau_2.setDate(
                QtCore.QDate(int(row[2].split('-')[0]), int(row[2].split('-')[1]), int(row[2].split('-')[2])))
            self.fi_NgayKetThuc_2.setDate(
                QtCore.QDate(int(row[3].split('-')[0]), int(row[3].split('-')[1]), int(row[3].split('-')[2])))
            # self.fi_PhongHoc_2.setCurrentText(row[8])
            # self.fi_GioBD_22.setTime(QtCore.QTime(int(row[4].split(":")[0]),int(row[4].split(":")[1])))
            # self.fi_GioKT_22.setTime(QtCore.QTime(int(row[5].split(":")[0]), int(row[5].split(":")[1])))

        #load sv trong lớp học phần
        row = 0
        self.lstSVLHP = []
        for row1 in cursor.execute(f"select * from CHITIETLHP,SINHVIEN WHERE CHITIETLHP.MASV=SINHVIEN.MASV AND CHITIETLHP.MALOPMH='{ms}'"):
            LHP = {}
            LHP["ID"] = row1[2]
            LHP["name"] = row1[3]
            self.lstSVLHP.append(LHP)
        self.tbl_DSSV_2.setColumnWidth(0, 110)
        self.tbl_DSSV_2.setColumnWidth(1, 200)
        self.tbl_DSSV_2.setRowCount(len(self.lstSVLHP))
        for mh in self.lstSVLHP:
            self.tbl_DSSV_2.setItem(row, 0, QtWidgets.QTableWidgetItem(mh["ID"]))
            self.tbl_DSSV_2.setItem(row, 1, QtWidgets.QTableWidgetItem(mh["name"]))
            row += 1
    def GetMonHoc(self):
        row = self.tbl_MonHoc_2.currentIndex().row()
        ms = self.tbl_MonHoc_2.item(row, 0).text()
        cursor.execute(f"SELECT MAHK FROM HOCKI WHERE TENHK='{self.cbo_hocki.currentText()}'")
        data = cursor.fetchall()
        for row in cursor.execute(f"select * from MONHOC Where MAMH='{ms}'"):
            self.fi_IDMonHoc_2.setText(row[0])
            self.fi_TenMonHoc_2.setText(row[1])
            self.fi_SoTC_2.setText(str(row[2]))
            self.fi_TongSoTiet_2.setText(str(row[3]))
            self.fi_TietLT_2.setText(str(row[4]))
            self.fi_TietTH_2.setText(str(row[5]))


        #load các lớp học phần
        row = 0
        self.lstLHP = []
        for row1 in cursor.execute(f"select * from LOPMONHOC,GIANGVIEN,HOCKI WHERE LOPMONHOC.MAGV=GIANGVIEN.MAGV "
                                   f"AND LOPMONHOC.MAMH='{ms}' AND LOPMONHOC.MAHK=HOCKI.MAHK AND HOCKI.MAHK='{data[0][0]}'"):
            LHP = {}
            LHP["ID"] = row1[0]
            LHP["name"] = row1[8]
            self.lstLHP.append(LHP)
        self.tbl_LopHocPhan_2.setColumnWidth(0, 90)
        self.tbl_LopHocPhan_2.setColumnWidth(1, 169)
        self.tbl_LopHocPhan_2.setRowCount(len(self.lstLHP))
        for mh in self.lstLHP:
            self.tbl_LopHocPhan_2.setItem(row, 0, QtWidgets.QTableWidgetItem(mh["ID"]))
            self.tbl_LopHocPhan_2.setItem(row, 1, QtWidgets.QTableWidgetItem(mh["name"]))
            row += 1

    def ChangeHK(self):
        cursor.execute(f"SELECT MAHK FROM HOCKI WHERE TENHK='{self.cbo_hocki.currentText()}'")
        data = cursor.fetchall()
        if(data==[]) :
            cursor.execute(f"SELECT COUNT(*) FROM HOCKI")
            data = cursor.fetchall()

        cursor.execute(f"SELECT COUNT(*) FROM HOCKI")
        data1 = cursor.fetchall()
        str1=""

        if(data[0][0]!=data1[0][0]):
             str1= f"select distinct MONHOC.MAMH,TENMH, SOTC from MONHOC,LOPMONHOC WHERE MONHOC.MAMH=LOPMONHOC.MAMH AND LOPMONHOC.MAHK={data[0][0]}"
             self.btn_ThemLopHP_2.setEnabled(False)
             self.btn_SuaLopHP_2.setEnabled(False)
             self.btn_XoaLopHP_2.setEnabled(False)
             self.btn_ThemSV_2.setEnabled(False)
             self.btn_XoaSV_2.setEnabled(False)
        else:
            str1=(f"select*from MONHOC")
            self.btn_ThemLopHP_2.setEnabled(True)
            self.btn_SuaLopHP_2.setEnabled(True)
            self.btn_XoaLopHP_2.setEnabled(True)
            self.btn_ThemSV_2.setEnabled(True)
            self.btn_XoaSV_2.setEnabled(True)
        row = 0
        self.lstMH = []
        for row1 in cursor.execute(str1):
            MH = {}
            MH["ID"] = row1[0]
            MH["name"] = row1[1]
            MH["soTC"] = row1[2]
            self.lstMH.append(MH)
        self.tbl_MonHoc_2.setColumnWidth(0, 150)
        self.tbl_MonHoc_2.setColumnWidth(1, 280)
        self.tbl_MonHoc_2.setColumnWidth(2, 225)
        self.tbl_MonHoc_2.setRowCount(len(self.lstMH))
        for mh in self.lstMH:
            self.tbl_MonHoc_2.setItem(row, 0, QtWidgets.QTableWidgetItem(mh["ID"]))
            self.tbl_MonHoc_2.setItem(row, 1, QtWidgets.QTableWidgetItem(mh["name"]))
            self.tbl_MonHoc_2.setItem(row, 2, QtWidgets.QTableWidgetItem(str(mh["soTC"])))
            row += 1

    def KhoiTaoCboHK(self):
        self.cbo_hocki.clear()
        for row3 in cursor.execute("select * from HOCKI ORDER BY  MAHK DESC"):
            self.cbo_hocki.addItem(row3[1])
    def loadMonHoc(self):
        #load combobox giảng viên
        self.fi_GiangVien_2.clear()
        for row1 in cursor.execute("select * from GIANGVIEN"):
            self.fi_GiangVien_2.addItem(row1[1]+'-'+row1[0])
        # self.fi_PhongHoc_2.clear()
        # for row1 in cursor.execute("select * from PHONGHOC"):
        #     self.fi_PhongHoc_2.addItem(row1[0])
        # Load combobox học kì
        # self.cbo_hocki.clear()
        # for row3 in cursor.execute("select * from HOCKI ORDER BY  MAHK DESC"):
        #     self.cbo_hocki.addItem(row3[1])

        cursor.execute(f"SELECT MAHK FROM HOCKI WHERE TENHK='{self.cbo_hocki.currentText()}'")
        data = cursor.fetchall()

        #load môn học
        row = 0
        self.lstMH = []
        for row1 in cursor.execute(f"select*FROM MONHOC"):
            MH = {}
            MH["ID"] = row1[0]
            MH["name"] = row1[1]
            MH["soTC"] = row1[2]
            self.lstMH.append(MH)
        self.HK=data[0][0]
        self.tbl_MonHoc_2.setColumnWidth(0, 150)
        self.tbl_MonHoc_2.setColumnWidth(1, 280)
        self.tbl_MonHoc_2.setColumnWidth(2, 225)
        self.tbl_MonHoc_2.setRowCount(len(self.lstMH))
        for mh in self.lstMH:
            self.tbl_MonHoc_2.setItem(row, 0, QtWidgets.QTableWidgetItem(mh["ID"]))
            self.tbl_MonHoc_2.setItem(row, 1, QtWidgets.QTableWidgetItem(mh["name"]))
            self.tbl_MonHoc_2.setItem(row, 2, QtWidgets.QTableWidgetItem(str(mh["soTC"])))
            row += 1
        self.cbo_TimMH_2.clear()
        self.cbo_TimMH_2.addItem("ID")
        self.cbo_TimMH_2.addItem("Tên Môn Học")

    #page sinh viên ##############################################################################################


    def Training(self):
        folder = ('Data/processed/')
        database = {}
        cnt=0
        self.progressBar.setVisible(True)
        self.btn_TrainingData.setEnabled(False)
        for filename in os.listdir(folder):
            path = folder + filename

            if cnt < 88:
                self.progressBar.setValue(cnt)
            else:
                self.progressBar.setValue(88)
            cnt+=3
            QApplication.processEvents()
            for filename2 in os.listdir(path):
                gbr1 = cv2.imread(path + "/" + filename2)
                face = cv2.resize(gbr1, (160, 160))
                face = face.astype('float32')
                mean, std = face.mean(), face.std()
                face = (face - mean) / std
                face = expand_dims(face, axis=0)
                signature = MyFaceNet.predict(face)
                database[os.path.splitext(filename)[0]] = signature

        myfile = open("data.pkl", "wb")
        pickle.dump(database, myfile)
        myfile.close()
        self.progressBar.setValue(100)
        msg = QMessageBox()
        msg.setIcon(QMessageBox.NoIcon)
        msg.setWindowTitle("Thông báo")
        msg.setText("Training data thành công")
        msg.setStandardButtons(QMessageBox.Ok)
        result = msg.exec_()

        # for filename in os.listdir(folder):
        #    shutil.rmtree(folder+filename)
        self.progressBar.setVisible(False)
        self.btn_TrainingData.setEnabled(True)
    def LayAnh(self):
        if self.kTLuuSV() == False:
            if self.fi_IDSV.text() == "":
                msg = QMessageBox()
                msg.setIcon(QMessageBox.Warning)
                msg.setWindowTitle("Thông báo")
                msg.setText("Vui lòng chọn sinh viên muốn thêm ảnh")
                msg.setStandardButtons(QMessageBox.Ok )
                result = msg.exec_()
            else:
                msg = QMessageBox()
                msg.setIcon(QMessageBox.Warning)
                msg.setWindowTitle("Thông báo")
                msg.setText("Bạn có muốn lưu sinh viên " + self.fi_IDSV.text() + " không?")
                msg.setStandardButtons(QMessageBox.Ok | QMessageBox.No)
                result = msg.exec_()
                if result == QMessageBox.Ok:
                    self.them = True
                    self.LuuSV()
                    # msg = QMessageBox()
                    # msg.setIcon(QMessageBox.Warning)
                    # msg.setWindowTitle("Thông báo")
                    # msg.setText("Lưu thành công")
                    # msg.setStandardButtons(QMessageBox.Ok | QMessageBox.No)
                    # result = msg.exec_()
                    self.anhSV.fi_ID.setText(self.fi_IDSV.text())
                    self.anhSV.fi_HoTen.setText(self.fi_HoTen.text())
                    self.anhSV.fi_ChuyenNganh.setText(self.fi_ChuyenNganh.currentText())
                    self.anhSV.fi_Lop.setText(self.fi_Lop.currentText())
                    self.anhSV.show()
                    self.hide()
        else:
            self.anhSV.fi_ID.setText(self.fi_IDSV.text())
            self.anhSV.fi_HoTen.setText(self.fi_HoTen.text())
            self.anhSV.fi_ChuyenNganh.setText(self.fi_ChuyenNganh.currentText())
            self.anhSV.fi_Lop.setText(self.fi_Lop.currentText())
            self.anhSV.show()
            self.hide()
    def kTLuuSV(self):
        try:
            cursor.execute(f"select* from SINHVIEN Where MASV='{self.fi_IDSV.text()}'")
            data = cursor.fetchall()
            if data[0][0] != None:
                return True
        except:
            pass
        return False

    def XoaLop(self):
        if self.fi_TenLopHoc.text() == "":
            msg = QMessageBox()
            msg.setIcon(QMessageBox.Warning)
            msg.setWindowTitle("Thông báo")
            msg.setText("Vui lòng chọn Lớp muốn xóa")
            msg.setStandardButtons(QMessageBox.Ok)
            result = msg.exec_()
        else:
            if self.kTLopHocTonTaiSV() == True:
                msg = QMessageBox()
                msg.setIcon(QMessageBox.NoIcon)
                msg.setWindowTitle("Thông báo")
                msg.setText("Không thể xóa!!!")
                msg.setStandardButtons(QMessageBox.Ok)
                result = msg.exec_()
            else:
                try:
                    cursor.execute("DELETE LOP WHERE MALOP=?", self.fi_TenLopHoc.text())
                    con.commit()
                    msg = QMessageBox()
                    msg.setIcon(QMessageBox.NoIcon)
                    msg.setWindowTitle("Thông báo")
                    msg.setText("Xóa thành công")
                    msg.setStandardButtons(QMessageBox.Ok)
                    result = msg.exec_()
                    self.fi_TenLopHoc.setText("")
                    self.loadData()
                    self.KhoiTao()
                    self.KhoiTaoCombobox()
                except:
                    msg = QMessageBox()
                    msg.setIcon(QMessageBox.NoIcon)
                    msg.setWindowTitle("Thông báo")
                    msg.setText("Lỗi!!!")
                    msg.setStandardButtons(QMessageBox.Ok)
                    result = msg.exec_()

    def kTLopHocTonTaiSV(self):
        try:
            cursor.execute(f"select* from SINHVIEN Where MALOP='{self.fi_TenLopHoc.text()}'")
            data = cursor.fetchall()
            if data[0][0] != None:
                return True
        except:
            pass
        return False

    def kTLopHoc(self, tenlop):
        try:
            cursor.execute(f"select* from LOP Where MALOP='{self.fi_TenLopHoc.text()}'")
            data = cursor.fetchall()
            if data[0][0] != None:
                return True
        except:
            pass
        return False

    def LuuLop(self):
        if self.themlop == True:
            if self.fi_TenLopHoc.text() == "" or self.fi_KhoaLop.currentIndex == -1:
                msg = QMessageBox()
                msg.setIcon(QMessageBox.Warning)
                msg.setWindowTitle("Thông báo")
                msg.setText("Vui lòng nhập đầy đủ thông tin")
                msg.setStandardButtons(QMessageBox.Ok)
                result = msg.exec_()
            else:
                if self.kTLopHoc(self.fi_TenLopHoc.text()) == True:
                    msg = QMessageBox()
                    msg.setIcon(QMessageBox.Warning)
                    msg.setWindowTitle("Thông báo")
                    msg.setText("Lớp học " + self.fi_TenLopHoc.text() + " đã tồn tại. Vui lòng nhập lớp học mới!!")
                    msg.setStandardButtons(QMessageBox.Ok )
                    result = msg.exec_()
                else:
                    try:
                        cursor.execute("insert into LOP VALUES(?,?)", self.fi_TenLopHoc.text(),
                                       self.fi_KhoaLop.currentText().split('-')[1])
                        con.commit()
                        msg = QMessageBox()
                        msg.setIcon(QMessageBox.NoIcon)
                        msg.setWindowTitle("Thông báo")
                        msg.setText("Thêm thành công")
                        msg.setStandardButtons(QMessageBox.Ok)
                        result = msg.exec_()
                        self.loadData()
                        self.btn_ThemLop.setVisible(True)
                        self.btn_XoaLop.setVisible(True)
                        self.btn_SuaLop.setVisible(True)
                        self.btn_LuuLop.setVisible(False)
                        self.btn_HuyLop.setVisible(False)
                        self.fi_KhoaLop.setEnabled(False)
                        self.fi_TenLopHoc.setEnabled(False)
                    except:
                        msg = QMessageBox()
                        msg.setIcon(QMessageBox.Warning)
                        msg.setWindowTitle("Thông báo")
                        msg.setText("Lỗi")
                        msg.setStandardButtons(QMessageBox.Ok)
                        result = msg.exec_()


        elif self.themlop == False:
            if self.fi_TenLopHoc.text() == "" or self.fi_KhoaLop.currentIndex == -1:
                msg = QMessageBox()
                msg.setIcon(QMessageBox.Warning)
                msg.setWindowTitle("Thông báo")
                msg.setText("Vui lòng nhập đầy đủ thông tin")
                msg.setStandardButtons(QMessageBox.Ok)
                result = msg.exec_()
            else:
                try:
                    cursor.execute("UPDATE LOP SET MAKHOA=? WHERE MALOP=?", self.fi_KhoaLop.currentText().split('-')[1],
                                   self.fi_TenLopHoc.text())
                    con.commit()
                    msg = QMessageBox()
                    msg.setIcon(QMessageBox.NoIcon)
                    msg.setWindowTitle("Thông báo")
                    msg.setText("Cập nhật thành công")
                    msg.setStandardButtons(QMessageBox.Ok)
                    result = msg.exec_()
                    self.loadData()
                    self.btn_ThemLop.setVisible(True)
                    self.btn_XoaLop.setVisible(True)
                    self.btn_SuaLop.setVisible(True)
                    self.btn_LuuLop.setVisible(False)
                    self.btn_HuyLop.setVisible(False)
                    self.fi_KhoaLop.setEnabled(False)
                    self.fi_TenLopHoc.setEnabled(False)
                except:
                    msg = QMessageBox()
                    msg.setIcon(QMessageBox.Warning)
                    msg.setWindowTitle("Thông báo")
                    msg.setText("Lỗi")
                    msg.setStandardButtons(QMessageBox.Ok)
                    result = msg.exec_()

    def HuyLop(self):
        self.btn_ThemLop.setVisible(True)
        self.btn_XoaLop.setVisible(True)
        self.btn_SuaLop.setVisible(True)
        self.btn_LuuLop.setVisible(False)
        self.btn_HuyLop.setVisible(False)
        self.fi_KhoaLop.setEnabled(False)
        self.fi_KhoaLop.setCurrentIndex(-1)
        self.fi_TenLopHoc.setEnabled(False)
        self.fi_TenLopHoc.setText("")

    def SuaLop(self):
        if self.fi_TenLopHoc.text()=="":
            msg = QMessageBox()
            msg.setIcon(QMessageBox.NoIcon)
            msg.setWindowTitle("Thông báo")
            msg.setText("Vui lòng chọn lớp học cần cập nhật thông tin!!")
            msg.setStandardButtons(QMessageBox.Ok)
            result = msg.exec_()
            self.loadPageGV()
        else:
            self.themlop = False
            self.fi_KhoaLop.setEnabled(True)
            self.btn_ThemLop.setVisible(False)
            self.btn_XoaLop.setVisible(False)
            self.btn_SuaLop.setVisible(False)
            self.btn_LuuLop.setVisible(True)
            self.btn_HuyLop.setVisible(True)

    def ThemLop(self):
        self.themlop = True
        self.fi_TenLopHoc.setEnabled(True)
        self.fi_KhoaLop.setEnabled(True)
        self.btn_ThemLop.setVisible(False)
        self.btn_XoaLop.setVisible(False)
        self.btn_SuaLop.setVisible(False)
        self.btn_LuuLop.setVisible(True)
        self.btn_HuyLop.setVisible(True)
        self.fi_TenLopHoc.setText("")
        self.fi_KhoaLop.setCurrentIndex(-1)

    def XoaSV(self):
        if self.fi_IDSV.text() == "":
            msg = QMessageBox()
            msg.setIcon(QMessageBox.Warning)
            msg.setWindowTitle("Thông báo")
            msg.setText("Vui lòng chọn Sinh viên muốn xóa")
            msg.setStandardButtons(QMessageBox.Ok)
            result = msg.exec_()
        else:
            try:
                cursor.execute("DELETE SINHVIEN WHERE MASV=?", self.fi_IDSV.text())
                con.commit()
                msg = QMessageBox()
                msg.setIcon(QMessageBox.NoIcon)
                msg.setWindowTitle("Thông báo")
                msg.setText("Xóa sinh viên thành công")
                msg.setStandardButtons(QMessageBox.Ok )
                result = msg.exec_()
                self.fi_IDSV.setText("")
                self.loadData()
                self.KhoiTao()
                self.LamMoiSV()
                self.KhoiTaoCombobox()
            except:
                con.commit()
                msg = QMessageBox()
                msg.setIcon(QMessageBox.NoIcon)
                msg.setWindowTitle("Thông báo")
                msg.setText("Lỗi!!!")
                msg.setStandardButtons(QMessageBox.Ok)
                result = msg.exec_()

    def KhoiTaoCombobox(self):
        self.fi_Khoa.setCurrentIndex(-1)
        self.fi_ChuyenNganh.setCurrentIndex(-1)
        self.fi_NienKhoa.setCurrentIndex(-1)
        self.fi_Lop.setCurrentIndex(-1)
        self.fi_GioiTinh.setCurrentIndex(-1)
        self.fi_KhoaLop.setCurrentIndex(-1)

    def SuaSV(self):
        if self.fi_IDSV.text()=="":
            msg = QMessageBox()
            msg.setIcon(QMessageBox.NoIcon)
            msg.setWindowTitle("Thông báo")
            msg.setText("Vui lòng chọn sinh viên cần cập nhật thông tin!!")
            msg.setStandardButtons(QMessageBox.Ok)
            result = msg.exec_()
        else:
            self.them = False
            self.fi_Khoa.setEnabled(True)
            self.fi_ChuyenNganh.setEnabled(True)
            self.fi_NienKhoa.setEnabled(True)
            self.fi_Lop.setEnabled(True)
            self.fi_GioiTinh.setEnabled(True)
            self.fi_DCThuongTru.setEnabled(True)
            self.fi_DCTamTru.setEnabled(True)
            self.fi_HoTen.setEnabled(True)
            self.fi_CMND.setEnabled(True)
            self.fi_NgaySinh.setEnabled(True)
            self.fi_SDT.setEnabled(True)
            self.fi_DanToc.setEnabled(True)
            self.fi_Email_2.setEnabled(True)
            self.fi_TenLopHoc.setEnabled(True)
            self.fi_KhoaLop.setEnabled(True)
            self.btnLuuSV.setVisible(True)
            self.btnHuySV.setVisible(True)
            self.btn_LamMoiSV.setVisible(True)
            self.btn_ThemSV.setVisible(False)
            self.btn_SuaSV.setVisible(False)
            self.btn_XoaSV.setVisible(False)

    def kiemTraNhapSV(self):
        if self.fi_Khoa.currentIndex() == -1 or self.fi_ChuyenNganh.currentIndex() == -1 or self.fi_NienKhoa.currentIndex() == -1 or self.fi_Lop.currentIndex() == -1 or self.fi_GioiTinh.currentIndex() == -1 or self.fi_IDSV.text() == "" or self.fi_DCThuongTru.text() == "" or self.fi_DCTamTru.text() == "" or self.fi_HoTen.text() == "" or self.fi_CMND.text() == "" or self.fi_SDT.text() == "" or self.fi_DanToc.text() == "" or self.fi_Email_2.text() == "":
            return False
        return True

    def LuuSV(self):
        if self.them == True:
            if self.kiemTraNhapSV() == False:
                msg = QMessageBox()
                msg.setIcon(QMessageBox.Warning)
                msg.setWindowTitle("Thông báo")
                msg.setText("Vui lòng nhập đầy đủ thông tin")
                msg.setStandardButtons(QMessageBox.Ok)
                result = msg.exec_()
            else:
                try:
                    mk=self.fi_NgaySinh.text().split("/")[0]+self.fi_NgaySinh.text().split("/")[1]+self.fi_NgaySinh.text().split("/")[2]
                    cursor.execute("set dateformat dmy "
                                   "INSERT INTO SINHVIEN(MASV,TENSV,SDT, NGAYSINH ,CMND,DANTOC,GIOITINH, EMAIL,DIACHITT ,DCTAMTRU ,MALOP ,MACN, MANK,MATKHAU,MAQUYEN ) "
                                   "Values(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)", self.fi_IDSV.text(), self.fi_HoTen.text(),
                                   self.fi_SDT.text(),
                                   self.fi_NgaySinh.text(), self.fi_CMND.text(), self.fi_DanToc.text(),
                                   self.fi_GioiTinh.currentText(),
                                   self.fi_Email_2.text(), self.fi_DCThuongTru.text(), self.fi_DCTamTru.text(),
                                   self.fi_Lop.currentText(), self.fi_ChuyenNganh.currentText().split('-')[1],
                                   self.fi_NienKhoa.currentText().split('-')[2],mk,'SV')
                    con.commit()
                    msg = QMessageBox()
                    msg.setIcon(QMessageBox.NoIcon)
                    msg.setWindowTitle("Thông báo")
                    msg.setText("Thêm sinh viên thành công")
                    msg.setStandardButtons(QMessageBox.Ok)
                    result = msg.exec_()
                    self.loadData()
                    self.KhoiTao()
                except:
                    msg = QMessageBox()
                    msg.setIcon(QMessageBox.Warning)
                    msg.setWindowTitle("Thông báo")
                    msg.setText("Lỗi")
                    msg.setStandardButtons(QMessageBox.Ok)
                    result = msg.exec_()

        elif self.them == False:
            if self.kiemTraNhapSV() == False:
                msg = QMessageBox()
                msg.setIcon(QMessageBox.Warning)
                msg.setWindowTitle("Thông báo")
                msg.setText("Vui lòng nhập đầy đủ thông tin")
                msg.setStandardButtons(QMessageBox.Ok )
                result = msg.exec_()
            else:
                if self.fi_CMND.text() == "":
                    print("t")
                try:
                    cursor.execute("set dateformat dmy "
                                   "Update SINHVIEN set TENSV=?,SDT=?, NGAYSINH=? ,CMND=?,DANTOC=?,GIOITINH=?, EMAIL=?,DIACHITT=?,DCTAMTRU=? ,MALOP=? ,MACN=?, MANK=? where MASV=? "
                                   , self.fi_HoTen.text(), self.fi_SDT.text(),
                                   self.fi_NgaySinh.text(), self.fi_CMND.text(), self.fi_DanToc.text(),
                                   self.fi_GioiTinh.currentText(),
                                   self.fi_Email_2.text(), self.fi_DCThuongTru.text(), self.fi_DCTamTru.text(),
                                   self.fi_Lop.currentText(), self.fi_ChuyenNganh.currentText().split('-')[1],
                                   self.fi_NienKhoa.currentText().split('-')[2], self.fi_IDSV.text(), )
                    con.commit()
                    msg = QMessageBox()
                    msg.setIcon(QMessageBox.NoIcon)
                    msg.setWindowTitle("Thông báo")
                    msg.setText("Cập nhật sinh viên thành công")
                    msg.setStandardButtons(QMessageBox.Ok)
                    result = msg.exec_()
                    self.loadData()
                    self.KhoiTao()
                except:
                    msg = QMessageBox()
                    msg.setIcon(QMessageBox.Warning)
                    msg.setWindowTitle("Thông báo")
                    msg.setText("Lỗi")
                    msg.setStandardButtons(QMessageBox.Ok)
                    result = msg.exec_()

    def HuySV(self):
        self.KhoiTao()
        self.LamMoiSV()
        self.fi_IDSV.setText("")

    def LamMoiSV(self):
        self.fi_Khoa.setCurrentIndex(-1)
        self.fi_ChuyenNganh.setCurrentIndex(-1)
        self.fi_NienKhoa.setCurrentIndex(-1)

        self.fi_Lop.setCurrentIndex(-1)
        self.fi_GioiTinh.setCurrentIndex(-1)
        self.fi_DCThuongTru.setText("")
        self.fi_DCTamTru.setText("")
        self.fi_HoTen.setText("")
        self.fi_CMND.setText("")
        self.fi_NgaySinh.setDate(QtCore.QDate(2000, 1, 1))
        self.fi_SDT.setText("")
        self.fi_DanToc.setText("")
        self.fi_Email_2.setText("")
        image = np.array(Image.open(f"Avatar/Who1.png"))
        image = cv2.resize(image, (212, 137))
        image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        img = QtGui.QImage(image, image.shape[1], image.shape[0], image.strides[0],
                           QtGui.QImage.Format_RGB888)  # tổng số pixel quét của ảnh
        self.lbl_Avatar.setPixmap(QtGui.QPixmap.fromImage(img))

    def KhoiTao(self):
        self.fi_Khoa.setEnabled(False)
        self.fi_ChuyenNganh.setEnabled(False)
        self.fi_NienKhoa.setEnabled(False)
        self.fi_IDSV.setEnabled(False)
        self.fi_Lop.setEnabled(False)
        self.fi_GioiTinh.setEnabled(False)
        self.fi_DCThuongTru.setEnabled(False)
        self.fi_DCTamTru.setEnabled(False)
        self.fi_HoTen.setEnabled(False)
        self.fi_CMND.setEnabled(False)
        self.fi_NgaySinh.setEnabled(False)
        self.fi_SDT.setEnabled(False)
        self.fi_DanToc.setEnabled(False)
        self.fi_Email_2.setEnabled(False)
        self.fi_TenLopHoc.setEnabled(False)
        self.fi_KhoaLop.setEnabled(False)
        self.btnLuuSV.setVisible(False)
        self.btnHuySV.setVisible(False)
        self.btn_LuuLop.setVisible(False)
        self.btn_HuyLop.setVisible(False)
        self.btn_LamMoiSV.setVisible(False)
        self.btn_ThemSV.setVisible(True)
        self.btn_SuaSV.setVisible(True)
        self.btn_XoaSV.setVisible(True)
        self.rbo_CoAnh.setEnabled(False)
        self.rbo_KhongAnh.setEnabled(False)
        image = np.array(Image.open(f"Avatar/Who1.png"))
        image = cv2.resize(image, (212, 137))
        image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        img = QtGui.QImage(image, image.shape[1], image.shape[0], image.strides[0],
                           QtGui.QImage.Format_RGB888)  # tổng số pixel quét của ảnh
        self.lbl_Avatar.setPixmap(QtGui.QPixmap.fromImage(img))

    def themSV(self):
        self.them = True
        self.fi_Khoa.setEnabled(True)
        self.fi_ChuyenNganh.setEnabled(True)
        self.fi_NienKhoa.setEnabled(True)
        self.fi_Lop.setEnabled(True)
        self.fi_GioiTinh.setEnabled(True)
        self.fi_DCThuongTru.setEnabled(True)
        self.fi_DCTamTru.setEnabled(True)
        self.fi_HoTen.setEnabled(True)
        self.fi_CMND.setEnabled(True)
        self.fi_NgaySinh.setEnabled(True)
        self.fi_SDT.setEnabled(True)
        self.fi_DanToc.setEnabled(True)
        self.fi_Email_2.setEnabled(True)
        self.fi_TenLopHoc.setEnabled(True)
        self.fi_KhoaLop.setEnabled(True)
        self.btnLuuSV.setVisible(True)
        self.btnHuySV.setVisible(True)
        self.btn_LamMoiSV.setVisible(True)
        self.btn_ThemSV.setVisible(False)
        self.btn_SuaSV.setVisible(False)
        self.btn_XoaSV.setVisible(False)
        self.LamMoiSV()
        sql = " EXEC SINHVIEN_ID "
        cursor.execute(sql)
        data = cursor.fetchall()
        self.fi_IDSV.setText(data[0][0])

    def GetAllLop(self):
        i = 0
        self.tbl_Lop.setColumnWidth(0, 95)
        self.tbl_Lop.setColumnWidth(1, 63)
        self.tbl_Lop.setRowCount(len(self.lstLop))
        for lop in self.lstLop:
            self.tbl_Lop.setItem(i, 0, QtWidgets.QTableWidgetItem(lop["ID"]))
            self.tbl_Lop.setItem(i, 1, QtWidgets.QTableWidgetItem(lop["Khoa"]))
            i += 1

    def TimLop(self):
        lstTimLop = []
        i = 0
        if self.txt_TimLop.text() == "":
            self.GetAllLop()
        elif self.cbo_TimLop.currentText() == "Lớp":
            for row in cursor.execute(f"select * from LOP,KHOA Where LOP.MAKHOA=KHOA.MAKHOA "
                                      f"and LOP.MALOP='{self.txt_TimLop.text()}' "):
                lop = {}
                lop["ID"] = row[0]
                lop["Khoa"] = row[2]
                lstTimLop.append(lop)
            self.tbl_Lop.setColumnWidth(0, 95)
            self.tbl_Lop.setColumnWidth(1, 63)
            self.tbl_Lop.setRowCount(len(lstTimLop))
            for lop in lstTimLop:
                self.tbl_Lop.setItem(i, 0, QtWidgets.QTableWidgetItem(lop["ID"]))
                self.tbl_Lop.setItem(i, 1, QtWidgets.QTableWidgetItem(lop["Khoa"]))
                i += 1

        elif self.cbo_TimLop.currentText() == "Khoa":
            for row in cursor.execute(f"select * from LOP,KHOA Where LOP.MAKHOA=KHOA.MAKHOA "
                                      f"and KHOA.MAKHOA='{self.txt_TimLop.text()}'"):
                lop = {}
                lop["ID"] = row[0]
                lop["Khoa"] = row[2]
                lstTimLop.append(lop)
            self.tbl_Lop.setColumnWidth(0, 95)
            self.tbl_Lop.setColumnWidth(1, 63)
            self.tbl_Lop.setRowCount(len(lstTimLop))
            for lop in lstTimLop:
                self.tbl_Lop.setItem(i, 0, QtWidgets.QTableWidgetItem(lop["ID"]))
                self.tbl_Lop.setItem(i, 1, QtWidgets.QTableWidgetItem(lop["Khoa"]))
                i += 1
        else:
            self.GetAllLop()

    def TimSV(self):

        lstTimSV = []
        row = 0
        if self.txt_TimSV.text() == "":
            self.GetAllSV()
        elif self.cbo_TimSV.currentText() == "ID Sinh viên":
            for row1 in cursor.execute(f"select * from SINHVIEN,LOP WHERE SINHVIEN.MALOP=LOP.MALOP"
                                       f" AND SINHVIEN.MASV='{self.txt_TimSV.text()}'"):
                SV = {}
                SV["ID"] = row1[0]
                SV["name"] = row1[1]
                SV["class"] = row1[10]
                lstTimSV.append(SV)

            self.tbl_SinhVien.setColumnWidth(0, 100)
            self.tbl_SinhVien.setColumnWidth(1, 240)
            self.tbl_SinhVien.setColumnWidth(2, 220)
            self.tbl_SinhVien.setRowCount(len(lstTimSV))
            for sv in lstTimSV:
                self.tbl_SinhVien.setItem(row, 0, QtWidgets.QTableWidgetItem(sv["ID"]))
                self.tbl_SinhVien.setItem(row, 1, QtWidgets.QTableWidgetItem(sv["name"]))
                self.tbl_SinhVien.setItem(row, 2, QtWidgets.QTableWidgetItem(sv["class"]))
                row += 1


        elif self.cbo_TimSV.currentText() == "Họ tên":
            for row1 in cursor.execute(f"select * from SINHVIEN,LOP WHERE SINHVIEN.MALOP=LOP.MALOP"
                                       f" AND SINHVIEN.TENSV LIKE N'%{self.txt_TimSV.text()}%'"):
                SV = {}
                SV["ID"] = row1[0]
                SV["name"] = row1[1]
                SV["class"] = row1[10]
                lstTimSV.append(SV)

            self.tbl_SinhVien.setColumnWidth(0, 100)
            self.tbl_SinhVien.setColumnWidth(1, 240)
            self.tbl_SinhVien.setColumnWidth(2, 220)
            self.tbl_SinhVien.setRowCount(len(lstTimSV))
            for sv in lstTimSV:
                self.tbl_SinhVien.setItem(row, 0, QtWidgets.QTableWidgetItem(sv["ID"]))
                self.tbl_SinhVien.setItem(row, 1, QtWidgets.QTableWidgetItem(sv["name"]))
                self.tbl_SinhVien.setItem(row, 2, QtWidgets.QTableWidgetItem(sv["class"]))
                row += 1


        elif self.cbo_TimSV.currentText() == "Lớp":
            for row1 in cursor.execute(f"select * from SINHVIEN,LOP WHERE SINHVIEN.MALOP=LOP.MALOP"
                                       f" AND LOP.MALOP='{self.txt_TimSV.text()}'"):
                SV = {}
                SV["ID"] = row1[0]
                SV["name"] = row1[1]
                SV["class"] = row1[10]
                lstTimSV.append(SV)

            self.tbl_SinhVien.setColumnWidth(0, 100)
            self.tbl_SinhVien.setColumnWidth(1, 240)
            self.tbl_SinhVien.setColumnWidth(2, 220)
            self.tbl_SinhVien.setRowCount(len(lstTimSV))
            for sv in lstTimSV:
                self.tbl_SinhVien.setItem(row, 0, QtWidgets.QTableWidgetItem(sv["ID"]))
                self.tbl_SinhVien.setItem(row, 1, QtWidgets.QTableWidgetItem(sv["name"]))
                self.tbl_SinhVien.setItem(row, 2, QtWidgets.QTableWidgetItem(sv["class"]))
                row += 1
        else:
            self.GetAllSV()

    def GetAllSV(self):
        row = 0
        self.tbl_SinhVien.setColumnWidth(0, 100)
        self.tbl_SinhVien.setColumnWidth(1, 240)
        self.tbl_SinhVien.setColumnWidth(2, 220)
        self.tbl_SinhVien.setRowCount(len(self.lstSV))
        for sv in self.lstSV:
            self.tbl_SinhVien.setItem(row, 0, QtWidgets.QTableWidgetItem(sv["ID"]))
            self.tbl_SinhVien.setItem(row, 1, QtWidgets.QTableWidgetItem(sv["name"]))
            self.tbl_SinhVien.setItem(row, 2, QtWidgets.QTableWidgetItem(sv["class"]))
            row += 1

    def GetLop(self):
        row = self.tbl_Lop.currentIndex().row()
        ms = self.tbl_Lop.item(row, 0).text()
        for row in cursor.execute(f"select*from LOP,KHOA WHERE LOP.MAKHOA=KHOA.MAKHOA AND LOP.MALOP='{ms}'"):
            self.fi_TenLopHoc.setText(row[0])
            self.fi_KhoaLop.setCurrentText(row[3] + "-" + row[2])

    def GetSV(self):
        row = self.tbl_SinhVien.currentIndex().row()
        ms = self.tbl_SinhVien.item(row, 0).text()
        try:
            for row in cursor.execute(f"select * from SINHVIEN,KHOA,LOP,CHUYENNGANH,NIENKHOA WHERE SINHVIEN.MASV='{ms}' "
                                      f"AND LOP.MAKHOA=KHOA.MAKHOA AND SINHVIEN.MALOP=LOP.MALOP AND SINHVIEN.MACN=CHUYENNGANH.MACN "
                                      f"AND NIENKHOA.MANK=SINHVIEN.MANK"):
                self.fi_IDSV.setText(row[0])
                self.fi_Khoa.setCurrentText(row[17] + "-" + row[16])
                self.fi_ChuyenNganh.setCurrentText(row[21] + "-" + row[20])
                self.fi_NienKhoa.setCurrentText(row[24] + '-' + row[23])
                self.fi_Lop.setCurrentText(row[10])
                self.fi_GioiTinh.setCurrentText(row[6])
                self.fi_Email_2.setText(row[7])
                self.fi_DCTamTru.setText(row[9])
                self.fi_DCThuongTru.setText(row[8])
                self.fi_DanToc.setText(row[5])
                self.fi_HoTen.setText(row[1])
                self.fi_CMND.setText(row[4])
                self.fi_SDT.setText(row[2])
                self.fi_NgaySinh.setDate(
                QtCore.QDate(int(row[3].split('-')[0]), int(row[3].split('-')[1]), int(row[3].split('-')[2])))
                if row[11] == None:
                    self.rbo_KhongAnh.setChecked(True)
                    image = np.array(Image.open(f"Avatar/Who1.png"))
                    image = cv2.resize(image, (212, 137))
                    image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
                    img = QtGui.QImage(image, image.shape[1], image.shape[0], image.strides[0],
                                       QtGui.QImage.Format_RGB888)  # tổng số pixel quét của ảnh
                    self.lbl_Avatar.setPixmap(QtGui.QPixmap.fromImage(img))
                else:
                    self.rbo_CoAnh.setChecked(True)
                    image = np.array(Image.open(f"Avatar/{row[11]}"))

                    image = cv2.resize(image, (212, 137))
                    img = QtGui.QImage(image, image.shape[1], image.shape[0], image.strides[0],
                                       QtGui.QImage.Format_RGB888)  # tổng số pixel quét của ảnh
                    self.lbl_Avatar.setPixmap(QtGui.QPixmap.fromImage(img))
        except:
            pass

    def loadData(self):
        self.fi_ChuyenNganh.clear()
        self.fi_NienKhoa.clear()
        self.fi_Khoa.clear()
        self.fi_KhoaLop.clear()
        self.fi_Lop.clear()
        self.fi_GioiTinh.clear()
        self.cbo_TimSV.clear()
        self.cbo_TimLop.clear()

        for row in cursor.execute("  select * from CHUYENNGANH"):
            self.fi_ChuyenNganh.addItem(row[1] + "-" + row[0])
        for row in cursor.execute("select * from NIENKHOA"):
            self.fi_NienKhoa.addItem(row[1] + "-" + row[0])
        for row in cursor.execute("select * from KHOA"):
            self.fi_Khoa.addItem(row[1] + "-" + row[0])
            self.fi_KhoaLop.addItem(row[1] + "-" + row[0])
        for row in cursor.execute("select * from LOP"):
            self.fi_Lop.addItem(row[0])

        self.fi_GioiTinh.addItem("Nam")
        self.fi_GioiTinh.addItem("Nữ")
        self.fi_GioiTinh.addItem("Khác")

        # combobox tìm kiếm sinh viên
        self.cbo_TimSV.addItem("ID Sinh viên")
        self.cbo_TimSV.addItem("Họ tên")
        self.cbo_TimSV.addItem("Lớp")

        # combobox tìm lớp
        self.cbo_TimLop.addItem("Lớp")
        self.cbo_TimLop.addItem("Khoa")

        # table Lop
        i = 0
        self.lstLop = []
        for row in cursor.execute("select * from LOP,KHOA Where LOP.MAKHOA=KHOA.MAKHOA "):
            lop = {}
            lop["ID"] = row[0]
            lop["Khoa"] = row[2]
            self.lstLop.append(lop)
        self.tbl_Lop.setColumnWidth(0, 95)
        self.tbl_Lop.setColumnWidth(1, 63)
        self.tbl_Lop.setRowCount(len(self.lstLop))
        for lop in self.lstLop:
            self.tbl_Lop.setItem(i, 0, QtWidgets.QTableWidgetItem(lop["ID"]))
            self.tbl_Lop.setItem(i, 1, QtWidgets.QTableWidgetItem(lop["Khoa"]))
            i += 1

        # table Sinh Viên
        row = 0
        self.lstSV = []
        for row1 in cursor.execute("select * from SINHVIEN,LOP WHERE SINHVIEN.MALOP=LOP.MALOP"):
            SV = {}
            SV["ID"] = row1[0]
            SV["name"] = row1[1]
            SV["class"] = row1[10]
            self.lstSV.append(SV)

        self.tbl_SinhVien.setColumnWidth(0, 100)
        self.tbl_SinhVien.setColumnWidth(1, 240)
        self.tbl_SinhVien.setColumnWidth(2, 220)
        self.tbl_SinhVien.setRowCount(len(self.lstSV))
        for sv in self.lstSV:
            self.tbl_SinhVien.setItem(row, 0, QtWidgets.QTableWidgetItem(sv["ID"]))
            self.tbl_SinhVien.setItem(row, 1, QtWidgets.QTableWidgetItem(sv["name"]))
            self.tbl_SinhVien.setItem(row, 2, QtWidgets.QTableWidgetItem(sv["class"]))
            row += 1

# if __name__=="__main__":
#     app=QApplication(sys.argv)
#     ui=MAIN("00","AD")
#     app.exec_()