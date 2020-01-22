# Implement the row of a QListWidget with a custom Widget

import json
import urllib.request

from PyQt5 import QtNetwork
from PyQt5.QtCore import QUrl, QSettings, Qt, pyqtSignal
from PyQt5.QtGui import QPixmap
from PyQt5.QtWidgets import (QWidget, QHBoxLayout, QLabel, QPushButton, QVBoxLayout, QMessageBox,
                             QListWidget, QListWidgetItem)

from EntryMenuForm import EntryMenuForm
from MenuItemWidget import MenuItemWidget


class MenuManagerWidget(QWidget):

    launchEditMenuForm = pyqtSignal(MenuItemWidget)

    def __init__(self,):
        super().__init__()
        self.nam = QtNetwork.QNetworkAccessManager()
        self.listMenu = []

        self.setting = QSettings()

        self.mylist = QListWidget()

        self.mylist.setStyleSheet("QListWidget::item { border-bottom: 1px solid gray; }")
        self.mylist.setFocusPolicy(Qt.NoFocus)

        self.refreshButton = QPushButton()
        self.refreshButton.setText("Refresh")
        self.refreshButton.clicked.connect(self.refresh)

        self.manageMenuButton = QPushButton()
        self.manageMenuButton.setText("Add")
        self.manageMenuButton.clicked.connect(self.openEntryMenuForm)

        self.backButton = QPushButton()
        self.backButton.setText("Back")

        hbox = QHBoxLayout()
        hbox.addWidget(self.backButton)
        hbox.addWidget(self.manageMenuButton)
        hbox.addWidget(self.refreshButton)

        widgetTitleLabel = QLabel()
        widgetTitleLabel.setAlignment(Qt.AlignCenter)
        widgetTitleLabel.setText("Menu Manager")

        mainLayout = QVBoxLayout()
        mainLayout.addWidget(widgetTitleLabel)
        mainLayout.addWidget(self.mylist)
        mainLayout.addLayout(hbox)
        self.mylist.show()

        self.setLayout(mainLayout)

    def clear(self):
        self.mylist.clear()
        self.listMenu.clear()

    def refresh(self):
        self.clear()
        self.doRequestMenu()

    def populateList(self):
        self.mylist.clear()

        for menu in self.listMenu:
            # Add to list a new item (item is simply an entry in your list)
            qListWidgetItem = QListWidgetItem(self.mylist)

            self.mylist.addItem(qListWidgetItem)
            # Instanciate a custom widget
            menu.editButton.clicked.connect(lambda checked, menu=menu: self.editMenu(menu))
            qListWidgetItem.setSizeHint(menu.minimumSizeHint())

            # Associate the custom widget to the list entry
            self.mylist.setItemWidget(qListWidgetItem, menu)

    def openEntryMenuForm(self):
        self.launchEditMenuForm.emit(None)

    def editMenu(self, menuItemWidget):
        self.launchEditMenuForm.emit(menuItemWidget)

    def doRequestMenu(self):
        url = self.setting.value("baseURL", "")
        url += "/menu/?sellerID=" + str(self.setting.value("sellerID", ""))
        req = QtNetwork.QNetworkRequest(QUrl(url))

        reply = self.nam.get(req)
        reply.finished.connect(self.handleResponseMenu)

    def handleResponseMenu(self):
        reply = self.sender()

        er = reply.error()

        if er == QtNetwork.QNetworkReply.NoError:

            bytes_string = reply.readAll()
            data = json.loads(str(bytes_string, 'utf-8'))
            
            for menu in data:
                id = menu['id']
                data = urllib.request.urlopen(menu['image']).read()
                image = QPixmap()
                image.loadFromData(data)
                name = menu['name']
                price = menu['price']
                category = menu['category']
                availability = menu['availability']
                qtyAvailable = menu['qtyAvailable']
                qtyOnBooked = menu['qtyOnBooked']

                menuItem = MenuItemWidget(id, image, name, price, category, availability, qtyAvailable, qtyOnBooked)
                self.listMenu.append(menuItem)

            self.populateList()

        else:
            errorMessage = "Error occured: " + str(er) + "\n" + str(reply.errorString())
            QMessageBox.critical(self, "Error Order Detail", errorMessage)
        reply.deleteLater()
