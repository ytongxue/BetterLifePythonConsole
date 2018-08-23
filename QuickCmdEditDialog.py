from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import QTimer
from PyQt5.QtCore import pyqtSlot, pyqtSignal, QObject
from util import printToShell

class QuickCmdEditDialog(QtWidgets.QDialog):
    finished = pyqtSignal([str, str, str])
    def __init__(self, *args):
        super().__init__(*args)
        self.mode = ""

        self.setModal(True)
        font = QtGui.QFont()
        font.setFamily("DejaVu Sans Mono")
        font.setPointSize(12)
        self.setFont(font)

        self.setFixedSize(500, 460)

        self.labelQuickCmdName = QtWidgets.QLabel(self)
        self.labelQuickCmdName.setGeometry(QtCore.QRect(20, 20, 60, 30))
        self.labelQuickCmdName.setText("Name:")

        self.lineEditQuickCmdName = QtWidgets.QLineEdit(self)
        self.lineEditQuickCmdName.setGeometry(QtCore.QRect(100, 20, 350, 30))

        self.labelQuickCmdSourceCode = QtWidgets.QLabel(self)
        self.labelQuickCmdSourceCode.setGeometry(QtCore.QRect(20, 60, 300, 30))
        self.labelQuickCmdSourceCode.setText("Source Code:")

        self.plainTextEditSourceCode = QtWidgets.QPlainTextEdit(self)
        self.plainTextEditSourceCode.setGeometry(QtCore.QRect(20, 100, 460, 280))
        
        self.buttonOk = QtWidgets.QPushButton(self)
        self.buttonOk.setGeometry(QtCore.QRect(190, 400, 80, 40))
        self.buttonOk.clicked.connect(self.onOkButtonClicked)
        self.buttonOk.setText("OK")
    def onOkButtonClicked(self):
        name = self.lineEditQuickCmdName.text()
        sourceCode = self.plainTextEditSourceCode.toPlainText()
        if not name or not sourceCode:
            self.messageBox = QtWidgets.QMessageBox(self)
            if not name:
                self.messageBox.setText("Name cannot be empty")
            elif not sourceCode:
                self.messageBox.setText("source code cannot be empty")
            self.messageBox.open()
        else:
            self.finished.emit(self.mode, name, sourceCode)
            self.accept()
    def setMode(self, mode):
        self.mode = mode
    def setCmdName(self, name):
        self.lineEditQuickCmdName.setText(name)
    def setSourceCode(self, code):
        self.plainTextEditSourceCode.setPlainText(code)
