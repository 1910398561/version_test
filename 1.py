# LogWindow.py
# !/usr/bin/env python3
# -*- coding:utf-8 -*-
# Created on 2019年4月10日
# Author: linwy

import sys
import time
import socket
import json
import threading
import File
# from PyQt5 import QtCore
# from PyQt5 import QtCore
# import pyqtGuiLib
# # print(PyQt5)
# print(pyqtGuiLib)
# exit()

from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtWidgets import QMessageBox, QTableView, QVBoxLayout, QHBoxLayout, QHeaderView, QApplication, QFileDialog
from PyQt5.QtGui import QIcon, QColor, QStandardItemModel, QStandardItem
from PyQt5.QtCore import Qt, QPropertyAnimation, QPoint, QTimer, pyqtSignal
from pyqtGuiLib.LogWindow_ui import Ui_Dialog
from pyqtGuiLib.PyQTGUI import FramelessWindow

# 样式
StyleSheet = """
/*标题栏*/
TitleBar {
    background-color: rgb(81, 119, 199);
}

/*最小化最大化关闭按钮通用默认背景*/
#buttonMinimum,#buttonMaximum,#buttonClose {
    border: none;
    background-color: rgb(81, 119, 199);
}

/*悬停*/
#buttonMinimum:hover,#buttonMaximum:hover {
    background-color: rgb(116, 146, 210);
}
#buttonClose:hover {
    color: white;
    background-color: rgb(232, 17, 35);
}

/*鼠标按下不放*/
#buttonMinimum:pressed,#buttonMaximum:pressed {
    background-color: rgb(116, 146, 210);
}
#buttonClose:pressed {
    color: white;
    background-color: rgb(161, 73, 92);
}
"""

MAINWND_HEIGHT = 508
MAINWND_WIDHT = 328
logsocketPort = 8380
logsocketAddress = '127.0.0.1'


class LogDialogClass(QtWidgets.QDialog, Ui_Dialog):
    def __init__(self):
        super(LogDialogClass, self).__init__()
        self.setupUi(self)

        self.model = QStandardItemModel()
        self.model.setHorizontalHeaderLabels(['日志时间', '日志信息'])

        # 实例化表格视图，设置模型为自定义的模型
        self.tableView = QTableView()
        self.tableView.setModel(self.model)

        self.tableView.horizontalHeader().setStretchLastSection(True)
        # self.tableView.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.tableView.setColumnWidth(0, 130)
        self.tableView.verticalHeader().hide()
        self.tableView.horizontalHeader().setDefaultAlignment(QtCore.Qt.AlignLeft)

        # 设置布局 horizontalLayout
        layout = QVBoxLayout(self, spacing=0)
        layout.setContentsMargins(0, 0, 0, 30)
        layout.addWidget(self.tableView)
        """
        layout.addWidget(self.pushButton)
        layout.addWidget(self.pushButton_2)
        layout.addWidget(self.label)
        """
        self.setLayout(layout)

        threadSocket = threading.Thread(target=self.Initsocket, args=())
        threadSocket.start()

        self.pushButton_clrear.clicked.connect(self.ClearAllMessage)
        self.pushButton_export.clicked.connect(self.LogExport)

    def Initsocket(self):
        serverSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        serverSocket.bind((logsocketAddress, logsocketPort))
        serverSocket.listen(5)  # 监听
        print('starting....')

        while True:
            conn, addr = serverSocket.accept()  # 接收客户端信号
            print(conn)
            print('client addr', addr)
            print('ready to read msg')
            client_msg = conn.recv(1024)  # 收消息
            print('client msg: %s' % client_msg)

            decodejson = json.loads(client_msg)
            print(type(decodejson))
            print(decodejson)

            strType = decodejson['type']
            strMsg = decodejson['msg']

            if (strType == 'OutputMessage'):
                self.SendMessage(strMsg)
            elif (strType == 'ClearAllMessage'):
                self.ClearAllMessage()
            elif (strType == 'CloseWindow'):
                self.CloseWindow()
                break

        conn.close()
        serverSocket.close()

        print('The end....')

    def SendMessage(self, msg):
        # 第iRow+1行
        iRow = self.model.rowCount()
        item10 = QStandardItem(time.strftime("%Y/%m/%d %H:%M:%S", time.localtime()))
        self.model.setItem(iRow, 0, item10)
        item11 = QStandardItem(msg)
        self.model.setItem(iRow, 1, item11)

    def ClearAllMessage(self):
        irowCount = self.model.rowCount()
        print(irowCount)
        while (irowCount > 0):
            self.model.removeRow(irowCount - 1)
            irowCount = irowCount - 1

    def CloseWindow(self):
        self.pushButton_close.click()

    def LogExport(self):

        fileName_choose, filetype = QFileDialog.getSaveFileName(self,
                                                                "文件保存",
                                                                "C:/",  # 起始路径
                                                                "All Files (*);;Text Files (*.txt)")

        if fileName_choose == "":
            return

        print("\n你选择要保存的文件为:")
        print(fileName_choose)
        print("文件筛选器类型: ", filetype)

        irowCount = self.model.rowCount()
        icolumn = self.model.columnCount()
        print(irowCount)
        print(icolumn)

        # 获取表头文字
        strLog = ''
        for icol1 in range(icolumn):
            aItem = self.model.horizontalHeaderItem(icol1)  # 获取表头的项数据
            strLog = strLog + aItem.text() + "\t\t\t"  # //以TAB见隔开
            print(strLog)

        strLog = strLog + '\n'
        File.Write(fileName_choose, strLog)

        for irow in range(irowCount):
            str = ""
            for icol in range(icolumn):
                item = self.model.item(irow, icol)
                print('行：', irow)
                print('列：', icol)
                print(item.text())
                str = str + item.text() + ("\t\t")
            File.Append(fileName_choose, str + "\r\n")


def Close():
    print('Close...')


def _show():
    app = QtWidgets.QApplication(sys.argv)
    app.setStyleSheet(StyleSheet)

    mainWnd = FramelessWindow()
    logDlg = LogDialogClass()
    mainWnd.setWindowTitle(logDlg.windowTitle())
    mainWnd.setWindowIcon(QIcon('title.ico'))

    logDlg.pushButton_close.clicked.connect(mainWnd.close)

    mainWnd.setWidget(logDlg)  # 把自己的窗口添加进来
    mainWnd.resize(MAINWND_HEIGHT, MAINWND_WIDHT)

    # 桌面
    _desktop = QApplication.instance().desktop()
    # 窗口初始开始位置
    _startPos = QPoint(
        _desktop.screenGeometry().width() - mainWnd.width() - 5,
        _desktop.screenGeometry().height() - mainWnd.height() - 30
    )
    # 初始化位置到右下角
    mainWnd.move(_startPos)

    mainWnd.show()

    sys.exit(app.exec_())


def _showLogWnd():
    _show()


def _GetClientSocket():
    clientSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  # 指定端口，可根据实际情况设置
    clientSocket.connect((logsocketAddress, logsocketPort))
    return clientSocket


def _Send(msgType, msgInfo=None):
    clientSocket = _GetClientSocket()
    msgJsonData = {'type': msgType, 'msg': msgInfo}
    dumpData = json.dumps(msgJsonData, sort_keys=True)

    clientSocket.send(dumpData.encode('utf-8'))
    clientSocket.close()


def LogStart():
    try:
        logWinthread = threading.Thread(target=_showLogWnd, args=())
        logWinthread.start()
        time.sleep(2)  # 延时2秒确保socket线程启动成功
        return logWinthread
    except Exception as e:
        raise Exception("LogStart error:{0}".format(e))


def LogClose(thread):
    try:
        _Send('CloseWindow')
    except Exception as e:
        raise Exception("LogClose error:{0}".format(e))


def OutputMessage(strMessage):
    try:
        _Send('OutputMessage', strMessage)
    except Exception as e:
        raise Exception("OutputMessage error:{0}".format(e))


def ClearAllMessage():
    try:
        _Send('ClearAllMessage')
    except Exception as e:
        raise Exception("ClearAllMessage error:{0}".format(e))


if __name__ == '__main__':
    logWinthread = LogStart()
    print(logWinthread)
    for i in range(5):
        OutputMessage(str(i))
        time.sleep(1)

    # 清空日志
    time.sleep(1)
    ClearAllMessage()

    # 关闭日志窗口
    time.sleep(1)
    LogClose(logWinthread)
