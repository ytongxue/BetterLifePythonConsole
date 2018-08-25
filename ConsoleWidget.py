#! /usr/bin/python3
import code
import re
import traceback
from contextlib import redirect_stdout, redirect_stderr
from collections import namedtuple
import queue

from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import QThread, pyqtSignal, QTimer
from PyQt5.QtCore import pyqtSlot, QObject
from PyQt5.QtGui import QKeyEvent, QKeySequence

from util import printToShell
    
"""
class ExecThread(QThread):
    finished = pyqtSignal()
    def __init__(self, sourceCode, stdout, stderr):
        super().__init__()
        self.sourceCode = sourceCode
        self.stdout = stdout
        self.stderr = stderr
        self.scope = None
    def setScope(self, scope):
        self.scope = scope
    def run(self):
        try:
            with redirect_stdout(self.stdout), redirect_stderr(self.stderr):
                exec(self.sourceCode, self.scope, self.scope)
        except Exception as ex:
            printToShell("exception happend in exec()")
            printToShell(traceback.format_exc())
            self.stderr.write(traceback.format_exc())
        finally:
            self.finished.emit()
            """

class OutputBuffer(QObject):
    outputWritten = pyqtSignal([str])
    def __init__(self):
        super().__init__()
    def write(self, string):
        self.outputWritten.emit(string)
    def flush(self):
        pass #do nothing

class MyConsole(QThread):
    finished = pyqtSignal([bool]) #need more line(s)
    outputWritten = pyqtSignal([str])
    Work = namedtuple("Work", "type content")
    def __init__(self, scope=None, filename='<console>'):
        super().__init__()
        self.realConsole = code.InteractiveConsole(scope, filename)
        self.scope = scope
        self.plainTextWidget = None
        self.output = None
        self.output = OutputBuffer()
        self.output.outputWritten.connect(self.outputWritten)
        self.workQueue = queue.Queue()
        self.running = False
        savedHelp = help
        def overridedHelp(*args):
            if len(args) != 0:
                savedHelp(*args)
        self.scope["help"] = overridedHelp
    def start(self):
        self.running = True
        super().start()
    def stop(self):
        self.running = False
        super.join()
    def run(self):
        while self.running:
            try:
                work = self.workQueue.get(timeout=0.1)
            except queue.Empty as ex:
                continue
            if work.type == "line":
                needMoreLine = self.realConsole.push(work.content)
                self.finished.emit(needMoreLine)
            elif work.type == "script":
                try:
                    with redirect_stdout(self.output), redirect_stderr(self.output):
                        exec(work.content, self.scope, self.scope)
                except Exception as ex:
                    printToShell("exception happend in exec()")
                    printToShell(traceback.format_exc())
                    self.output.write(traceback.format_exc())
                finally:
                    self.finished.emit(False)
            else:
                printToShell("Unknown work type:", work.type)

    def push(self, line):
        self.workQueue.put(self.Work("line", line))
    def runScriptSource(self, sourceCode):
        self.workQueue.put(self.Work("script", sourceCode))

class ConsoleWidget(QtWidgets.QPlainTextEdit):
    welcomeMsg = """
Hello World! Welcome to my console. Have fun.
"""
    promote = ">>> "
    moreLinePromote = "... "
    newline = pyqtSignal([str])
    def __init__(self, parent = None):
        super().__init__(parent)
        self.histories = []
        self.historyIndex = -1
        self.currentLine = ""
        self.scriptRunning = False
        self.tabCounter = 0
        self.scope = {}
        self.console = None
        
        self.appendPlainText(self.welcomeMsg)
        self.appendPlainText("\n")
        self.appendPlainText(self.promote)
    
    def setScope(self, scope):
        self.scope = scope
        self.console = MyConsole(scope)
        self.console.outputWritten.connect(self.onOutputWritten)
        self.console.finished.connect(self.onConsoleFinished)
        self.console.start()
    def getCurrentLine(self):
        """ get content of current line(the line the cursor is at) """
        cursor = self.textCursor()
        block = cursor.block()
        line = block.text()[len(self.promote):]
        return line
    def onEnter(self):
        #printToShell("just got an Enter key")
        if not self.console: return
        self.historyIndex = -1
        line = self.getCurrentLine()
        printToShell('[onEnter] line:"{}"'.format(line))
        if line:
            self.histories.insert(0, line)
        self.appendPlainText("\n")
        self.scriptRunning = True
        self.console.push(line)
    def appendPlainText(self, string):
        """
        QPlainTextEdit's original appendPlainText() method appends a new paragraph,
    with newlines before and after the string.
        And our version only appends just the string, no newlines added.
        """
        cursor = self.textCursor()
        cursor.movePosition(QtGui.QTextCursor.End)
        self.setTextCursor(cursor)
        self.insertPlainText(string)
    def insertPromote(self, needMoreLine = False, newline = True):
        if newline:
            self.appendPlainText("\n")
        promote = self.promote
        if needMoreLine:
            promote = self.moreLinePromote
        self.appendPlainText(promote)
    def keyPressEvent(self, keyEvent):
        key = keyEvent.key()
        #printToShell("key: {0} => {0:#x}".format(key))
        cursor = self.textCursor()
        #printToShell("cursor:", cursor.blockNumber(), self.blockCount())
        handled = False
        if self.scriptRunning:
            handled = True
        elif cursor.blockNumber() < self.blockCount() - 1: # not on the bottom line
            #printToShell("cursor not on the bottom line")
            handled = True
        elif key == QtCore.Qt.Key_Backspace \
                and self.textCursor().columnNumber() <= len(self.promote):
            handled = True
        elif key == QtCore.Qt.Key_Return: #ENTER
            self.onEnter()
            handled = True
        elif key == QtCore.Qt.Key_Up:
            if self.histories and self.historyIndex < len(self.histories) - 1:
                self.historyIndex += 1
                line = self.histories[self.historyIndex]
                #printToShell("history: ", line)
                cursor = self.textCursor()
                cursor.select(QtGui.QTextCursor.BlockUnderCursor)
                cursor.removeSelectedText()
                self.insertPromote()
                self.appendPlainText(line)
            handled = True
        elif key == QtCore.Qt.Key_Down:
            line = ""
            if self.historyIndex > -1:
                if self.historyIndex == 0:
                    self.historyIndex -= 1
                    line = self.currentLine
                elif self.histories and self.historyIndex > 0:
                    self.historyIndex -= 1
                    line = self.histories[self.historyIndex]
                cursor = self.textCursor()
                cursor.select(QtGui.QTextCursor.BlockUnderCursor)
                cursor.removeSelectedText()
                self.insertPromote()
                self.appendPlainText(line)
            handled = True
        elif key == QtCore.Qt.Key_Tab:
            self.tabCounter += 1
            line = self.getCurrentLine()
            pattern = re.compile(r"([\d\w_]+$)")
            m = pattern.search(line)
            if m:
                part = m.groups()[0]
                printToShell("part", part)
                flatDict = {}
                for symbol in self.scope:
                    flatDict[symbol] = self.scope[symbol]
                for symbol in dir(self.scope["__builtins__"]):
                    flatDict[symbol] = self.scope["__builtins__"].__dict__[symbol]
                candidateList = []
                for symbol in flatDict:
                    if symbol.startswith(part):
                        #printToShell("find: ", symbol)
                        candidateList.append(symbol)
                if len(candidateList) == 1:
                    candidate = candidateList[0]
                    cursor = self.textCursor()
                    cursor.select(QtGui.QTextCursor.BlockUnderCursor)
                    cursor.removeSelectedText()
                    pos = line.rfind(part)
                    if pos == -1:
                        return
                    line = line[:pos] + candidate
                    if callable(flatDict[candidate]):
                        line += "("
                    self.insertPromote()
                    self.appendPlainText(line)
                elif len(candidateList) > 1 and self.tabCounter > 1:
                    self.appendPlainText("\n")
                    # show all candidates
                    for candidate in candidateList:
                        self.appendPlainText(candidate + "  ")
                    self.insertPromote()
                    self.appendPlainText(line)
            else:
                printToShell("nothing found")
            handled = True
        if key != QtCore.Qt.Key_Tab:
            #printToShell("clear tab counter")
            self.tabCounter = 0
        if not handled:
            #printToShell("let parent handle this key")
            super().keyPressEvent(keyEvent)
            self.currentLine = self.getCurrentLine()
    def runScripts(self, scriptPathList):
        self.scriptPathList = scriptPathList
        self.scriptListIndex = 0
        self.runScript(scriptPathList[0])
    def runScript(self, scriptPath):
        if self.scriptRunning: return
        self.setFocus()
        self.appendPlainText("\n[console] running {}\n\n".format(scriptPath))
        self.scriptRunning = True
        printToShell("runScript:", scriptPath)
        self.console.runScriptSource(open(scriptPath, "r").read())
    def runSourceCode(self, sourceCode):
        if self.scriptRunning:
            printToShell("console is busy")
            return
        if not sourceCode: return
        self.setFocus()
        #self.appendPlainText("\nrun source code:\n")
        self.appendPlainText(sourceCode)
        self.appendPlainText("\n")
        self.console.runScriptSource(sourceCode)
    def onOutputWritten(self, string):
        self.appendPlainText(string)
    def onConsoleFinished(self, needMoreLine):
        self.scriptRunning = False
        if self.scriptPathList:
            if self.scriptListIndex < len(self.scriptPathList) - 1:
                printToShell("run next script")
                self.scriptListIndex += 1
                self.runScript(self.scriptPathList[self.scriptListIndex])
                return
            else:
                self.scriptPathList = None
        # insert promote
        self.insertPromote(needMoreLine, False)
