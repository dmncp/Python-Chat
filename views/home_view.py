# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file '.\resources\home.ui'
#
# Created by: PyQt5 UI code generator 5.15.2
#
# WARNING: Any manual changes made to this file will be lost when pyuic5 is
# run again.  Do not edit this file unless you know what you are doing.

from PyQt5 import QtCore, QtGui, QtWidgets


class HomeWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super(HomeWindow, self).__init__()
        self.setupUi()

    def setupUi(self):
        self.setObjectName("MainWindow")
        self.resize(353, 201)
        self.centralwidget = QtWidgets.QWidget(self)
        self.centralwidget.setObjectName("centralwidget")
        self.welcome_label = QtWidgets.QLabel(self.centralwidget)
        self.welcome_label.setGeometry(QtCore.QRect(10, 0, 331, 41))
        font = QtGui.QFont()
        font.setPointSize(16)
        font.setBold(True)
        font.setWeight(75)
        self.welcome_label.setFont(font)
        self.welcome_label.setObjectName("welcome_label")
        self.nick_value = QtWidgets.QTextEdit(self.centralwidget)
        self.nick_value.setGeometry(QtCore.QRect(10, 80, 331, 51))
        self.nick_value.setObjectName("nick_value")
        self.nick_label = QtWidgets.QLabel(self.centralwidget)
        self.nick_label.setGeometry(QtCore.QRect(10, 40, 141, 41))
        font = QtGui.QFont()
        font.setPointSize(12)
        font.setBold(True)
        font.setWeight(75)
        self.nick_label.setFont(font)
        self.nick_label.setObjectName("nick_label")
        self.close_btn = QtWidgets.QPushButton(self.centralwidget)
        self.close_btn.setGeometry(QtCore.QRect(60, 140, 111, 41))
        font = QtGui.QFont()
        font.setPointSize(12)
        font.setBold(True)
        font.setWeight(75)
        self.close_btn.setFont(font)
        self.close_btn.setObjectName("close_btn")
        self.next_btn = QtWidgets.QPushButton(self.centralwidget)
        self.next_btn.setGeometry(QtCore.QRect(180, 140, 111, 41))
        font = QtGui.QFont()
        font.setPointSize(12)
        font.setBold(True)
        font.setWeight(75)
        self.next_btn.setFont(font)
        self.next_btn.setObjectName("next_btn")
        self.setCentralWidget(self.centralwidget)
        self.statusbar = QtWidgets.QStatusBar(self)
        self.statusbar.setObjectName("statusbar")
        self.setStatusBar(self.statusbar)

        self.retranslateUi(self)
        QtCore.QMetaObject.connectSlotsByName(self)

    def retranslateUi(self, HomeWindow):
        _translate = QtCore.QCoreApplication.translate
        HomeWindow.setWindowTitle(_translate("HomeWindow", "HomeWindow"))
        self.welcome_label.setText(_translate("HomeWindow", "Witaj w komunikatorze Python"))
        self.nick_label.setText(_translate("HomeWindow", "Podaj swój nick:"))
        self.close_btn.setText(_translate("HomeWindow", "Zamknij"))
        self.next_btn.setText(_translate("HomeWindow", "Dalej"))

    def validate(self):
        if self.nick_value.toPlainText():
            return self.nick_value.toPlainText()
        else:
            new_text = 'Musisz podać nick, żeby kontynuować'
            self.nick_label.resize(350, 40)
            self.nick_label.setStyleSheet('color: red')
            self.nick_label.setText(new_text)
            return False
