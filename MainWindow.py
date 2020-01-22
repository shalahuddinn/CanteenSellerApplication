# Main File
# Control the Widget Flow

from PyQt5.Qt import QApplication
from PyQt5.QtCore import QCoreApplication, QSize
from PyQt5.QtGui import QFont
from PyQt5.QtWidgets import QMainWindow, QStackedWidget

from HomeWidget import HomeWidget
from MenuManagerWidget import MenuManagerWidget
from HistoryManagerWidget import HistoryManagerWidget
from OrderManagerWidget import  OrderManagerWidget
from EntryMenuForm import EntryMenuForm


class MainWindow(QMainWindow):

    Home = 0
    OrderManager = 1
    MenuManager = 2
    HistoryManager = 3
    EntryMenu = 4

    def __init__(self):
        super().__init__()

        #Init QSetting
        QCoreApplication.setOrganizationName("YOUR_ORGANIZATION_NAME")
        QCoreApplication.setOrganizationDomain("YOUR_ORGANIZATION_DOMAIN")
        QCoreApplication.setApplicationName("YOUR_APPLICATION_NAME")
        font = QFont("Arial", 18, QFont.Normal)
        QApplication.setFont(font)

        # Setup UI
        self.resize(800, 600)
        # self.showFullScreen()

        self.centralWidget = QStackedWidget()
        self.setCentralWidget(self.centralWidget)

        self.homeWidget = HomeWidget()
        self.orderManagerWidget = OrderManagerWidget()
        self.menuManagerWidget = MenuManagerWidget()
        self.historyManagerWidget = HistoryManagerWidget()
        self.entryMenuWidget = EntryMenuForm()

        self.setupNavigation()
        
    def setupNavigation(self):
        self.centralWidget.addWidget(self.homeWidget)
        self.centralWidget.addWidget(self.orderManagerWidget)
        self.centralWidget.addWidget(self.menuManagerWidget)
        self.centralWidget.addWidget(self.historyManagerWidget)
        self.centralWidget.addWidget(self.entryMenuWidget)

        self.centralWidget.setCurrentIndex(self.Home)

        self.homeWidget.loginSuccess.connect(self.goToOrderManager)

        self.orderManagerWidget.logOutButton.clicked.connect(self.goToHome)
        self.orderManagerWidget.manageMenuButton.clicked.connect(self.goToMenuManager)
        self.orderManagerWidget.historyMenuButton.clicked.connect(self.goToHistoryManager)

        self.menuManagerWidget.backButton.clicked.connect(self.goToOrderManager)
        self.menuManagerWidget.launchEditMenuForm.connect(self.goToEntryMenu)

        self.historyManagerWidget.backButton.clicked.connect(self.goToOrderManager)

        self.entryMenuWidget.close.connect(self.goToMenuManager)

    def goToEntryMenu(self, menuItem):
        self.entryMenuWidget.setMenuItem(menuItem)
        self.centralWidget.setCurrentIndex(self.EntryMenu)

    def goToHome(self):
        self.historyManagerWidget.clear()
        self.orderManagerWidget.clear()
        self.menuManagerWidget.clear()
        self.centralWidget.setCurrentIndex(self.Home)

    def goToOrderManager(self):
        self.centralWidget.setCurrentIndex(self.OrderManager)
        self.orderManagerWidget.refresh()

    def goToMenuManager(self):
        self.centralWidget.setCurrentIndex(self.MenuManager)
        self.menuManagerWidget.refresh()

    def goToHistoryManager(self):
        self.centralWidget.setCurrentIndex(self.HistoryManager)
        self.historyManagerWidget.refresh()




