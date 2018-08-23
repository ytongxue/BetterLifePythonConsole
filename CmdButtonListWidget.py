from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import QTimer
from PyQt5.QtCore import pyqtSlot, pyqtSignal, QObject

class CmdButtonListWidgetItem(QtWidgets.QListWidgetItem):
    def __init__(self, *args):
        super().__init__(*args)
        self.name = ""
        self.action = ""
    def __repr__(self):
        s = ""
        s = "<{cls} name: {name}>".format(cls=__class__.__name__, name=self.name)
        return s

class CmdButtonListWidget(QtWidgets.QListWidget):
    reordered = pyqtSignal()
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
    def addItem(self, item):
        if isinstance(item, CmdButtonListWidgetItem):
            item.setText("{}. {}".format(self.count(), item.name))
        super().addItem(item)
    def __iter__(self):
        for i in range(self.count()):
            item = self.item(i)
            yield item
    def refreshItemIndex(self):
        """ refresh the index at the front of each item, usally needed after the list is changed """
        for i in range(self.count()):
            item = self.item(i)
            if isinstance(item, CmdButtonListWidgetItem):
                item.setText("{}. {}".format(i + 1, item.name))