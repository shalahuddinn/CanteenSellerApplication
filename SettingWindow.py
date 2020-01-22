# A screen to set the BASE API URL

from PyQt5.QtCore import QSettings
from PyQt5.QtWidgets import (QLabel, QPushButton, QLineEdit, QGridLayout, QDialog)


class SettingWindow(QDialog):
    def __init__(self):
        super().__init__()
        self.setupUi()

    def setupUi(self):
        self.setWindowTitle('Setting')

        self.baseURL = QLabel()
        self.baseURL.setText("Base API URL")
        self.baseURLLineEdit = QLineEdit()

        #Read settings
        setting = QSettings()
        self.baseURLLineEdit.setText(setting.value("baseURL", ""))

        self.okButton = QPushButton()
        self.okButton.setText("Ok")
        self.okButton.clicked.connect(self.ok)

        layout = QGridLayout()
        layout.addWidget(self.baseURL, 0, 0)
        layout.addWidget(self.baseURLLineEdit, 0, 1)
        layout.addWidget(self.okButton, 1,1)

        self.setLayout(layout)

    def ok(self):
        setting = QSettings()
        setting.setValue("baseURL", self.baseURLLineEdit.text())

        self.close()
