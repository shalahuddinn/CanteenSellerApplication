#Main Program

import sys
from PyQt5.QtWidgets import QApplication
from MainWindow import MainWindow

if __name__ == '__main__':
    qApplication = QApplication(sys.argv)

    form = MainWindow()
    form.show()
    qApplication.exec_()
