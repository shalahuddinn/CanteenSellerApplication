# Implement the row of a QListWidget with a custom Widget
# Source: https://stackoverflow.com/questions/14068823/how-to-create-filters-for-qtableview-in-pyqt/14075797#14075797
# Accessed on Aug 1, 2019

import datetime
import json
import urllib.request

from PyQt5 import QtNetwork
from PyQt5.QtCore import QUrl, QSettings, Qt, QRegExp, QSignalMapper, QPoint, QSortFilterProxyModel, QFile
from PyQt5.QtGui import QPixmap, QStandardItemModel, QStandardItem
from PyQt5.QtWidgets import (QWidget, QHBoxLayout, QLabel, QPushButton, QVBoxLayout, QMessageBox, QHeaderView,
                             QListWidget, QListWidgetItem, QTableWidget, QTableWidgetItem, QLineEdit, QTableView,
                             QComboBox, QAction, QMenu, QFileDialog)

from HelperMethod import formatRupiah
from MenuManagerWidget import MenuManagerWidget


class HistoryManagerWidget(QWidget):

    def __init__(self):
        super().__init__()

        self.listHistory = []
        self.nam = QtNetwork.QNetworkAccessManager()

        self.setting = QSettings()

        self.searchLineEdit = QLineEdit()
        self.tableView = QTableView()
        self.columnComboBox = QComboBox()
        self.searchLabel = QLabel()
        self.searchLabel.setText("Filter")

        self.model = QStandardItemModel(self)

        searchHbox = QHBoxLayout()
        searchHbox.addWidget(self.searchLabel)
        searchHbox.addWidget(self.searchLineEdit)
        searchHbox.addWidget(self.columnComboBox)

        self.header = "Order ID;Order Status;Card ID;Menu ID;Menu Name;Price;Qty;" \
                 "Item Status;Table Number;Order Time;Modified Time".split(";")
        self.model.setHorizontalHeaderLabels(self.header)
        self.tableView.horizontalHeader().setStretchLastSection(True)

        hboxLayout = QHBoxLayout()
        self.backButton = QPushButton()
        self.backButton.setText("Back")

        self.refreshButton = QPushButton()
        self.refreshButton.setText("Refresh")
        self.refreshButton.clicked.connect(self.refresh)

        self.saveCSVButton = QPushButton()
        self.saveCSVButton.setText("Save as CSV")
        self.saveCSVButton.clicked.connect(self.saveCSV)

        hboxLayout.addWidget(self.backButton)
        hboxLayout.addWidget(self.refreshButton)
        hboxLayout.addWidget(self.saveCSVButton)

        widgetTitleLabel = QLabel()
        widgetTitleLabel.setAlignment(Qt.AlignCenter)
        widgetTitleLabel.setText("History Manager")

        mainLayout = QVBoxLayout()
        mainLayout.addWidget(widgetTitleLabel)
        mainLayout.addLayout(searchHbox)
        mainLayout.addWidget(self.tableView)
        mainLayout.addLayout(hboxLayout)

        self.proxy = QSortFilterProxyModel(self)
        self.proxy.setSourceModel(self.model)

        self.tableView.setModel(self.proxy)
        self.columnComboBox.addItems(self.header)

        self.searchLineEdit.textChanged.connect(self.on_lineEdit_textChanged)
        self.columnComboBox.currentIndexChanged.connect(self.on_comboBox_currentIndexChanged)

        self.horizontalHeader = self.tableView.horizontalHeader()

        self.setLayout(mainLayout)

    def saveCSV(self):
        data = ""
        rows = self.model.rowCount()
        columns = self.model.columnCount()

        if rows>0:
            for title in self.header:
                data += title
                data += ","
            data += "\n"
            for i in range(rows):
                for j in range(columns):
                    index = self.model.index(i,j)
                    # print(str(self.model.data(index)))
                    data += str(self.model.data(index))
                    data += ","
                data += "\n"

            name, _ = QFileDialog.getSaveFileName(self, 'Save File', "History SELFO.csv", "csv(*.csv)")
            if name:
                file = open(name, 'w')
                file.write(data)
                file.close()
        else:
            QMessageBox.critical(self, "Error", "No Data")

    def clear(self):
        self.listHistory.clear()
        self.model.clear()
        self.model.setHorizontalHeaderLabels(self.header)

    def refresh(self):
        self.clear()
        self.doRequestOrderDetail()

    def populateList(self):
        for rowName in range(len(self.listHistory)):
            self.model.invisibleRootItem().appendRow(
                [QStandardItem("{}".format(self.listHistory[rowName][column]))
                 for column in range(len(self.header))
                 ]
            )
        self.tableView.resizeColumnsToContents()

    def closeHistoryManager(self):
        self.mainWindow.stackedWidget.removeWidget(self)

    def doRequestOrderDetail(self):
        url = self.setting.value("baseURL", "")
        url += "/orderdetail/?sellerID=" + str(self.setting.value("sellerID", "")) \
               # + "&itemStatus=" + "placed"
        req = QtNetwork.QNetworkRequest(QUrl(url))

        reply = self.nam.get(req)
        reply.finished.connect(self.handleResponseOrderDetail)

    def handleResponseOrderDetail(self):
        reply = self.sender()

        er = reply.error()

        if er == QtNetwork.QNetworkReply.NoError:

            bytes_string = reply.readAll()
            data = json.loads(str(bytes_string, 'utf-8'))
            # print(data)

            for history in data:
                # id = history['id']
                orderID = history['orderID']
                orderStatus = history['orderStatus']
                cardID = history['cardID']
                # sellerID = history['sellerID']
                menuID = history['menuID']
                menuName = history['menuName']
                itemStatus = history['itemStatus']
                price = formatRupiah(history['price'])
                qty = history['qty']
                tableNumber = history['tableNumber']
                rawOrderTime = history['orderTime']
                orderTime = datetime.datetime.strptime(
                    rawOrderTime, "%Y-%m-%dT%H:%M:%S.%f+07:00").strftime("%d %b %Y %H:%M:%S")
                rawModifiedTime = history['modifiedTime']
                if rawModifiedTime is not None:
                    modifiedTime = datetime.datetime.strptime(
                        rawModifiedTime, "%Y-%m-%dT%H:%M:%S.%f+07:00").strftime("%d %b %Y %H:%M:%S")
                else:
                    modifiedTime = "null"
                historyItem = [orderID, orderStatus, cardID, menuID, menuName, price, qty, itemStatus, tableNumber, orderTime, modifiedTime]
                self.listHistory.append(historyItem)

            self.populateList()

        else:
            errorMessage = "Error occured: " + str(er) + "\n" + str(reply.errorString())
            QMessageBox.critical(self, "Error Order Detail", errorMessage)
        reply.deleteLater()

    def on_view_horizontalHeader_sectionClicked(self, logicalIndex):
        self.logicalIndex   = logicalIndex
        self.menuValues     = QMenu(self)
        self.signalMapper   = QSignalMapper(self)

        self.columnComboBox.blockSignals(True)
        self.columnComboBox.setCurrentIndex(self.logicalIndex)
        self.columnComboBox.blockSignals(True)

        valuesUnique = [    self.model.item(row, self.logicalIndex).text()
                            for row in range(self.model.rowCount())
                            ]

        actionAll = QAction("All", self)
        actionAll.triggered.connect(self.on_actionAll_triggered)
        self.menuValues.addAction(actionAll)
        self.menuValues.addSeparator()

        for actionNumber, actionName in enumerate(sorted(list(set(valuesUnique)))):
            action = QAction(actionName, self)
            self.signalMapper.setMapping(action, actionNumber)
            action.triggered.connect(self.signalMapper.map)
            self.menuValues.addAction(action)

        self.signalMapper.mapped.connect(self.on_signalMapper_mapped)

        headerPos = self.tableView.mapToGlobal(self.horizontalHeader.pos())

        posY = headerPos.y() + self.horizontalHeader.height()
        posX = headerPos.x() + self.horizontalHeader.sectionPosition(self.logicalIndex)

        self.menuValues.exec_(QPoint(posX, posY))

    def on_actionAll_triggered(self):
        filterColumn = self.logicalIndex
        filterString = QRegExp(  "",
                                        Qt.CaseInsensitive,
                                        QRegExp.RegExp
                                        )

        self.proxy.setFilterRegExp(filterString)
        self.proxy.setFilterKeyColumn(filterColumn)

    def on_signalMapper_mapped(self, i):
        stringAction = self.signalMapper.mapping(i).text()
        filterColumn = self.logicalIndex
        filterString = QRegExp(  stringAction,
                                        Qt.CaseSensitive,
                                        QRegExp.FixedString
                                        )

        self.proxy.setFilterRegExp(filterString)
        self.proxy.setFilterKeyColumn(filterColumn)

    def on_lineEdit_textChanged(self, text):
        search = QRegExp(    text,
                                    Qt.CaseInsensitive,
                                    QRegExp.RegExp
                                    )

        self.proxy.setFilterRegExp(search)

    def on_comboBox_currentIndexChanged(self, index):
        self.proxy.setFilterKeyColumn(index)
