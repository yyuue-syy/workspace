import sys
import os
import serial
import serial.tools.list_ports
import platform
import time
import xmodem
import logging

from PyQt6.QtGui import QFont
from PyQt6.QtGui import QTextCursor
from PyQt6.QtGui import QAction
from PyQt6.QtGui import QKeySequence

from PyQt6.QtCore import pyqtSignal
from PyQt6.QtCore import QThread
from PyQt6.QtCore import Qt
from PyQt6.QtCore import QTimer
from PyQt6.QtCore import QT_VERSION_STR
from PyQt6.QtCore import PYQT_VERSION_STR

from PyQt6.QtWidgets import QMenu
from PyQt6.QtWidgets import QApplication
from PyQt6.QtWidgets import QMainWindow
from PyQt6.QtWidgets import QPushButton
from PyQt6.QtWidgets import QVBoxLayout
from PyQt6.QtWidgets import QHBoxLayout
from PyQt6.QtWidgets import QWidget
from PyQt6.QtWidgets import QTreeWidget
from PyQt6.QtWidgets import QTreeWidgetItem
from PyQt6.QtWidgets import QFileDialog
from PyQt6.QtWidgets import QSplitter
from PyQt6.QtWidgets import QLabel
from PyQt6.QtWidgets import QTextEdit
from PyQt6.QtWidgets import QMessageBox
from PyQt6.QtWidgets import QFormLayout
from PyQt6.QtWidgets import QSizePolicy
from PyQt6.QtWidgets import QComboBox
from PyQt6.QtWidgets import QLineEdit
from PyQt6.QtWidgets import QToolTip
from PyQt6.QtWidgets import QGridLayout
from PyQt6.QtWidgets import QListWidget
from PyQt6.QtWidgets import QInputDialog
from PyQt6.QtWidgets import QDockWidget
from PyQt6.QtWidgets import QToolBar
from PyQt6.QtWidgets import QLabel
from PyQt6.QtWidgets import QFontDialog
from PyQt6.QtWidgets import QColorDialog

class uartTool(QMainWindow):
	def __init__(self, upWindow:QWidget=None):
		super().__init__()

		self.upWindow = upWindow

		self.uiInit()

	def uiCentralWidgetInit(self):
		self.centralWidget = QWidget()
		self.setCentralWidget(self.centralWidget)
		self.gridLayout = QGridLayout(self.centralWidget)

	def uiInit(self):
		self.uiCentralWidgetInit()

	def closeEvent(self, event):
		print('uart tool close')
		if self.upWindow != None:
			self.upWindow.show()

		return super().closeEvent(event)
