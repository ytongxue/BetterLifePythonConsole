from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import QTimer
from PyQt5.QtCore import pyqtSlot, pyqtSignal, QObject

import util
util.redirectPrintToShell(globals())

class QuickCmdButtonListWidgetItem(QtWidgets.QListWidgetItem):
    def __init__(self, *args):
        super().__init__(*args)
        font = QtGui.QFont()
        font.setFamily("DejaVu Sans Mono")
        font.setPointSize(12)
        self.setFont(font)

        self.name = ""
        self.action = ""
    def __repr__(self):
        s = ""
        s = "<{cls} name: {name}>".format(cls=__class__.__name__, name=self.name)
        return s

class QuickCmdButtonListWidget(QtWidgets.QListWidget):
    reordered = pyqtSignal()
    focused = pyqtSignal()
    unfocused = pyqtSignal()
    def __init__(self, *args):
        super().__init__(*args)
        self.setAcceptDrops(True)
        self.setDragEnabled(True)
        self.setSelectionMode(QtWidgets.QAbstractItemView.SingleSelection)
        self.setDropIndicatorShown(True)
        self.setDragDropMode(QtWidgets.QAbstractItemView.InternalMove)
    def dropEvent(self, event):
        print("[dropEvent] event", event)
        print("event source:", event.source())
        super().dropEvent(event)
        self.refreshItemIndex()
        self.reordered.emit()
    def focusInEvent(self, event):
        #print("focused")
        super().focusInEvent(event)
        self.focused.emit()
    def focusOutEvent(self, event):
        #print("unfocused")
        super().focusOutEvent(event)
        self.unfocused.emit()
    def addItem(self, item):
        super().addItem(item)
        self.refreshItemIndex()
    def __iter__(self):
        for i in range(self.count()):
            item = self.item(i)
            yield item
    def refreshItemIndex(self):
        """ refresh the index at the front of each item, usally needed after the list is changed """
        for i in range(self.count()):
            item = self.item(i)
            if isinstance(item, QuickCmdButtonListWidgetItem):
                item.setText("{}. {}".format(i + 1, item.name))
