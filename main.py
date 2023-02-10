# !/usr/bin/python
# -*- coding: utf-8 -*-
import json
import sys

import cv2
# from PyQt5.QtCore import Qt
# from PyQt5.QtGui import QPixmap
# from PyQt5.QtWidgets import QWidget, QApplication
# from PyQt5.QtWidgets import QMessageBox
# QT5库
from PyQt5 import QtCore, QtWidgets, QtGui
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *

import login
from login import Ui_login
from userpage import Ui_UserPage
import database
import mediapipe_image as poseImage

# 当前用户,当前密码
Now_Username = 'USER'
Now_Password = ''

# 参考位置选项框flag
checkBoxDict = {'checkBox_right_elbow_flag': {'angle': 0, 'state': False},
                'checkBox_right_shoulder_flag': {'angle': 0, 'state': False},
                'checkBox_left_elbow_flag': {'angle': 0, 'state': False},
                'checkBox_left_shoulder_flag': {'angle': 0, 'state': False},
                'checkBox_left_hip_flag': {'angle': 0, 'state': False},
                'checkBox_right_hip_flag': {'angle': 0, 'state': False},
                'checkBox_left_knee_flag': {'angle': 0, 'state': False},
                'checkBox_right_knee_flag': {'angle': 0, 'state': False},
                }
checkPointDict = {'1': 'checkBox_right_elbow',
                  '2': 'checkBox_right_shoulder',
                  '3': 'checkBox_left_elbow',
                  '4': 'checkBox_left_shoulder',
                  '5': 'checkBox_left_hip',
                  '6': 'checkBox_right_hip',
                  '7': 'checkBox_left_knee',
                  '8': 'checkBox_right_knee', }
checkPointJson = {'sport_name': None, 'check_point': checkBoxDict}
print("进入main文件")


# 登录界面
class LoginWindow(QWidget, Ui_login):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setupUi(self)  # 渲染页面控件
        self.connect_signals()  # 设置信号槽
        self.start_x = None
        self.start_y = None
        self.setWindowFlags(Qt.FramelessWindowHint)  # 设置窗口标志：隐藏窗口边框

        pixmap = QPixmap(':/icon/9.png')
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.resize(pixmap.size())
        self.setMask(pixmap.mask())

    # 鼠标点击事件
    def mousePressEvent(self, event):
        if event.button() == QtCore.Qt.LeftButton:
            super(LoginWindow, self).mousePressEvent(event)
            self.start_x = event.x()
            self.start_y = event.y()

    # 鼠标释放事件
    def mouseReleaseEvent(self, event):
        self.start_x = None
        self.start_y = None

    # 鼠标移动事件
    def mouseMoveEvent(self, event):
        try:
            super(LoginWindow, self).mouseMoveEvent(event)
            dis_x = event.x() - self.start_x
            dis_y = event.y() - self.start_y
            self.move(self.x() + dis_x, self.y() + dis_y)
        except:
            pass

    def keyPressEvent(self, QKeyEvent):
        """快捷键"""
        if QKeyEvent.key() == Qt.Key_Enter or QKeyEvent.key() == Qt.Key_Return:  # enter
            self.pushButton_signin_clicked()

    # 用于窗口不规则图案绘制
    def paintEvent(self, event):
        painter = QPainter()
        painter.begin(self)
        painter.drawPixmap(0, 0, QPixmap(':/1/G:/png/1.png'))
        painter.end()

    # ------------------公用函数-----------------
    # 获取用户名栏信息
    def getEditUserName(self):
        global Now_Username
        Now_Username = self.lineEdit_username.text()
        print(Now_Username)
        return Now_Username

    # 获取用户密码栏的信息
    def getEditPassword(self):
        global Now_Password
        Now_Password = self.lineEdit_password.text()
        print(Now_Password)
        return Now_Password

    # 清除用户输入栏的信息
    def clearUserNameEditLine(self):
        self.lineEdit_username.clear()

    # 清除用户密码栏的信息
    def clearPasswordEditLine(self):
        self.lineEdit_password.clear()

    # ------------------控件功能-----------------
    # 注册按钮
    def pushButton_signup_clicked(self):
        if not (self.lineEdit_username.text() == '' or self.lineEdit_password.text() == ''):
            database.UserSignUp(self.getEditUserName(), self.getEditPassword())
            self.clearUserNameEditLine()
            self.clearPasswordEditLine()
        else:
            QMessageBox.information(self, '登录', '请输入有效信息', QMessageBox.Ok)

    # 登录按钮
    def pushButton_signin_clicked(self):
        if not (self.lineEdit_username.text() == '' or self.lineEdit_password.text() == ''):
            if not database.querypassword(self.getEditUserName(), self.getEditPassword()):
                # 匹配用户密码失败
                QMessageBox.information(None, '登录', '用户名不存在或密码错误', QMessageBox.Ok)
            else:
                # 匹配成功
                self.close()
                userPage.label_Now_username.setText(login_ui.getEditUserName())  # 获取用户名
                userPage.show()

        else:
            QMessageBox.information(None, '登录', '请输入有效信息', QMessageBox.Ok)

    # 信号连接
    def connect_signals(self):
        self.pushButton_signin.clicked.connect(self.pushButton_signin_clicked)  # 登录按钮事件绑定
        self.pushButton_signup.clicked.connect(self.pushButton_signup_clicked)  # 注册按钮事件绑定


# 用户界面
class UserPageWindow(QWidget, Ui_UserPage):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setupUi(self)  # 渲染页面控件
        self.connect_signals()  # 设置信号槽

        self.stackedWidget.setCurrentIndex(0)  # 默认界面为HomePage
        self.setWindowState(Qt.WindowMaximized)  # 窗口最大化

        # 过滤事件绑定
        self.label_right_elbow.installEventFilter(self)
        self.label_left_elbow.installEventFilter(self)
        self.label_right_knee.installEventFilter(self)
        self.label_left_knee.installEventFilter(self)
        self.label_right_hip.installEventFilter(self)
        self.label_left_hip.installEventFilter(self)
        self.label_right_shoulder.installEventFilter(self)
        self.label_left_shoulder.installEventFilter(self)

    # 清除填写内容
    def pushButton_page2_clear_clicked(self):
        self.lineEdit_page2_nowPwd.clear()
        self.lineEdit_page2_newPwd.clear()
        self.lineEdit_page2_newPwdAgain.clear()

    # 确认密码修改
    def pushButton_page2_ok_clicked(self):
        nowPwd = self.lineEdit_page2_nowPwd.text()
        newPwd = self.lineEdit_page2_newPwd.text()
        newPwdAgain = self.lineEdit_page2_newPwdAgain.text()
        if nowPwd == '' or newPwd == '' or newPwdAgain == '':  # 检查是否有空
            QMessageBox.information(None, "警告", "请将数据填写完整", QMessageBox.Ok)
        else:
            if nowPwd == newPwd or nowPwd == newPwdAgain or newPwd != newPwdAgain:  # 检查是否输入的新密码和原始密码一致
                QMessageBox.information(None, "警告", "密码与原密码一致或新密码不一致", QMessageBox.Ok)
            else:
                if Now_Password == self.lineEdit_page2_nowPwd.text():  # 检查当前密码是否正确
                    database.updatePassword(Now_Username, newPwd)
                    print("更新密码成功")
                else:
                    QMessageBox.information(None, "警告", "密码错误", QMessageBox.Ok)

    # 个人信息修改
    def pushButton_personaLinfoPage_changeInfo_clicked(self):
        pass

    # 个人信息修改确认
    def pushButton_personaLinfoPage_ok_clicked(self):
        pass

    # 左侧工具栏点击切换界面
    def listWidget_clicked(self, index: QModelIndex):
        # print(index)
        # print(index.row())
        if index.row() == 0:
            self.stackedWidget.setCurrentIndex(0)
        elif index.row() == 1:
            self.stackedWidget.setCurrentIndex(1)
        elif index.row() == 2:
            self.stackedWidget.setCurrentIndex(2)
        elif index.row() == 3:
            self.stackedWidget.setCurrentIndex(3)
        elif index.row() == 4:
            self.stackedWidget.setCurrentIndex(4)
        elif index.row() == 5:
            self.stackedWidget.setCurrentIndex(5)

    # 照片角度显示
    def showAngle(self, angle_data):
        self.label_right_elbow_data.setText("{:.2f}°".format(angle_data[0]))
        self.label_left_elbow_data.setText("{:.2f}°".format(angle_data[1]))
        self.label_right_knee_data.setText("{:.2f}°".format(angle_data[2]))
        self.label_left_knee_data.setText("{:.2f}°".format(angle_data[3]))
        self.label_right_hip_data.setText("{:.2f}°".format(angle_data[4]))
        self.label_left_hip_data.setText("{:.2f}°".format(angle_data[5]))
        self.label_right_shoulder_data.setText("{:.2f}°".format(angle_data[6]))
        self.label_left_shoulder_data.setText("{:.2f}°".format(angle_data[7]))
        j = 1
        for i in angle_data:
            # print(i)
            # print(checkPointDict.get(str(j))+'_flag')
            checkBoxDict[checkPointDict.get(str(j)) + '_flag']['angle'] = i
            # print(checkBoxDict[checkPointDict.get(str(j))+'_flag']['angle'])
            j += 1
        # print(checkBoxDict)

    # 获取图片路径
    def getFileDirectory(self):
        fileDirectory = QFileDialog.getOpenFileName(self, "请选择图片路径", "./")  # 返回选中的文件路径
        print(fileDirectory)
        before, later, actions = poseImage.startOpenpose(fileDirectory)
        self.showAngle(actions)
        pix = QPixmap('background.jpg')
        size = (int(self.label_before.width()), int(self.label_before.height()))
        # shrink = cv2.resize(before, size, interpolation=cv2.INTER_AREA)
        # # cv2.imshow('img', shrink)
        # shrink = cv2.cvtColor(shrink, cv2.COLOR_BGR2RGB)
        # self.QtImg = QtGui.QImage(shrink.data,
        #                           shrink.shape[1],
        #                           shrink.shape[0],
        #                           shrink.shape[1] * 3,
        #                           QtGui.QImage.Format_RGB888)
        #
        # self.label_before.setPixmap(QtGui.QPixmap.fromImage(self.QtImg))

        shrink1 = cv2.resize(later, size, interpolation=cv2.INTER_AREA)
        shrink1 = cv2.cvtColor(shrink1, cv2.COLOR_BGR2RGB)
        self.QtImg = QtGui.QImage(shrink1.data,
                                  shrink1.shape[1],
                                  shrink1.shape[0],
                                  shrink1.shape[1] * 3,
                                  QtGui.QImage.Format_RGB888)

        self.label_before.setPixmap(QtGui.QPixmap.fromImage(self.QtImg))

    # 事件过滤
    def eventFilter(self, object, event):
        if event.type() == QEvent.Enter:  # 当鼠标进入时
            if object.text() == '右手肘':
                QToolTip.showText(QCursor.pos(), '<img src=":/pic/14.png">', self)
                # print('Mouse is over the label, Object Text, {}'.format(object.text()))
            elif object.text() == '右大臂':
                QToolTip.showText(QCursor.pos(), '<img src=":/pic/12.png">', self)
            elif object.text() == '左手肘':
                QToolTip.showText(QCursor.pos(), '<img src=":/pic/13.png">', self)
            elif object.text() == '左大臂':
                QToolTip.showText(QCursor.pos(), '<img src=":/pic/11.png">', self)
            elif object.text() == '左腰':
                QToolTip.showText(QCursor.pos(), '<img src=":/pic/23.png">', self)
            elif object.text() == '右腰':
                QToolTip.showText(QCursor.pos(), '<img src=":/pic/24.png">', self)
            elif object.text() == '左膝盖':
                QToolTip.showText(QCursor.pos(), '<img src=":/pic/25.png">', self)
            elif object.text() == '右膝盖':
                QToolTip.showText(QCursor.pos(), '<img src=":/pic/26.png">', self)

            return True
        elif event.type() == QEvent.Leave:  # 当鼠标离开时
            print('Mouse is not over the label')

        return False

    # 根据选择参考修改flag
    def checkBoxRecord(self, btn, _checkBoxFlags, _state):
        if btn.isChecked():
            checkBoxDict[_checkBoxFlags][_state] = True
        else:
            checkBoxDict[_checkBoxFlags][_state] = False
        # print("flag:" + str(_checkBoxFlags) + "  " + str(
        #     checkBoxDict.get(_checkBoxFlags)))

    # 创建标准
    def crateStandard(self):
        filename = self.lineEdit_sportName.text()
        if filename == '':
            QMessageBox.information(None, "警告", "请填写运动名", QMessageBox.Ok)
            return
        checkPointJson['sport_name'] = filename
        # 直接用dump()方法将python字典数据写入json文件中,并格式化
        with open("config/" + filename + ".json", 'w') as write_f:
            json.dump(checkPointJson, write_f, indent=4, ensure_ascii=False)
            QMessageBox.information(None, "提示", "创建" + filename + "运动完成", QMessageBox.Ok)

    # 信号连接
    def connect_signals(self):
        self.pushButton_personaLinfoPage_ok.clicked.connect(self.pushButton_personaLinfoPage_ok_clicked)  # 个人信息修改确认
        self.pushButton_page2_clear.clicked.connect(self.pushButton_page2_clear_clicked)  # 清除填写内容
        self.pushButton_page2_ok.clicked.connect(self.pushButton_page2_ok_clicked)  # 确认密码修改
        self.listWidget.clicked.connect(self.listWidget_clicked)  # 左侧工具栏点击切换界面
        self.pushButton_startOpenpose.clicked.connect(self.getFileDirectory)  # 获取图片路径
        self.pushButton_cteateStandard.clicked.connect(self.crateStandard)

        # 根据选择参考修改flag
        self.checkBox_right_elbow.stateChanged.connect(
            lambda: self.checkBoxRecord(self.checkBox_right_elbow, 'checkBox_right_elbow_flag', 'state'))
        self.checkBox_right_shoulder.stateChanged.connect(
            lambda: self.checkBoxRecord(self.checkBox_right_shoulder, 'checkBox_right_shoulder_flag', 'state'))
        self.checkBox_left_elbow.stateChanged.connect(
            lambda: self.checkBoxRecord(self.checkBox_left_elbow, 'checkBox_left_elbow_flag', 'state'))
        self.checkBox_left_shoulder.stateChanged.connect(
            lambda: self.checkBoxRecord(self.checkBox_left_shoulder, 'checkBox_left_shoulder_flag', 'state'))
        self.checkBox_left_hip.stateChanged.connect(
            lambda: self.checkBoxRecord(self.checkBox_left_hip, 'checkBox_left_hip_flag', 'state'))
        self.checkBox_right_hip.stateChanged.connect(
            lambda: self.checkBoxRecord(self.checkBox_right_hip, 'checkBox_right_hip_flag', 'state'))
        self.checkBox_left_knee.stateChanged.connect(
            lambda: self.checkBoxRecord(self.checkBox_left_knee, 'checkBox_left_knee_flag', 'state'))
        self.checkBox_right_knee.stateChanged.connect(
            lambda: self.checkBoxRecord(self.checkBox_right_knee, 'checkBox_right_knee_flag', 'state'))


if __name__ == '__main__':
    print("进入__name__ == '__main__'")
    app = QApplication(sys.argv)
    login_ui = LoginWindow()  # 登录界面
    login_ui.show()  # 打开登录界面
    userPage = UserPageWindow()  # 主界面

    database.createConnection()  # 创建连接
    # database.createTable()#创建数据库内容

    # ------------------按钮信号连接-----------------
    # 关闭登录界面
    login_ui.pushButton_quit.clicked.connect(  # 切换界面到userpage画面
        lambda: {login_ui.close()}
    )

    sys.exit(app.exec_())