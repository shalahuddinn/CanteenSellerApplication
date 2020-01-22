import json

from PyQt5.QtCore import (QUrl, QSettings, pyqtSignal)
from PyQt5.QtGui import QPixmap
from PyQt5.QtNetwork import (QNetworkAccessManager, QNetworkReply, QNetworkRequest)
from PyQt5.QtWidgets import (QLabel, QGridLayout, QPushButton, QWidget, QLineEdit, QVBoxLayout, QHBoxLayout,
                             QMessageBox)
from passlib.hash import pbkdf2_sha256

from OrderManagerWidget import OrderManagerWidget
from SettingWindow import SettingWindow


class HomeWidget(QWidget):
    loginSuccess = pyqtSignal()

    def __init__(self):
        super().__init__()
        self.nam = QNetworkAccessManager()

        logoLabel = QLabel()
        logoPixmap = QPixmap("images/logo.png")
        logoLabel.setPixmap(logoPixmap)
        logoLabel.setFixedSize(logoPixmap.width(), logoPixmap.height())

        logoHBoxLayout = QHBoxLayout()
        logoHBoxLayout.addStretch(1)
        logoHBoxLayout.addWidget(logoLabel)
        logoHBoxLayout.addStretch(1)

        titleLabel = QLabel()
        titleLabel.setText("YOUR TEXT TITLE")

        titleHBoxLayout = QHBoxLayout()
        titleHBoxLayout.addStretch(1)
        titleHBoxLayout.addWidget(titleLabel)
        titleHBoxLayout.addStretch(1)

        usernameLabel = QLabel()
        usernameLabel.setText("Username")
        self.usernameLineEdit = QLineEdit()
        self.usernameLineEdit.returnPressed.connect(self.doRequestSeller)

        passwordLabel = QLabel()
        passwordLabel.setText("Password")
        self.passwordLineEdit = QLineEdit()
        self.passwordLineEdit.setEchoMode(QLineEdit.Password)
        self.passwordLineEdit.returnPressed.connect(self.doRequestSeller)


        self.loginButton = QPushButton("Login")
        self.loginButton.clicked.connect(self.doRequestSeller)
        self.settingButton = QPushButton("Setting")
        self.settingButton.clicked.connect(self.openSettingWindow)


        fieldLayout = QGridLayout()
        fieldLayout.addWidget(usernameLabel, 0, 0)
        fieldLayout.addWidget(self.usernameLineEdit, 0, 1)
        fieldLayout.addWidget(passwordLabel, 1, 0)
        fieldLayout.addWidget(self.passwordLineEdit,1 ,1)

        fieldLayoutHbox = QHBoxLayout()
        fieldLayoutHbox.addStretch(1)
        fieldLayoutHbox.addLayout(fieldLayout)
        fieldLayoutHbox.addStretch(1)


        buttonHBoxLayout = QHBoxLayout()
        buttonHBoxLayout.addStretch(1)
        buttonHBoxLayout.addWidget(self.settingButton)
        buttonHBoxLayout.addWidget(self.loginButton)
        buttonHBoxLayout.addStretch(1)

        vBoxLayout = QVBoxLayout()
        vBoxLayout.addStretch(1)
        vBoxLayout.addLayout(logoHBoxLayout)
        vBoxLayout.addLayout(titleHBoxLayout)
        vBoxLayout.addSpacing(10)
        vBoxLayout.addLayout(fieldLayoutHbox)
        vBoxLayout.addSpacing(5)
        vBoxLayout.addLayout(buttonHBoxLayout)
        vBoxLayout.addStretch(1)

        self.setLayout(vBoxLayout)

    def openSettingWindow(self):
        preferenceWindow = SettingWindow()
        preferenceWindow.exec_()

    # Attempt to do HTTP Request for Seller Model
    def doRequestSeller(self):
        # Check whether the username empty or not
        username = self.usernameLineEdit.text()
        password = self.passwordLineEdit.text()
        if username == "" or password == "" :
            QMessageBox.warning(self, "Login", "Username or Password is Empty")
            return

        setting = QSettings()
        url = setting.value("baseURL", "")
        url += "/seller/?username=" + username

        req = QNetworkRequest(QUrl(url))
        req.setHeader(QNetworkRequest.ContentTypeHeader,
                      "application/x-www-form-urlencoded")

        reply = self.nam.get(req)
        reply.finished.connect(self.handleResponseSeller)

    def handleResponseSeller(self):
        reply = self.sender()
        er = reply.error()
        if er == QNetworkReply.NoError:
            bytes_string = reply.readAll()
            data = json.loads(str(bytes_string, 'utf-8'))

            if len(data)==0:
                QMessageBox.warning(self, "Error Login", "User is not found")
                return
            password = self.passwordLineEdit.text()
            passwordFromServer = data[0]['password']

            if pbkdf2_sha256.verify(password, passwordFromServer):
                QMessageBox.information(self, "Success", "Login Sukses")
                setting = QSettings()
                setting.setValue("sellerID", data[0]['id'])
                self.loginSuccess.emit()
            else:
                QMessageBox.warning(self, "Error Login", "Username or Password doesn't match")
        else:
            errorMessage = "Error occured: " + str(er) + "\n" + str(reply.errorString())
            QMessageBox.critical(self, "Error Seller", errorMessage)
        reply.deleteLater()
