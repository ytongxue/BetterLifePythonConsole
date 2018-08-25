from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import QTimer
from PyQt5.QtCore import pyqtSlot, pyqtSignal, QObject
from util import printToShell

class UserInputDialog(QtWidgets.QDialog):
    def __init__(self, *args):
        super().__init__(*args)
        self.userInputValue = None

        self.setModal(True)
        font = QtGui.QFont()
        font.setFamily("DejaVu Sans Mono")
        font.setPointSize(12)
        self.setFont(font)

        self.setFixedSize(400, 160)

        self.labelHint = QtWidgets.QLabel(self)
        self.labelHint.setGeometry(QtCore.QRect(20, 20, 360, 30))
        self.labelHint.setText("")

        self.lineEditValue = QtWidgets.QLineEdit(self)
        self.lineEditValue.setGeometry(QtCore.QRect(20, 60, 360, 30))

        self.buttonOk = QtWidgets.QPushButton(self)
        self.buttonOk.setGeometry(QtCore.QRect(160, 100, 80, 40))
        self.buttonOk.setText("OK")

        self.buttonOk.clicked.connect(self.onOkButtonClicked)

    def onOkButtonClicked(self):
        self.userInputValue = self.lineEditValue.text()
        self.accept()

    def setHint(self, text):
        self.labelHint.setText(text)
