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
import json
from functools import partial
from util import printToShell
import threading

# PyQt-related
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import QTimer, pyqtSignal
from PyQt5.QtCore import pyqtSlot, QObject
from PyQt5.QtWidgets import QApplication, QMainWindow
from ConsoleWidget import ConsoleWidget
from QuickCmdButtonListWidget import QuickCmdButtonListWidget, QuickCmdButtonListWidgetItem
from QuickCmdEditDialog import QuickCmdEditDialog
from UserInputDialog import UserInputDialog

class MyConsoleUI(QObject):
    userInputNeeded = pyqtSignal([dict])
    def __init__(self):
        super().__init__()
        self.requestUserInputDict = None
        self.userInputNeeded.connect(self.requestUserInput)
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

        # right panel
        self.addQuickCmdButton = QtWidgets.QPushButton(self.mainWindow)
        self.addQuickCmdButton.setText("Add")
        self.addQuickCmdButton.setGeometry(QtCore.QRect(820, 50, 85, 35))
        self.addQuickCmdButton.clicked.connect(partial(self.onQuickCmdListChangeButtonClicked, "add"))

        self.deleteQuickCmdButton = QtWidgets.QPushButton(self.mainWindow)
        self.deleteQuickCmdButton.setText("Delete")
        self.deleteQuickCmdButton.setGeometry(QtCore.QRect(925, 50, 85, 35))
        self.deleteQuickCmdButton.clicked.connect(partial(self.onQuickCmdListChangeButtonClicked, "delete"))

        self.editQuickCmdButton = QtWidgets.QPushButton(self.mainWindow)
        self.editQuickCmdButton.setText("Edit")
        self.editQuickCmdButton.setGeometry(QtCore.QRect(1030, 50, 85, 35))
        self.editQuickCmdButton.clicked.connect(partial(self.onQuickCmdListChangeButtonClicked, "edit"))

        self.quickCmdButtonListWidget = QuickCmdButtonListWidget(mainWindow)
        self.quickCmdButtonListWidget.setGeometry(QtCore.QRect(820, 100, 350, 480))
        self.quickCmdButtonListWidget.itemDoubleClicked.connect(self.onCmdButtonClicked)
        self.quickCmdButtonListWidget.focused.connect(self.onQuickCmdListWidgetFocused)
        self.quickCmdButtonListWidget.unfocused.connect(self.onQuickCmdListWidgetUnfocused)
        self.loadQuickCmds()
        self.onQuickCmdListWidgetUnfocused()
        self.quickCmdButtonListWidget.reordered.connect(self.onQuickCmdListReordered)

        self.retranslateUi(mainWindow)
        QtCore.QMetaObject.connectSlotsByName(mainWindow)
        printToShell("ready")
        self.timer = QTimer()
        self.timer.timeout.connect(self.autorun)
        self.timer.setSingleShot(True)
        self.timer.start(1)
    def onQuickCmdListWidgetFocused(self):
        if self.quickCmdButtonListWidget.count() > 0:
            self.deleteQuickCmdButton.setEnabled(True)
            self.editQuickCmdButton.setEnabled(True)
    def onQuickCmdListWidgetUnfocused(self):
        self.deleteQuickCmdButton.setEnabled(False)
        self.editQuickCmdButton.setEnabled(False)
    def onQuickCmdListChangeButtonClicked(self, button):
        printToShell("clicked button: ", button)
        currentItem = self.quickCmdButtonListWidget.currentItem()
        if button in ("add", "edit"):
            self.dialog = QuickCmdEditDialog(self.mainWindow)
            self.dialog.finished.connect(self.onQuickCmdEditDialogFinished)
            self.dialog.setMode(button)
            if button == "add":
                self.dialog.setWindowTitle("Add New Quick Command")
            elif button == "edit":
                if not currentItem: return
                self.dialog.setWindowTitle("Edit Quick Command")
                self.dialog.setCmdName(currentItem.name)
                self.dialog.setSourceCode(currentItem.action)
            self.dialog.open()
        elif button == "delete":
            if not currentItem: return
            self.dialog = QtWidgets.QMessageBox(self.mainWindow)
            self.dialog.buttonClicked.connect(self.onQuickCmdDeletionConfirmingDialogFinished)
            self.dialog.setText('Are you sure to delete quick command "{}"?'.format(currentItem.name))
            self.confirmButtonYes = self.dialog.addButton(QtWidgets.QMessageBox.Yes)
            self.confirmButtonNo = self.dialog.addButton(QtWidgets.QMessageBox.No)
            self.dialog.open()
    def onQuickCmdDeletionConfirmingDialogFinished(self, button):
        #printToShell(button)
        if button == self.confirmButtonYes:
            printToShell("yes")
            currentRow = self.quickCmdButtonListWidget.currentRow()
            self.quickCmdButtonListWidget.takeItem(currentRow)
            self.quickCmdButtonListWidget.refreshItemIndex()
            if self.quickCmdButtonListWidget.count() == 0: #empty
                self.onQuickCmdListWidgetUnfocused()
            self.saveQuickCmds()
        elif button == self.confirmButtonNo:
            printToShell("No")
        else:
            printToShell("Unknown button", button)
    def onQuickCmdListReordered(self):
        self.saveQuickCmds()
    def onQuickCmdEditDialogFinished(self, mode, name, sourceCode):
        printToShell("mode: {}, name: {}, source: {}",
                mode, name, sourceCode)
        if mode not in ("add", "edit"):
            printToShell("invalid mode:", mode)
            return
        if not name:
            printToShell("empty name")
            return
        if not sourceCode:
            printToShell("empty source  code")
            return
        if mode == "add":
            cmdButtonItem = QuickCmdButtonListWidgetItem()
            cmdButtonItem.name = name
            cmdButtonItem.action = sourceCode
            self.quickCmdButtonListWidget.addItem(cmdButtonItem)
        elif mode == "edit":
            item = self.quickCmdButtonListWidget.currentItem()
            item.name = name
            item.action = sourceCode
            self.quickCmdButtonListWidget.refreshItemIndex()
        self.saveQuickCmds()
    def onCmdButtonClicked(self, cmdButtonItem):
        printToShell(cmdButtonItem)
        action = cmdButtonItem.action
        if action:
            self.consoleWidget.runSourceCode(action)
    def loadQuickCmds(self):
        try:
            with open("quick_cmds.json", "r") as fCmds:
                cmds = json.load(fCmds)
                for cmd in cmds:
                    cmdButton = QuickCmdButtonListWidgetItem(self.quickCmdButtonListWidget)
                    cmdButton.name = cmd["name"]
                    cmdButton.action = cmd["action"]
                    self.quickCmdButtonListWidget.addItem(cmdButton)
        except Exception as ex:
            printToShell(ex)
            printToShell(traceback.format_exc())
    def saveQuickCmds(self):
        try:
            count = self.quickCmdButtonListWidget.count()
            cmdList = []
            for i in range(count):
                item = self.quickCmdButtonListWidget.item(i)
                cmd = {}
                cmd["name"] = item.name
                cmd["action"] = item.action
                cmdList.append(cmd)
            with open("quick_cmds.json", "w") as fCmds:
                json.dump(cmdList, fCmds)
        except Exception as ex:
            printToShell(ex)
            printToShell(traceback.format_exc())
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
    def requestUserInput(self, configDict):
        self.requestUserInputDict = configDict
        hint = configDict["hint"]
        lock = configDict["lock"]
        self.requestUserInputDict["lock"].acquire()

        self.dialog = UserInputDialog(self.mainWindow)
        self.dialog.finished.connect(self.onUserInputDialogFinished)
        self.dialog.setHint(hint)
        self.dialog.open()

    def onUserInputDialogFinished(self, result):
        if not self.requestUserInputDict: return
        if result == QtWidgets.QDialog.Accepted:
            self.requestUserInputDict["value"] = self.dialog.userInputValue
        else:
            self.requestUserInputDict["value"] = None
        self.requestUserInputDict["condition"].notify()
        self.requestUserInputDict["lock"].release()
        self.requestUserInputDict = None
    def autorun(self):
        """
        scan the .py file in autorun/ directory and run them one by one
        """
        printToShell("[autorun]")
        scriptList = glob.glob(os.path.join("autorun", "*.py"))
        printToShell("scriptList:", scriptList)
        for script in scriptList:
            self.consoleWidget.runScript(script)

def runScript(scriptPath):
    ui.consoleWidget.runScript(scriptPath)

def requestUserInput(hintText):
    l = []
    d = {}
    d["hint"] = hintText
    d["lock"] = threading.Lock()
    d["condition"] = threading.Condition(d["lock"])
    d["value"] = None
    d["lock"].acquire()
    ui.userInputNeeded.emit(d)
    d["condition"].wait()
    d["lock"].release()
    printToShell("finished, value:", d["value"])
    return d["value"]

scope = {}
scope["__builtins__"] = globals()["__builtins__"]
scope["runScript"] = runScript
scope["requestUserInput"] = requestUserInput

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
