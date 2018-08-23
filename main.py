#! /usr/bin/python3

"""
  A simple dummy console wrapper written by YangDingpeng (ytongxue@gmail.com)

  Codes are a little bit messy.

  All this script does is handling some GUI issue incluing some special keys,
and passing the source code to InterativeConsole, or exec().

  This could be useful if you wanna embed a console into your PyQt5 application.
"""
#! /usr/bin/python3

# standard modules
import sys
import os
import traceback
import glob

from util import printToShell

# PyQt-related
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import QTimer
from PyQt5.QtCore import pyqtSlot, QObject
from PyQt5.QtWidgets import QApplication, QMainWindow
from ConsoleWidget import ConsoleWidget
from CmdButtonListWidget import CmdButtonListWidget, CmdButtonListWidgetItem

class MyConsoleUI(QObject):
    def __init__(self):
        super().__init__()
    def setupUi(self, mainWindow):
        self.mainWindow = mainWindow
        mainWindow.setObjectName("MainWindow")
        mainWindow.setFixedSize(1200, 600)
        font = QtGui.QFont()
        font.setFamily("DejaVu Sans Mono")
        font.setPointSize(12)
        mainWindow.setFont(font)
        self.centralwidget = QtWidgets.QWidget(mainWindow)
        self.centralwidget.setObjectName("centralwidget")
        
        self.buttonRunScript = QtWidgets.QPushButton(self.centralwidget)
        self.buttonRunScript.setIcon(QtGui.QIcon(os.path.join('icon', 'run_script.png')))
        self.buttonRunScript.setIconSize(QtCore.QSize(40, 40))
        self.buttonRunScript.setGeometry(QtCore.QRect(20, 20, 60, 60))
        self.buttonRunScript.clicked.connect(self.onRunScriptButtonClicked)
        
        self.consoleWidget = ConsoleWidget(self.centralwidget)
        self.consoleWidget.setGeometry(QtCore.QRect(10, 100, 780, 480))
        self.consoleWidget.setObjectName("ConsoleWidget")
        mainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QtWidgets.QMenuBar(mainWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 800, 26))
        self.menubar.setObjectName("menubar")
        mainWindow.setMenuBar(self.menubar)
        self.statusbar = QtWidgets.QStatusBar(mainWindow)
        self.statusbar.setObjectName("statusbar")
        mainWindow.setStatusBar(self.statusbar)

        self.cmdButtonListWidget = CmdButtonListWidget(mainWindow)
        self.cmdButtonListWidget.setGeometry(QtCore.QRect(820, 100, 350, 480))
        self.cmdButtonListWidget.itemDoubleClicked.connect(self.onCmdButtonClicked)
        self.loadCmdButtons()

        self.retranslateUi(mainWindow)
        QtCore.QMetaObject.connectSlotsByName(mainWindow)
        printToShell("ready")
        self.timer = QTimer()
        self.timer.timeout.connect(self.autorun)
        self.timer.setSingleShot(True)
        self.timer.start(1)
    def onCmdButtonClicked(self, cmdButtonItem):
        print(cmdButtonItem)
        action = cmdButtonItem.action
        if action:
            self.consoleWidget.runSourceCode(action)
    def loadCmdButtons(self):
        cmds = [
            {
                "name": "sayHello",
                "action": """print("hello")"""
            },
            {
                "name": "sayGoodBye",
                "action": """print("Good bye")"""
            },
        ]
        for cmd in cmds:
            cmdButton = CmdButtonListWidgetItem(self.cmdButtonListWidget)
            cmdButton.name = cmd["name"]
            cmdButton.action = cmd["action"]
            self.cmdButtonListWidget.addItem(cmdButton)

    def retranslateUi(self, mainWindow):
        _translate = QtCore.QCoreApplication.translate
        mainWindow.setWindowTitle(_translate("MainWindow", "Better Life"))

    def setConsole(self, console):
        self.console = console
        self.consoleWidget.setConsole(console)

    def onRunScriptButtonClicked(self):
        if self.consoleWidget.scriptRunning: return
        self.fileDialog = QtWidgets.QFileDialog(self.mainWindow)
        self.fileDialog.setWindowTitle("Select script to run")
        self.fileDialog.setAcceptMode(QtWidgets.QFileDialog.AcceptOpen)
        self.fileDialog.setFileMode(QtWidgets.QFileDialog.ExistingFile)
        self.fileDialog.setModal(True)
        self.fileDialog.setNameFilter("Python Script(*.py)")
        self.fileDialog.fileSelected.connect(self.onScriptSelected)
        self.fileDialog.open()
    def onScriptSelected(self, scriptPath):
        printToShell("script:", scriptPath)
        self.consoleWidget.runScript(scriptPath)
    def autorun(self):
        """
        scan the .py file in autorun/ directory and run them one by one
        """
        printToShell("[autorun]")
        scriptList = glob.glob(os.path.join("autorun", "*.py"))
        printToShell("scriptList:", scriptList)
        for script in scriptList:
            self.consoleWidget.runScript(script)
        printToShell("scope:", self.consoleWidget.console.locals)
        printToShell("[MyConsoleUI] scope id:", id(self.consoleWidget.console.locals))
scope = {}
scope["__builtins__"] = globals()["__builtins__"]

app = QApplication(sys.argv)

if os.name == "nt": #running on Windows
    #need to set appid before set application icon
    import ctypes
    myappid = 'my_console_or_whatever_1.0.0' # arbitrary string
    ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)
icon = QtGui.QIcon(os.path.join('icon', 'app.png'))
app.setWindowIcon(icon)

window = QMainWindow()
ui = MyConsoleUI()
ui.setupUi(window)
ui.consoleWidget.setScope(scope)
window.show()
sys.exit(app.exec_())
