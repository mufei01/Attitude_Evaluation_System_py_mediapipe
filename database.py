# !/usr/bin/python
# -*- coding: utf-8 -*-


from PyQt5.QtSql import QSqlDatabase, QSqlQuery
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *


def createConnection() -> bool:
    db = QSqlDatabase.addDatabase('QSQLITE', 'sqlite1')  # 指定数据库类型
    # 指定SQLite数据库文件名
    db.setDatabaseName(".//userMessage.db")
    if not db.open():
        print('无法建立与数据库的连接')
        return False
    return True


def createTable() -> bool:
    db = QSqlDatabase.database("sqlite1")
    query = QSqlQuery(db)
    success = query.exec_(
        "create table userinfo(username varchar primary key,password varchar,nickname varchar,sex varchar,userdate date,phone varchar)")
    if success:
        print("数据库表创建成功！\n")
        return True
    else:
        print("数据库表创建失败！\n")
        return False


# 用户名匹配
def queryUsername(username) -> bool:
    db = QSqlDatabase.database("sqlite1")  # 建立数据库连接
    if not db.open():
        print("无法建立数据库连接")
        return False
    query = QSqlQuery("select username from userinfo", db)
    rec = query.record()
    while query.next():
        rec = query.record()
        snamecol = rec.indexOf("username")
        value = query.value(snamecol)
        print("username:" + value)
        if value == username:
            print("找到了")
            return True
    return False


# 账号密码匹配
def querypassword(username, password) -> bool:
    db = QSqlDatabase.database("sqlite1")  # 建立数据库连接
    if not db.open():
        print("无法建立数据库连接")
        return False

    S = "select username,password from userinfo where username=%s and password=%s" % (username, password)
    query = QSqlQuery(S, db)
    if not query.exec():  # 执行S的SQL语句
        print("Error: Fail to query table. " + query.lastError())
    while query.next():
        rec = query.record()
        UsernameCol = rec.indexOf("username")  # 获取username列号
        PasswordCol = rec.indexOf("password")  # 获取username列号
        value_username = query.value(UsernameCol)  # 获取值
        value_password = query.value(PasswordCol)
        # print("username"+value_username+"password"+value_password)
        if value_username == username and value_password == password:
            print("密码正确")
            return True
    return False


# 注册
def UserSignUp(username, password) -> bool:
    db = QSqlDatabase.database("sqlite1")  # 建立数据库连接
    if not db.open():
        print("无法建立数据库连接")
        return False
    if not queryUsername(username):
        query = QSqlQuery(db)
        query.prepare("insert into userinfo values(:username, :password)")
        query.bindValue(":username", username)  # 插入数据
        query.bindValue(":password", password)

        success = query.exec_()
        if not success:
            lastError = query.lastError()
            print(lastError.driverText() + "插入失败")
            return False
        print("添加成功")
        return True

    print("添加失败")
    QMessageBox.information(None, "登录", "用户名已存在", QMessageBox.Ok)
    db.close()
    return False


# 更新密码
def updatePassword(username, password) -> bool:
    db = QSqlDatabase.database("sqlite1")  # 建立数据库连接
    if not db.open():
        print("无法建立数据库连接")
        return False
    query = QSqlQuery(db)
    query.prepare("update userinfo set password=? where username=? ")
    query.addBindValue(password)  # 填入新密码
    query.addBindValue(username)

    success = query.exec_()  # 执行
    if not success:
        lastError = query.lastError()
        print(lastError.driverText() + "更新失败")
    return True
