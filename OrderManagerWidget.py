# Implement the row of a QListWidget with a custom Widget

import datetime
import json
import urllib.request

from PyQt5 import QtNetwork
from PyQt5.QtCore import QUrl, QSettings, QByteArray, Qt
from PyQt5.QtGui import QPixmap
from PyQt5.QtWidgets import (QWidget, QHBoxLayout, QLabel, QPushButton, QVBoxLayout, QMessageBox,
                             QListWidget, QListWidgetItem)

from HelperMethod import formatRupiah
from MenuManagerWidget import MenuManagerWidget
from HistoryManagerWidget import HistoryManagerWidget


class OrderManagerWidget(QWidget):

    def __init__(self):
        super().__init__()

        self.listOrder = []
        self.nam = QtNetwork.QNetworkAccessManager()


        self.setting = QSettings()

        self.mylist = QListWidget()
        self.mylist.setStyleSheet("QListWidget::item { border-bottom: 1px solid gray; }")
        self.mylist.setFocusPolicy(Qt.NoFocus)

        hboxLayout = QHBoxLayout()
        self.logOutButton = QPushButton()
        self.logOutButton.setText("Log Out")

        self.manageMenuButton = QPushButton()
        self.manageMenuButton.setText("Manage Menu")

        self.historyMenuButton = QPushButton()
        self.historyMenuButton.setText("History")

        self.refreshButton = QPushButton()
        self.refreshButton.setText("Refresh")
        self.refreshButton.clicked.connect(self.refresh)

        hboxLayout.addWidget(self.logOutButton)
        hboxLayout.addWidget(self.manageMenuButton)
        hboxLayout.addWidget(self.historyMenuButton)
        hboxLayout.addWidget(self.refreshButton)

        widgetTitleLabel = QLabel()
        widgetTitleLabel.setAlignment(Qt.AlignCenter)
        widgetTitleLabel.setText("Order Manager")

        mainLayout = QVBoxLayout()
        mainLayout.addWidget(widgetTitleLabel)
        mainLayout.addWidget(self.mylist)
        mainLayout.addLayout(hboxLayout)

        self.setLayout(mainLayout)

    def clear(self):
        self.listOrder.clear()
        self.mylist.clear()

    def refresh(self):
        self.clear()
        self.doRequestOrderDetail()

    def populateList(self):
        self.mylist.clear()

        for order in self.listOrder:
            # Add to list a new item (item is simply an entry in your list)
            qListWidgetItem = QListWidgetItem(self.mylist)

            self.mylist.addItem(qListWidgetItem)
            # Instanciate a custom widget
            order.doneButton.clicked.connect(lambda checked, order=order: self.confirmUpdateItemStatus(order, "done"))
            order.rejectButton.clicked.connect(lambda checked, order=order: self.confirmUpdateItemStatus(order, "reject"))
            qListWidgetItem.setSizeHint(order.minimumSizeHint())

            # Associate the custom widget to the list entry
            self.mylist.setItemWidget(qListWidgetItem, order)

    def confirmUpdateItemStatus(self, order, status):
        reply = QMessageBox.question(self, "Update Item Status", "Are you sure to {}?".format(status),
                                     QMessageBox.Yes|QMessageBox.No)
        if reply == QMessageBox.Yes:
            self.doRequestItemStatus(order, status)

    def doRequestItemStatus(self, order, status):
        # orderData = []
        temp = {}
        temp['orderID'] = order.orderID
        temp['sellerID'] = int(self.setting.value("sellerID", ""))
        temp['menuID'] = order.menuID
        temp['price'] = order.price
        temp['qty'] = order.qty
        temp['tableNumber'] = order.tableNumber
        temp['itemStatus'] = status

        data = QByteArray()
        data.append(json.dumps(temp))

        setting = QSettings()
        url = setting.value("baseURL", "")
        url += "/orderdetail/" + str(order.id) + "/"

        req = QtNetwork.QNetworkRequest(QUrl(url))
        req.setHeader(QtNetwork.QNetworkRequest.ContentTypeHeader,
                      "application/json")

        reply = self.nam.put(req, data)
        reply.finished.connect(self.handleResponseItemStatus)

    def handleResponseItemStatus(self):
        reply = self.sender()
        er = reply.error()
        if er == QtNetwork.QNetworkReply.NoError:
            QMessageBox.information(self, "Update Item Status", "Success!")
        else:
            errorMessage = "Error occured: " + str(er) + "\n" + str(reply.errorString())
            QMessageBox.critical(self, "Error Done", errorMessage)
        reply.deleteLater()
        self.refresh()

    def doRequestOrderDetail(self):

        url = self.setting.value("baseURL", "")
        url += "/orderdetail/?sellerID=" + str(self.setting.value("sellerID", "")) + "&itemStatus=" + "placed"
        req = QtNetwork.QNetworkRequest(QUrl(url))

        reply = self.nam.get(req)
        reply.finished.connect(self.handleResponseOrderDetail)

    def handleResponseOrderDetail(self):
        reply = self.sender()

        er = reply.error()

        if er == QtNetwork.QNetworkReply.NoError:

            bytes_string = reply.readAll()
            data = json.loads(str(bytes_string, 'utf-8'))

            for order in data:
                id = order['id']
                orderID = order['orderID']
                menuID = order['menuID']
                menuName = order['menuName']
                data = urllib.request.urlopen(order['image']).read()
                image = QPixmap()
                image.loadFromData(data)
                price = order['price']
                qty = order['qty']
                tableNumber = order['tableNumber']
                rawOrderTime = order['orderTime']
                orderTime = datetime.datetime.strptime(rawOrderTime, "%Y-%m-%dT%H:%M:%S.%f+07:00")
                orderStatus = order['orderStatus']
                if orderStatus == "paid":
                    orderItem = OrderItemWidget(id, orderID, menuID, menuName, image, price, qty, tableNumber, orderTime)
                    self.listOrder.append(orderItem)

            self.populateList()

        else:
            errorMessage = "Error occured: "+ str(er) + "\n" + str(reply.errorString())
            QMessageBox.critical(self, "Error Order Detail", errorMessage)
        reply.deleteLater()


class OrderItemWidget(QWidget):
    def __init__(self, id, orderID, menuID, menuName, image, price, qty, tableNumber, orderTime):
        super().__init__()

        self.id = id
        self.orderID = orderID
        self.menuID = menuID
        self.menuName = menuName
        self.image = image
        self.price = price
        self.qty = qty
        self.tableNumber = tableNumber
        self.orderTime = orderTime

        self.orderIDLabel = QLabel()
        self.orderIDLabel.setText("Order ID: " + str(self.orderID))

        self.menuIDNameLabel = QLabel()
        self.menuIDNameLabel.setText("ID-Name: " + str(self.menuID) + "-" + self.menuName)

        self.imageLabel = QLabel()
        self.imageLabel.setPixmap(self.image)

        self.priceLabel = QLabel()
        self.priceLabel.setText("Price: " + formatRupiah(price))

        self.qtyLabel = QLabel()
        self.qtyLabel.setText("Qty: " + str(self.qty))

        self.tableNumberLabel = QLabel()
        self.tableNumberLabel.setText("Table: " + str(self.tableNumber))

        self.orderTimeLabel = QLabel()
        self.orderTimeLabel.setText("Order Time: " +  self.orderTime.strftime("%d %b %Y %H:%M:%S"))

        self.doneButton = QPushButton("Done")
        self.rejectButton = QPushButton("Reject")

        self.vbox = QVBoxLayout()
        self.vbox.addWidget(self.orderIDLabel)
        self.vbox.addWidget(self.menuIDNameLabel)
        self.vbox.addWidget(self.priceLabel)

        self.hbox = QHBoxLayout()

        self.vbox2 = QVBoxLayout()
        self.vbox2.addWidget(self.orderTimeLabel)
        self.vbox2.addWidget(self.tableNumberLabel)
        self.vbox2.addWidget(self.qtyLabel)

        self.vbox3 = QVBoxLayout()
        self.vbox3.addWidget(self.doneButton)
        self.vbox3.addWidget(self.rejectButton)

        self.hbox.addWidget(self.imageLabel)
        self.hbox.addLayout(self.vbox)
        self.hbox.addLayout(self.vbox2)
        self.hbox.addLayout(self.vbox3)

        self.setLayout(self.hbox)

