# Implement the row of a QListWidget with a custom Widget

from PyQt5 import QtNetwork
from PyQt5.QtCore import QUrl, QSettings, QRegExp, QFile, QIODevice, QDir, QByteArray, pyqtSignal
from PyQt5.QtGui import QPixmap, QRegExpValidator
from PyQt5.QtNetwork import QNetworkRequest
from PyQt5.QtWidgets import (QWidget, QHBoxLayout, QLabel, QPushButton, QVBoxLayout, QMessageBox, QFileDialog,
                             QCheckBox, QGridLayout, QLineEdit, QRadioButton)


class EntryMenuForm(QWidget):

    close = pyqtSignal()

    def __init__(self):
        super().__init__()

        self.setting = QSettings()

        self.menuItem = None

        self.manager = QtNetwork.QNetworkAccessManager()
        self.filename = ""

        self.nameLabel = QLabel()
        self.nameLabel.setText("Name")
        self.nameLineEdit = QLineEdit()

        self.priceLabel = QLabel()
        self.priceLabel.setText("Price")
        self.priceLineEdit = QLineEdit()
        self.priceLineEdit.setValidator(QRegExpValidator(QRegExp("[0-9_]+")))

        self.categoryLabel = QLabel()
        self.categoryLabel.setText("Category")

        self.foodRadioButton = QRadioButton("Food")
        self.drinkRadioButton = QRadioButton("Drink")

        radioHbox = QHBoxLayout()
        radioHbox.addWidget(self.foodRadioButton)
        radioHbox.addWidget(self.drinkRadioButton)

        self.availabilityLabel = QLabel()
        self.availabilityLabel.setText("Availability")
        self.availabilityCheckBox = QCheckBox()

        self.qtyAvailableLabel = QLabel()
        self.qtyAvailableLabel.setText("Qty Available")
        self.qtyAvailableLineEdit = QLineEdit()
        self.qtyAvailableLineEdit.setValidator(QRegExpValidator(QRegExp("[0-9_]+")))

        self.imageLabel = QLabel()
        self.imagePixmap = QPixmap("images/noimage.png")
        self.imageLabel.setPixmap(self.imagePixmap)
        self.changePictureButton = QPushButton()
        self.changePictureButton.setText("Change Picture")
        self.changePictureButton.clicked.connect(self.selectPicture)

        self.okButton = QPushButton()
        self.okButton.setText("Ok")
        self.okButton.clicked.connect(self.upload)

        self.cancelButton = QPushButton()
        self.cancelButton.setText("Cancel")
        self.cancelButton.clicked.connect(self.closeEntryMenuForm)

        gridLayout = QGridLayout()
        gridLayout.addWidget(self.nameLabel, 0, 0)
        gridLayout.addWidget(self.nameLineEdit, 0, 1)
        gridLayout.addWidget(self.priceLabel, 1, 0)
        gridLayout.addWidget(self.priceLineEdit, 1, 1)
        gridLayout.addWidget(self.categoryLabel, 2, 0)
        gridLayout.addLayout(radioHbox, 2, 1)
        gridLayout.addWidget(self.availabilityLabel, 3, 0)
        gridLayout.addWidget(self.availabilityCheckBox, 3, 1)
        gridLayout.addWidget(self.qtyAvailableLabel, 4, 0)
        gridLayout.addWidget(self.qtyAvailableLineEdit, 4, 1)

        vbox = QVBoxLayout()
        vbox.addWidget(self.imageLabel)
        vbox.addWidget(self.changePictureButton)

        hbox = QHBoxLayout()
        hbox.addWidget(self.cancelButton)
        hbox.addWidget(self.okButton)

        hbox2 = QHBoxLayout()
        hbox2.addLayout(vbox)
        hbox2.addLayout(gridLayout)

        mainLayout = QVBoxLayout()
        mainLayout.addLayout(hbox2)
        mainLayout.addLayout(hbox)

        self.setLayout(mainLayout)

    def setMenuItem(self, menuItem):
        self.filename = ""
        self.menuItem = menuItem
        if self.menuItem is not None:
            self.nameLineEdit.setText(self.menuItem.name)
            self.priceLineEdit.setText(str(self.menuItem.price))
            self.qtyAvailableLineEdit.setText(str(self.menuItem.qtyAvailable))

            if self.menuItem.category == "food":
                self.foodRadioButton.setChecked(True)
            else:
                self.drinkRadioButton.setChecked(True)

            if self.menuItem.availability:
                self.availabilityCheckBox.setChecked(True)
            else:
                self.availabilityCheckBox.setChecked(False)

            self.imageLabel.setPixmap(self.menuItem.image)
        else:
            self.nameLineEdit.clear()
            self.priceLineEdit.clear()
            self.qtyAvailableLineEdit.clear()

            self.foodRadioButton.setChecked(False)
            self.drinkRadioButton.setChecked(False)
            self.availabilityCheckBox.setChecked(False)
            self.imageLabel.setPixmap(self.imagePixmap)

    def closeEntryMenuForm(self):
        self.close.emit()

    def selectPicture(self):
        fname, _ = QFileDialog.getOpenFileName(
            self,
            "Open Image",
            QDir.currentPath(),
            "Image Files (*.png *.jpg *.bmp)"
        )
        if fname:
            pixmap = QPixmap(fname)
            if pixmap.height()!=150 and pixmap.width()!=150:
                QMessageBox.information(self, "Select Picture", "Image size should be 150x150 px!")
                self.selectPicture()
            else:
                self.imageLabel.setPixmap(pixmap)
                self.filename = fname

    def getCategory(self):
        if self.foodRadioButton.isChecked():
            return "food"
        if self.drinkRadioButton.isChecked():
            return "drink"

    # The Upload Method
    # Source: https://stackoverflow.com/a/55132547/7020404
    # Accessed on March 13, 2019 18:08
    def upload(self):
        data = {
            "name": self.nameLineEdit.text(),
            "price": int(self.priceLineEdit.text()),
            "category": self.getCategory(),
            "availability": self.availabilityCheckBox.isChecked(),
            "qtyAvailable": int(self.qtyAvailableLineEdit.text()),
            # "qtyOnBooked": int(self.qtyOnBookedLineEdit.text()),
            "sellerID": str(self.setting.value("sellerID", ""))
        }

        url = self.setting.value("baseURL", "")
        url += "/menu/"

        if self.menuItem is not None:
            url += str(self.menuItem.id) + "/"

        path = self.filename

        files = {"image": path}

        multipart = self.construct_multipart(data, files)
        request = QNetworkRequest(QUrl(url))

        mode = QByteArray()
        if not self.menuItem:
            mode.append("POST")
        else: 
            mode.append("PATCH")


        reply = self.manager.sendCustomRequest(request, mode, multipart)
        reply.finished.connect(self.handleResponseMenu)
        multipart.setParent(reply)

    def handleResponseMenu(self):
        reply = self.sender()
        er = reply.error()
        if er == QtNetwork.QNetworkReply.NoError:
            # bytes_string = reply.readAll()
            # data = json.loads(str(bytes_string, 'utf-8'))
            # print(data)
            QMessageBox.information(self, "Menu", "Upload Berhasil!")
            self.closeEntryMenuForm()


        else:
            errorMessage = "Error occured: " + str(er) + "\n" + str(reply.errorString())
            QMessageBox.critical(self, "Error Add Menu", errorMessage)
        reply.deleteLater()


    def construct_multipart(self, data, files):
        multi_part = QtNetwork.QHttpMultiPart(QtNetwork.QHttpMultiPart.FormDataType)
        for key, value in data.items():
            post_part = QtNetwork.QHttpPart()
            post_part.setHeader(QtNetwork.QNetworkRequest.ContentDispositionHeader,
                "form-data; name=\"{}\"".format(key))
            post_part.setBody(str(value).encode())
            multi_part.append(post_part)
        for field, filepath in  files.items():
            if filepath:
                file = QFile(filepath)
                if not file.open(QIODevice.ReadOnly):
                    break
                post_part = QtNetwork.QHttpPart()
                post_part.setHeader(QtNetwork.QNetworkRequest.ContentDispositionHeader,
                    "form-data; name=\"{}\"; filename=\"{}\"".format(field, file.fileName()))
                post_part.setBodyDevice(file)
                file.setParent(multi_part)
                multi_part.append(post_part)
            else:
                break
        return  multi_part



