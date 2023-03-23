# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'dialog.ui'
#
# Created by: PyQt5 UI code generator 5.13.2
#
# WARNING! All changes made in this file will be lost!

db_host = '192.168.10.51'   # 'sql_hostname'
db_user = 'tunnel'          # 'sql_username'
db_pass = 'th#3Q@@8$M3rg'   # 'sql_password'
db_name = 'customers'  # 'db_name'
db_port = 3306

ssh_host = '103.121.236.50'      # 'ssh_hostname'
ssh_user = 'arpan'               # 'ssh_username'
ssh_port = 22
ssh_keyfile = "arpan_openssh.ppk"

from PyQt5 import QtCore, QtWidgets
import threading
import paramiko
from sshtunnel import SSHTunnelForwarder
import pymysql
import os

class Ui_Dialog(object):

    m_server = None

    def setupUi(self, Dialog):
        Dialog.setObjectName("Dialog")
        Dialog.resize(379, 418)
        self.txt_user = QtWidgets.QLineEdit(Dialog)
        self.txt_user.setGeometry(QtCore.QRect(80, 10, 151, 20))
        self.txt_user.setObjectName("txt_user")
        self.txt_pass = QtWidgets.QLineEdit(Dialog)
        self.txt_pass.setGeometry(QtCore.QRect(80, 50, 151, 20))
        self.txt_pass.setObjectName("txt_pass")
        self.txt_pass.setEchoMode(QtWidgets.QLineEdit.Password)

        self.label = QtWidgets.QLabel(Dialog)
        self.label.setGeometry(QtCore.QRect(16, 10, 51, 20))
        self.label.setObjectName("label")
        self.label_2 = QtWidgets.QLabel(Dialog)
        self.label_2.setGeometry(QtCore.QRect(16, 50, 51, 20))
        self.label_2.setObjectName("label_2")

        self.btnConnect = QtWidgets.QPushButton(Dialog)
        self.btnConnect.setGeometry(QtCore.QRect(280, 10, 75, 23))
        self.btnConnect.setObjectName("btnConnect")
        self.btnConnect.clicked.connect(self.onBtnConnectClicked)

        self.btnDisconnect = QtWidgets.QPushButton(Dialog)
        self.btnDisconnect.setGeometry(QtCore.QRect(280, 50, 75, 23))
        self.btnDisconnect.setObjectName("btnDisconnect")
        self.btnDisconnect.clicked.connect(self.onBtnDisconnectClicked)

        self.lineEdit = QtWidgets.QLineEdit(Dialog)
        self.lineEdit.setGeometry(QtCore.QRect(20, 90, 291, 20))
        self.lineEdit.setObjectName("lineEdit")
        self.btnOpenkey = QtWidgets.QPushButton(Dialog)
        self.btnOpenkey.setGeometry(QtCore.QRect(325, 90, 31, 23))
        self.btnOpenkey.setObjectName("btnOpenkey")
        self.btnOpenkey.clicked.connect(self.getKeyFile)

        self.txt_log = QtWidgets.QTextBrowser(Dialog)
        self.txt_log.setGeometry(QtCore.QRect(50, 130, 311, 271))
        self.txt_log.setObjectName("txt_log")
        self.label_3 = QtWidgets.QLabel(Dialog)
        self.label_3.setGeometry(QtCore.QRect(20, 130, 21, 16))
        self.label_3.setObjectName("label_3")

        self.retranslateUi(Dialog)
        QtCore.QMetaObject.connectSlotsByName(Dialog)

    def retranslateUi(self, Dialog):
        _translate = QtCore.QCoreApplication.translate
        Dialog.setWindowTitle(_translate("Dialog", "Dialog"))
        self.label.setText(_translate("Dialog", "Username"))
        self.label_2.setText(_translate("Dialog", "Password"))
        self.btnConnect.setText(_translate("Dialog", "Connect"))
        self.btnDisconnect.setText(_translate("Dialog", "Disconnect"))
        self.btnOpenkey.setText(_translate("Dialog", "Bro"))
        self.label_3.setText(_translate("Dialog", "Log"))

    def onBtnConnectClicked(self):
        # self.sshMgr.connect_forwarding(self.txt_user.text(), self.txt_pass.text())
        t = threading.Thread(target=self.connect_forwarding)
        t.start()

    def onBtnDisconnectClicked(self):
        self.disconnect_ssh()
        # t = threading.Thread(target=self.disconnect_ssh)
        # t.start()
        # t.join()

    def log(self, msg):

        t = threading.Thread(target=self.update_log, args=(msg, ))
        t.start()

    def update_log(self, msg):

        self.txt_log.append(msg)

    def connect_forwarding(self):

        self.log("Got in connect_forwarding.")

        _proxy_ip = ""
        _proxy_port = 0
        _proxy_user = ""
        _local_port = 0
        _remote_ip = ""
        _remote_port = 0
        _ssh_file_path = ""
        _file_path_to_run = ""

        ssh_keyfile = self.lineEdit.text()

        try:

            mypkey = paramiko.RSAKey.from_private_key_file(ssh_keyfile)

            with SSHTunnelForwarder(
                    (ssh_host, ssh_port),
                    ssh_username=ssh_user,
                    ssh_pkey=mypkey,
                    remote_bind_address=(db_host, db_port)) as tunnel:

                self.log("Forwarding is set to DB machine.")

                conn = pymysql.connect(host='127.0.0.1', user=db_user,
                                       passwd=db_pass, db=db_name,
                                       port=tunnel.local_bind_port)

                self.log("DB connection success.")

                query = "SELECT * FROM server WHERE user_name = '" + self.txt_user.text() + "';"
                self.log("query : " + query)

                cursor = conn.cursor()
                cursor.execute(query)
                ds = cursor.fetchall()

                if ds == ():
                    self.log("There is not the account for input user.")
                    return False

                sel_row = ds[0]
                if sel_row[9] != self.txt_pass.text():     # column name => user_pass
                    self.log("Password is not correct.")
                    return False

                _proxy_ip = sel_row[0]          # column name => proxy_ip
                _proxy_port = int(sel_row[1])   # column name => proxy_port
                _proxy_user = sel_row[2]        # column name => proxy_user
                _local_port = int(sel_row[3])   # column name => local_port
                _remote_ip = sel_row[4]         # column name => remote_ip
                _remote_port = int(sel_row[5])  # column name => remote_port
                _ssh_file_path = sel_row[14]    # column name => ssh_file_path
                _file_path_to_run = sel_row[15] # column name => file_path_to_run

                self.log("Proxy Server - " + _proxy_ip + ":" + str(_proxy_port) + ":" + _proxy_user)
                self.log("Local Port - " + str(_local_port))
                self.log("Remote - " + _remote_ip + ":" + str(_remote_port))
                self.log("SSH - " + _ssh_file_path)
                self.log("Cmd - " + _file_path_to_run)

                conn.close()

            self.connect_ssh(proxy_server=_proxy_ip, proxy_port=_proxy_port, proxy_user=_proxy_user,
                             local_port=_local_port,
                             remote_ip=_remote_ip, remote_port=_remote_port, ssh_file=_ssh_file_path)

        except Exception as ex:
            self.log(str(ex))
            return False

        os.system(_file_path_to_run)

        return True

    def connect_ssh(self, proxy_server, proxy_port, proxy_user, local_port, remote_ip, remote_port, ssh_file):

        mypkey = paramiko.RSAKey.from_private_key_file(ssh_file)

        self.m_server = SSHTunnelForwarder(
            (proxy_server, proxy_port),
            ssh_username=proxy_user,
            ssh_pkey=mypkey,
            local_bind_address=('127.0.0.1', local_port),
            remote_bind_address=(remote_ip, remote_port))
        self.m_server.start()

    def disconnect_ssh(self):

        if self.m_server != None:
            self.m_server.close()
        else:
            print("None")

    def getKeyFile(self):
        options = QtWidgets.QFileDialog.Options()
        options |= QtWidgets.QFileDialog.DontUseNativeDialog
        fname, _ = QtWidgets.QFileDialog.getOpenFileName(caption='Open file', directory=os.getcwd(),
                                                         filter="SSH key file (*.ppk)", options=options)
        self.lineEdit.setText(fname)