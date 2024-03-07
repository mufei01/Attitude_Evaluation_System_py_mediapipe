# !/usr/bin/python
# -*- coding: utf-8 -*-
import json
import sys
import threading
import os

sys.path.append(
    'E:\myComputer\desktop\BigProject\Attitude_Evaluation_System_py_mediapipe\mediapipe_knn')  # 将此目录添加到检索目录中
# print("路径", sys.path)
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
import mediapipe as mp
import numpy as np



# 当前用户,当前密码
Now_Username = 'USER'
Now_Password = ''

sport_name = None
check_point = None
startPosePicFile = None
stopPosePicFile = None

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
        self.cap = None
        self.QtImg = None
        self.thstop = False
        self.isReadStandard = False
        self.stage_flag = False
        self.isChangePose = True

        self.setupUi(self)  # 渲染页面控件
        self.connect_signals()  # 设置信号槽

        self.stackedWidget.setCurrentIndex(0)  # 默认界面为HomePage
        self.setWindowState(Qt.WindowMaximized)  # 窗口最大化

        self.pushButton_stopDetection.setEnabled(False)

        # 过滤事件绑定
        self.label_right_elbow.installEventFilter(self)
        self.label_left_elbow.installEventFilter(self)
        self.label_right_knee.installEventFilter(self)
        self.label_left_knee.installEventFilter(self)
        self.label_right_hip.installEventFilter(self)
        self.label_left_hip.installEventFilter(self)
        self.label_right_shoulder.installEventFilter(self)
        self.label_left_shoulder.installEventFilter(self)

        self.label_right_elbow_2.installEventFilter(self)
        self.label_left_elbow_2.installEventFilter(self)
        self.label_right_knee_2.installEventFilter(self)
        self.label_left_knee_2.installEventFilter(self)
        self.label_right_hip_2.installEventFilter(self)
        self.label_left_hip_2.installEventFilter(self)
        self.label_right_shoulder_2.installEventFilter(self)
        self.label_left_shoulder_2.installEventFilter(self)

        # 角度显示label
        self.PosePoint = [
            self.label_right_elbow_data,
            self.label_left_elbow_data,
            self.label_right_shoulder_data,
            self.label_left_shoulder_data,
            self.label_left_hip_data,
            self.label_right_hip_data,
            self.label_left_knee_data,
            self.label_right_knee_data
        ]
        self.PosePoint_2 = [
            self.label_right_elbow_data_2,
            self.label_left_elbow_data_2,
            self.label_right_shoulder_data_2,
            self.label_left_shoulder_data_2,
            self.label_left_hip_data_2,
            self.label_right_hip_data_2,
            self.label_left_knee_data_2,
            self.label_right_knee_data_2
        ]
        # 勾选框
        self.checkPoint = [
            self.checkBox_right_elbow,
            self.checkBox_left_elbow,
            self.checkBox_right_shoulder,
            self.checkBox_left_shoulder,
            self.checkBox_left_hip,
            self.checkBox_right_hip,
            self.checkBox_left_knee,
            self.checkBox_right_knee,
        ]
        # 参考位置选项框flag
        self.checkBoxDict = {
            # 开始动作
            'checkBox_right_elbow_flag': {'angle': 0, 'state': False},
            'checkBox_left_elbow_flag': {'angle': 0, 'state': False},
            'checkBox_right_shoulder_flag': {'angle': 0, 'state': False},
            'checkBox_left_shoulder_flag': {'angle': 0, 'state': False},
            'checkBox_left_hip_flag': {'angle': 0, 'state': False},
            'checkBox_right_hip_flag': {'angle': 0, 'state': False},
            'checkBox_left_knee_flag': {'angle': 0, 'state': False},
            'checkBox_right_knee_flag': {'angle': 0, 'state': False},
        }
        self.checkBoxDict_2 = {
            # 结束动作
            'checkBox_right_elbow_2_flag': {'angle': 0, 'state': False},
            'checkBox_left_elbow_2_flag': {'angle': 0, 'state': False},
            'checkBox_right_shoulder_2_flag': {'angle': 0, 'state': False},
            'checkBox_left_shoulder_2_flag': {'angle': 0, 'state': False},
            'checkBox_left_hip_2_flag': {'angle': 0, 'state': False},
            'checkBox_right_hip_2_flag': {'angle': 0, 'state': False},
            'checkBox_left_knee_2_flag': {'angle': 0, 'state': False},
            'checkBox_right_knee_2_flag': {'angle': 0, 'state': False},
        }
        self.checkBoxDictSum = {}

        self.checkPointDict = {
            # 开始动作
            '0': 'checkBox_right_elbow',
            '1': 'checkBox_left_elbow',
            '2': 'checkBox_right_shoulder',
            '3': 'checkBox_left_shoulder',
            '4': 'checkBox_left_hip',
            '5': 'checkBox_right_hip',
            '6': 'checkBox_left_knee',
            '7': 'checkBox_right_knee',
        }
        self.checkPointDict_2 = {
            # 结束动作
            '0': 'checkBox_right_elbow_2',
            '1': 'checkBox_left_elbow_2',
            '2': 'checkBox_right_shoulder_2',
            '3': 'checkBox_left_shoulder_2',
            '4': 'checkBox_left_hip_2',
            '5': 'checkBox_right_hip_2',
            '6': 'checkBox_left_knee_2',
            '7': 'checkBox_right_knee_2'
        }

        self.checkPointJson = {'sport_name': None, 'check_point': self.checkBoxDictSum, 'startPosePicFile': None,
                               'stopPosePicFile': None}

        self.angle14 = 0
        self.angle13 = 0
        self.angle26 = 0
        self.angle25 = 0
        self.angle24 = 0
        self.angle23 = 0
        self.angle12 = 0
        self.angle11 = 0

    def keyPressEvent(self, QKeyEvent):
        """快捷键"""
        if QKeyEvent.key() == Qt.Key_F11:  # F11
            if not self.isFullScreen():
                self.setWindowState(Qt.WindowFullScreen)  # 窗口最大化
            else:
                self.setWindowState(Qt.WindowMaximized)  # 窗口最大化

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
    def showAngle(self, angle_data, labels, _checkBoxDict, checkPointDictInedx):
        for i in range(8):
            labels[i].setText("{:.2f}°".format(angle_data[i]))
        # self.label_right_elbow_data.setText("{:.2f}°".format(angle_data[0]))
        j = 0
        for i in angle_data:
            # print(i)
            # print(self.checkPointDict.get(str(j))+'_flag')
            _checkBoxDict[checkPointDictInedx.get(str(j)) + '_flag']['angle'] = i
            # print(self.checkBoxDict[self.checkPointDict.get(str(j))+'_flag']['angle'])
            j += 1
        # print(self.checkBoxDict)

    # 获取图片路径
    def getFileDirectory(self, _checkBoxDict, checkPointDictInedx, labels, labelOnShow):
        filename = self.lineEdit_sportName.text()
        if filename == '':
            QMessageBox.information(None, "警告", "请填写运动名", QMessageBox.Ok)
            return
        fileDirectory = QFileDialog.getOpenFileName(self, "请选择图片路径", "./", "*.jpg *.png")  # 返回选中的文件路径
        if fileDirectory[0] == "": return
        print(fileDirectory)
        for i in range(8):  # 情况勾选框
            self.checkPoint[i].setChecked(False)
        before, later, actions = poseImage.startOpenpose(fileDirectory)
        self.showAngle(actions, labels, _checkBoxDict, checkPointDictInedx)
        pix = QPixmap('background.jpg')
        size = (int(labelOnShow.width()), int(labelOnShow.height()))

        img = cv2.imread(fileDirectory[0])
        width, height = img.shape[:2]
        # print("width:" + str(width) + "-" + 'height:' + str(height))
        # print(size)
        shrink1 = cv2.resize(later, (height, width), interpolation=cv2.INTER_AREA)
        shrink1 = cv2.cvtColor(shrink1, cv2.COLOR_BGR2RGB)
        if checkPointDictInedx.get('0') == 'checkBox_right_elbow':
            saveFileNme = './config/' + self.lineEdit_sportName.text() + '_start.jpg'
            self.checkPointJson['startPosePicFile'] = saveFileNme
        elif checkPointDictInedx.get('0') == 'checkBox_right_elbow_2':
            saveFileNme = './config/' + self.lineEdit_sportName.text() + '_stop.jpg'
            self.checkPointJson['stopPosePicFile'] = saveFileNme
        self.QtImg = QtGui.QImage(shrink1.data,
                                  shrink1.shape[1],
                                  shrink1.shape[0],
                                  shrink1.shape[1] * 3,
                                  QtGui.QImage.Format_RGB888)
        self.QtImg.save(saveFileNme, 'JPG')
        labelOnShow.setPixmap(QtGui.QPixmap.fromImage(self.QtImg))

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
    def checkBoxRecord(self, btn, _checkBoxDict, _checkBoxDict_2, _checkBoxFlags, _checkBoxFlags_2, _state):
        if btn.isChecked():
            _checkBoxDict[_checkBoxFlags][_state] = True
            _checkBoxDict_2[_checkBoxFlags_2][_state] = True
        else:
            _checkBoxDict[_checkBoxFlags][_state] = False
            _checkBoxDict_2[_checkBoxFlags_2][_state] = False
        print("flag:" + str(_checkBoxFlags) + "  " + str(_checkBoxDict.get(_checkBoxFlags)))
        print("flag:" + str(_checkBoxFlags_2) + "  " + str(_checkBoxDict_2.get(_checkBoxFlags_2)))

    # 创建标准
    def createStandard(self):
        filename = self.lineEdit_sportName.text()
        if filename == '':
            QMessageBox.information(None, "警告", "请填写运动名", QMessageBox.Ok)
            return
        self.checkBoxDictSum = self.checkBoxDict.copy()
        self.checkBoxDictSum.update(self.checkBoxDict_2)
        self.checkPointJson['check_point'] = self.checkBoxDictSum
        self.checkPointJson['sport_name'] = filename
        # 直接用dump()方法将python字典数据写入json文件中,并格式化
        with open("config/" + filename + ".json", 'w') as write_f:
            json.dump(self.checkPointJson, write_f, indent=4, ensure_ascii=False)
            QMessageBox.information(None, "提示", "创建" + filename + "运动完成", QMessageBox.Ok)

    def readStandard(self):
        global sport_name, check_point, startPosePicFile, stopPosePicFile
        fileDirectory = QFileDialog.getOpenFileName(self, "请选择标准路径", "./config", "*.json")  # 返回选中的文件路径
        if fileDirectory[0] == "":  # 未选择文件
            self.isReadStandard = False
            return
        # print(fileDirectory)
        with open(fileDirectory[0], 'r') as load_f:
            load_dict = json.load(load_f)
            # print(load_dict)
            # print(type(load_dict))
        self.label_video.setText("标准导入成功")
        sport_name = load_dict['sport_name']
        check_point = load_dict['check_point']
        startPosePicFile = load_dict['startPosePicFile']
        stopPosePicFile = load_dict['stopPosePicFile']
        # print("check_point:" + str(check_point))
        # print("check_point:"+str(type(check_point)))
        # 角度和勾选框数据导入
        for i in range(8):  # 开始动作数据导入
            self.PosePoint[i].setText("{:.2f}°".format(check_point[self.checkPointDict.get(str(i)) + '_flag']['angle']))
        for i in range(8):  # 开始动作数据导入
            if check_point[self.checkPointDict.get(str(i)) + '_flag']['state'] == True:
                self.checkPoint[i].setChecked(True)
            else:
                self.checkPoint[i].setChecked(False)
        for i in range(8):  # 结束动作数据导入
            self.PosePoint_2[i].setText(
                "{:.2f}°".format(check_point[self.checkPointDict_2.get(str(i)) + '_flag']['angle']))

        _width, _height = (int(self.label_startActionPicture.width()), int(self.label_startActionPicture.height()))
        print(_width, _height)
        pix_start = QPixmap(startPosePicFile)
        pix_start.scaled(_width, _height)
        self.label_startActionPicture.setPixmap(pix_start)

        pix_stop = QPixmap(stopPosePicFile)
        pix_stop.scaled(_width, _height)
        self.label_stopActionPicture.setPixmap(pix_stop)
        # QMessageBox.information(None, "提示", "导入成功", QMessageBox.Ok)
        self.isReadStandard = True

    def stopDetection(self):
        self.thstop = True
        self.label_video.setText("关闭相机中。。。")
        self.pushButton_stopDetection.setEnabled(False)
        self.pushButton_startDetection.setEnabled(True)
        self.pushButton_readStandard_2.setEnabled(True)
        self.timeEdit.setEnabled(True)

    # 检测界面
    def startDetection(self):
        if not self.isReadStandard:
            return
        # 开始检测后关闭按钮
        self.pushButton_stopDetection.setEnabled(True)
        self.pushButton_startDetection.setEnabled(False)
        self.pushButton_readStandard_2.setEnabled(False)
        self.timeEdit.setEnabled(False)

        self.label_video.setText("打开相机中。。。")
        mp_drawing = mp.solutions.drawing_utils
        mp_pose = mp.solutions.pose
        counter = 0
        stage = ['stretch', 'stretch', 'stretch', 'stretch', 'stretch', 'stretch', 'stretch', 'stretch']
        print("open camera")
        self.thstop = False
        self.cap = cv2.VideoCapture(0)  # 开启摄像头
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 800)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 600)
        self.cap.set(cv2.CAP_PROP_FPS, 20)
        inputFlag = [False, False, False, False, False, False, False, False]
        inputAngle_begin = [0, 0, 0, 0, 0, 0, 0, 0]
        inputAngle_stop = [0, 0, 0, 0, 0, 0, 0, 0]
        isChangePose = [False, False, False, False, False, False, False, False]
        for i in range(8):  # 开始动作数据导入
            inputAngle_begin[i] = check_point[self.checkPointDict.get(str(i)) + '_flag']['angle']
        for i in range(8):  # 结束动作数据导入
            inputAngle_stop[i] = check_point[self.checkPointDict_2.get(str(i)) + '_flag']['angle']
        for i in range(8):  # 检测关节导入
            if check_point[self.checkPointDict.get(str(i)) + '_flag']['state']:
                inputFlag[i] = True
            else:
                inputFlag[i] = False

        print("inputFlag:" + str(inputFlag))
        print("inputAngle_begin:" + str(inputAngle_begin))
        print("inputAngle_stop:" + str(inputAngle_stop))

        for i in range(8):  # 数值大的放stop，小的放begin
            if inputAngle_begin[i] > inputAngle_stop[i]:
                tempAngle = inputAngle_stop[i]
                inputAngle_stop[i] = inputAngle_begin[i]
                inputAngle_begin[i] = tempAngle

        print("inputAngle_begin:" + str(inputAngle_begin))
        print("inputAngle_stop:" + str(inputAngle_stop))
        with mp_pose.Pose(min_detection_confidence=0.5, min_tracking_confidence=0.5) as pose:
            while self.cap.isOpened():
                if self.thstop:
                    print("cap stop")
                    self.cap.release()
                    return
                ret, img = self.cap.read()
                if ret == False:
                    print("ret:False")
                    continue
                # get a frame
                ret, img = self.cap.read()
                img = cv2.flip(img, 1)
                height, width, bytesPerComponent = img.shape
                bytesPerLine = bytesPerComponent * width
                # 变换彩色空间顺序
                image = cv2.cvtColor(img, cv2.COLOR_BGR2RGB, img)

                image.flags.writeable = False

                # Make detection
                results = pose.process(image)

                # Recolor back to BGR
                image.flags.writeable = True
                # image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)

                # Extract landmarks
                try:
                    landmarks = results.pose_landmarks.landmark

                    right_shoulder = [landmarks[mp_pose.PoseLandmark.RIGHT_SHOULDER.value].x,
                                      landmarks[mp_pose.PoseLandmark.RIGHT_SHOULDER.value].y]
                    right_elbow = [landmarks[mp_pose.PoseLandmark.RIGHT_ELBOW.value].x,
                                   landmarks[mp_pose.PoseLandmark.RIGHT_ELBOW.value].y]
                    right_wrist = [landmarks[mp_pose.PoseLandmark.RIGHT_WRIST.value].x,
                                   landmarks[mp_pose.PoseLandmark.RIGHT_WRIST.value].y]
                    left_shoulder = [landmarks[mp_pose.PoseLandmark.LEFT_SHOULDER.value].x,
                                     landmarks[mp_pose.PoseLandmark.LEFT_SHOULDER.value].y]
                    left_elbow = [landmarks[mp_pose.PoseLandmark.LEFT_ELBOW.value].x,
                                  landmarks[mp_pose.PoseLandmark.LEFT_ELBOW.value].y]
                    left_wrist = [landmarks[mp_pose.PoseLandmark.LEFT_WRIST.value].x,
                                  landmarks[mp_pose.PoseLandmark.LEFT_WRIST.value].y]
                    right_hip = [landmarks[mp_pose.PoseLandmark.RIGHT_HIP.value].x,
                                 landmarks[mp_pose.PoseLandmark.RIGHT_HIP.value].y]
                    right_knee = [landmarks[mp_pose.PoseLandmark.RIGHT_KNEE.value].x,
                                  landmarks[mp_pose.PoseLandmark.RIGHT_KNEE.value].y]
                    right_ankle = [landmarks[mp_pose.PoseLandmark.RIGHT_ANKLE.value].x,
                                   landmarks[mp_pose.PoseLandmark.RIGHT_ANKLE.value].y]
                    left_hip = [landmarks[mp_pose.PoseLandmark.LEFT_HIP.value].x,
                                landmarks[mp_pose.PoseLandmark.LEFT_HIP.value].y]
                    left_knee = [landmarks[mp_pose.PoseLandmark.LEFT_KNEE.value].x,
                                 landmarks[mp_pose.PoseLandmark.LEFT_KNEE.value].y]
                    left_ankle = [landmarks[mp_pose.PoseLandmark.LEFT_ANKLE.value].x,
                                  landmarks[mp_pose.PoseLandmark.LEFT_ANKLE.value].y]

                    if inputFlag[0]:
                        self.angle14 = poseImage.calculate_angle(right_shoulder, right_elbow,
                                                                 right_wrist)  # 右手臂，右手肘的角度 14
                        if self.angle14 > inputAngle_stop[0]:
                            stage[0] = "stretch"
                            isChangePose[0] = False
                        if self.angle14 < inputAngle_begin[0] and stage[0] == 'stretch':
                            stage[0] = "crouch"
                            isChangePose[0] = True
                        print("angle14:", stage[0], "+", str(self.angle14), "+", inputAngle_begin[0], "+",
                              inputAngle_stop[0])
                    if inputFlag[1]:
                        self.angle13 = poseImage.calculate_angle(left_shoulder, left_elbow, left_wrist)  # 左手臂，左手肘的角度 13
                        if self.angle13 > inputAngle_stop[1]:
                            stage[1] = "stretch"
                            isChangePose[1] = False
                        if self.angle13 < inputAngle_begin[1] and stage[1] == 'stretch':
                            stage[1] = "crouch"
                            isChangePose[1] = True
                        print("angle13:", stage[1], "+", str(self.angle13), "+", inputAngle_begin[1], "+",
                              inputAngle_stop[1])
                    if inputFlag[2]:
                        self.angle26 = poseImage.calculate_angle(right_hip, right_knee, right_ankle)  # 右大腿，右小腿的角度 26
                        if self.angle26 > inputAngle_stop[2]:
                            stage[2] = "stretch"
                        if self.angle26 < inputAngle_begin[2] and stage[2] == 'stretch':
                            stage[2] = "crouch"
                            isChangePose[2] = True
                        print("angle26:", stage[2], "+", str(self.angle26), "+", inputAngle_begin[2], "+",
                              inputAngle_stop[2])
                    if inputFlag[3]:
                        self.angle25 = poseImage.calculate_angle(left_hip, left_knee, left_ankle)  # 左大腿，左小腿的角度 25
                        if self.angle25 > inputAngle_stop[3]:
                            stage[3] = "stretch"
                        if self.angle25 < inputAngle_begin[3] and stage[2] == 'stretch':
                            stage[3] = "crouch"
                            isChangePose[3] = True
                        print("angle25:", stage[3], "+", str(self.angle25), "+", inputAngle_begin[3], "+",
                              inputAngle_stop[3])
                    if inputFlag[4]:
                        self.angle24 = poseImage.calculate_angle(right_shoulder, right_hip, right_knee)  # 右肩，右大腿的角度 24
                        if self.angle24 > inputAngle_stop[4]:
                            stage[4] = "stretch"
                        if self.angle24 < inputAngle_begin[4] and stage[4] == 'stretch':
                            stage[4] = "crouch"
                            isChangePose[4] = True
                        print("angle24:", stage[4], "+", str(self.angle24), "+", inputAngle_begin[4], "+",
                              inputAngle_stop[4])
                    if inputFlag[5]:
                        self.angle23 = poseImage.calculate_angle(left_shoulder, left_hip, left_knee)  # 左肩，左大腿的角度 23
                        if self.angle23 > inputAngle_stop[5]:
                            stage[5] = "stretch"
                        if self.angle23 < inputAngle_begin[5] and stage[5] == 'stretch':
                            stage[5] = "crouch"
                            isChangePose[5] = True
                        print("angle23:", stage[5], "+", str(self.angle23), "+", inputAngle_begin[5], "+",
                              inputAngle_stop[5])
                    if inputFlag[6]:
                        self.angle12 = poseImage.calculate_angle(right_elbow, right_shoulder, right_hip)  # 右大臂，右臀的角度 12
                        if self.angle12 > inputAngle_stop[6]:
                            stage[6] = "stretch"
                        if self.angle12 < inputAngle_begin[6] and stage[6] == 'stretch':
                            stage[6] = "crouch"
                            isChangePose[6] = True
                        print("angle12:", stage[6], "+", str(self.angle12), "+", inputAngle_begin[6], "+",
                              inputAngle_stop[6])
                    if inputFlag[7]:
                        self.angle11 = poseImage.calculate_angle(left_elbow, left_shoulder, left_hip)  # 左大臂，左臀的角度 11
                        if self.angle11 > inputAngle_stop[7]:
                            stage[7] = "stretch"
                        if self.angle11 < inputAngle_begin[7] and stage[7] == 'stretch':
                            stage[7] = "crouch"
                            isChangePose[7] = True
                        print("angle11:", stage[7], "+", str(self.angle11), "+", inputAngle_begin[7], "+",
                              inputAngle_stop[7])
                    self.isChangePose = True
                    for i in range(8):
                        if inputFlag[i]:
                            if not isChangePose[i]:
                                self.isChangePose = False
                    if self.isChangePose:  # 如果都为crouch则一次动作完成
                        counter += 1
                        for i in range(8):
                            isChangePose[i] = False
                        self.isChangePose = False

                    cv2.putText(image, str(counter),
                                (100, 100),
                                cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 2, cv2.LINE_AA
                                )
                    print(self.timeEdit.time())
                    print(self.timeEdit.time().minute())
                    print(self.timeEdit.time().second())

                except:
                    print("error")

                mp_drawing.draw_landmarks(image, results.pose_landmarks, mp_pose.POSE_CONNECTIONS,
                                          mp_drawing.DrawingSpec(color=(245, 117, 66), thickness=2, circle_radius=2),
                                          mp_drawing.DrawingSpec(color=(245, 66, 230), thickness=2, circle_radius=2)
                                          )

                # 转为QImage对象
                self.image = QImage(image.data, width, height, bytesPerLine, QImage.Format_RGB888)
                self.label_video.setPixmap(
                    QPixmap.fromImage(self.image).scaled(self.label_video.width(), self.label_video.height()))

    def startDetection2(self):
        # flag = int(input("请输入检测的运动类型（数字）：1. 俯卧撑\t2. 深蹲\t3. 引体向上（暂未获得csv文件）\n"))
        flag = 1
        print("\n按英文状态下的q或esc退出摄像头采集")
        # tp.trainset_process(flag)
        vc.process(flag,self)

    # 信号连接
    def connect_signals(self):
        self.pushButton_personaLinfoPage_ok.clicked.connect(self.pushButton_personaLinfoPage_ok_clicked)  # 个人信息修改确认
        self.pushButton_page2_clear.clicked.connect(self.pushButton_page2_clear_clicked)  # 清除填写内容
        self.pushButton_page2_ok.clicked.connect(self.pushButton_page2_ok_clicked)  # 确认密码修改
        self.listWidget.clicked.connect(self.listWidget_clicked)  # 左侧工具栏点击切换界面
        self.pushButton_startAction.clicked.connect(
            lambda: self.getFileDirectory(self.checkBoxDict, self.checkPointDict, self.PosePoint,
                                          self.label_startActionPicture))  # 获取开始动作图片路径
        self.pushButton_stopAction.clicked.connect(
            lambda: self.getFileDirectory(self.checkBoxDict_2, self.checkPointDict_2, self.PosePoint_2,
                                          self.label_stopActionPicture))  # 获取结束动作图片路径
        self.pushButton_cteateStandard.clicked.connect(self.createStandard)  # 生成标准
        self.pushButton_readStandard.clicked.connect(self.readStandard)  # 查看标准

        # 检测界面
        self.pushButton_startDetection.clicked.connect(lambda: thread_it(True, self.startDetection))  # 开始检测
        self.pushButton_stopDetection.clicked.connect(self.stopDetection)  # 结束检测
        self.pushButton_readStandard_2.clicked.connect(self.readStandard)  # 导入标准

        # 深度学习检测界面
        # self.pushButton_startDetection_2.clicked.connect(self.startDetection2)
        self.pushButton_startDetection_2.clicked.connect(lambda: thread_it(False, self.startDetection2))
        # 根据选择参考修改flag
        # 检测关节点选择
        self.checkBox_right_elbow.stateChanged.connect(
            lambda: self.checkBoxRecord(self.checkBox_right_elbow, self.checkBoxDict, self.checkBoxDict_2,
                                        'checkBox_right_elbow_flag', 'checkBox_right_elbow_2_flag', 'state'))
        self.checkBox_right_shoulder.stateChanged.connect(
            lambda: self.checkBoxRecord(self.checkBox_right_shoulder, self.checkBoxDict, self.checkBoxDict_2,
                                        'checkBox_right_shoulder_flag', 'checkBox_right_shoulder_2_flag', 'state'))
        self.checkBox_left_elbow.stateChanged.connect(
            lambda: self.checkBoxRecord(self.checkBox_left_elbow, self.checkBoxDict, self.checkBoxDict_2,
                                        'checkBox_left_elbow_flag', 'checkBox_left_elbow_2_flag', 'state'))
        self.checkBox_left_shoulder.stateChanged.connect(
            lambda: self.checkBoxRecord(self.checkBox_left_shoulder, self.checkBoxDict, self.checkBoxDict_2,
                                        'checkBox_left_shoulder_flag', 'checkBox_left_shoulder_2_flag', 'state'))
        self.checkBox_left_hip.stateChanged.connect(
            lambda: self.checkBoxRecord(self.checkBox_left_hip, self.checkBoxDict, self.checkBoxDict_2,
                                        'checkBox_left_hip_flag',
                                        'checkBox_left_hip_2_flag', 'state'))
        self.checkBox_right_hip.stateChanged.connect(
            lambda: self.checkBoxRecord(self.checkBox_right_hip, self.checkBoxDict, self.checkBoxDict_2,
                                        'checkBox_right_hip_flag', 'checkBox_right_hip_2_flag', 'state'))
        self.checkBox_left_knee.stateChanged.connect(
            lambda: self.checkBoxRecord(self.checkBox_left_knee, self.checkBoxDict, self.checkBoxDict_2,
                                        'checkBox_left_knee_flag', 'checkBox_left_knee_2_flag', 'state'))
        self.checkBox_right_knee.stateChanged.connect(
            lambda: self.checkBoxRecord(self.checkBox_right_knee, self.checkBoxDict, self.checkBoxDict_2,
                                        'checkBox_right_knee_flag', 'checkBox_right_knee_2_flag', 'state'))


def thread_it(_bool, func, *args):
    t = threading.Thread(target=func, args=args)  # 调用func函数
    t.setDaemon(_bool)  # False设置为用户线程,True设置守护线程
    # 用户线程和守护线程的区别:
    # 主线程结束后用户线程还会继续运行，主线程结束后，如果没有用户线程，都是守护线程，那么结束（随之而来的是所有的一切烟消云散，包括所有的守护线程）。
    t.start()


# if __name__ == '__main__':
print("进入__name__ == '__main__'")
app = QApplication(sys.argv)
login_ui = LoginWindow()  # 登录界面
login_ui.show()  # 打开登录界面
userPage = UserPageWindow()  # 主界面
# 导入深度学习的模块
import mediapipe_knn.videoprocess as vp
import mediapipe_knn.trainingsetprocess as tp
import mediapipe_knn.videocapture as vc
database.createConnection()  # 创建连接
# database.createTable()#创建数据库内容

# ------------------按钮信号连接-----------------
# 关闭登录界面
login_ui.pushButton_quit.clicked.connect(  # 切换界面到userpage画面
    lambda: {login_ui.close()}
)

sys.exit(app.exec_())
