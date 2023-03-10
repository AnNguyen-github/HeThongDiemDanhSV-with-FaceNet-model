import sys
from PyQt5 import QtWidgets,uic,QtGui,QtCore
from  PyQt5.QtWidgets import  QMainWindow,QMessageBox,QApplication,QWidget,QLabel
from PyQt5.QtGui import QMovie
from PyQt5.QtCore import QTimer
import pyodbc
import  numpy as np
from PIL import Image
from cv2 import  cv2
con=pyodbc.connect('Driver={SQL Server};'
                   'SERVER=TRIEUAN\MASTERSQL;'
                   'Database=KhoaLuan;'
                   'Trusted_connection=yes')
cursor=con.cursor()
# stylesheet = """
#     frm_Login {
#         background-image: url("Image_Gui/image.png");
#         background-repeat: no-repeat;
#         background-position: center;
#         background-size: 100% 100%;
#     }
# """

class frm_Login(QMainWindow):
    def __init__(self):
        super().__init__()
        uic.loadUi('login.ui',self)
        self.movie = QMovie('Loading_2.gif')
        self.label_2.setMovie(self.movie)
        self.btn_DangNhap.clicked.connect(self.DangNhap)
        # self.timer = QTimer(self)
        # self.timer.timeout.connect(self.startAnimation)
        # self.timer.start(100)
        self.label_2.setVisible(False)
        self.movie.start()
        QApplication.processEvents()
        self.show()
    def startAnimation(self):
        self.movie.start()
        QApplication.processEvents()
    def DangNhap(self):
        con = pyodbc.connect('Driver={SQL Server};'
                             'SERVER=TRIEUAN\MASTERSQL;'
                             'Database=KhoaLuan;'
                             'Trusted_connection=yes')
        cursor = con.cursor()
        cursor.execute(f"select* from SINHVIEN Where MASV='{self.txt_ID.text()}' AND MATKHAU='{self.txt_Pwd.text()}'")
        data = cursor.fetchall()
        cursor.execute(f"select* from GIANGVIEN Where MAGV='{self.txt_ID.text()}' AND MATKHAU='{self.txt_Pwd.text()}'")
        data2 = cursor.fetchall()

        if data2==[] and data==[]:
            msg = QMessageBox()
            msg.setIcon(QMessageBox.Warning)
            msg.setWindowTitle("Thông báo")
            msg.setText("Tài khoản hoặc mật khẩu không đúng!!")
            msg.setStandardButtons(QMessageBox.Ok)
            result = msg.exec_()
        elif data2!= []:
            self.label_2.setVisible(True)
            QApplication.processEvents()
            import main
            fr = main.MAIN(self.txt_ID.text(), data2[0][14])
            fr.show()
            self.hide()
        elif data !=[]:
            self.label_2.setVisible(True)
            QApplication.processEvents()
            import main
            fr=main.MAIN(self.txt_ID.text(),data[0][15])
            fr.show()
            self.hide()





if __name__=="__main__":
    app=QApplication(sys.argv)
    # app.setStyleSheet(stylesheet)
    ui=frm_Login()
    app.exec_()