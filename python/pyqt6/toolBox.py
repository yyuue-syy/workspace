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

from PyQt6.QtCore import Qt
from PyQt6.QtCore import QSize
from PyQt6.QtCore import QTimer
from PyQt6.QtCore import QThread
from PyQt6.QtCore import pyqtSignal
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

from css.cssQPushButton import *

from testCase.testQpushButton import *
from testCase.testQLineEdit import *

from uartTool import *
from socketTool import *

class cssPtn(QPushButton):
	def __init__(self, title, parent=None):
		super().__init__(parent)

		self.setText(title)
		#self.setMinimumHeight(40)
		#self.setMinimumWidth(80)
		self.setStyleSheet(css_btn_cancel)
		self.setCheckable(True)

	def is_checked(self):
		return self.isChecked()

class toolBoxEnterWidget(QWidget):
	def __init__(self):
		super().__init__()

		self.toolNames = {
			'test-QPushButton': { 'ptn': None, 'window': None },
			'test-QLineEdit'  : { 'ptn': None, 'window': None },
			'test-tool'       : { 'ptn': None, 'window': None },
			'uart-tool'       : { 'ptn': None, 'window': None },
			'socket-tool'     : { 'ptn': None, 'window': None },
		}

		self.uiInit()

	def uiInit(self):
		self.setGeometry(1000, 600, 200, 250)

		self.gridLayoutInit()
		self.toolWindowInit()
		self.toolBtnInit()

	def gridLayoutInit(self):
		self.gridLayout = QGridLayout(self)

		self.gridLayoutSpacing = len(self.toolNames)
		self.gridLayout.setSpacing(self.gridLayoutSpacing)
		for i in range(self.gridLayoutSpacing):
			self.gridLayout.setColumnStretch(i, 1)
			self.gridLayout.setRowStretch(i, 1)

	def toolBtnClicked(self):
		sender = self.sender()
		toolName = sender.text()
		print(toolName)

		if self.toolNames[toolName]['window'] != None:
			self.hide()
			self.toolNames[toolName]['window'].show()

	def toolWindowInit(self):
		for toolName in self.toolNames:
			if toolName == 'uart-tool':
				self.toolNames[toolName]['window'] = uartTool(self)
			elif toolName == 'socket-tool':
				self.toolNames[toolName]['window'] = socketTool(self)
			elif toolName == 'test-QPushButton':
				self.toolNames[toolName]['window'] = testQpushButton(self)
			elif toolName == 'test-QLineEdit':
				self.toolNames[toolName]['window'] = testQLineEdit(self)

	def toolBtnInit(self):
		for toolName in self.toolNames.keys():
			ptn = cssPtn(toolName)
			ptn.clicked.connect(self.toolBtnClicked)
			self.toolNames[toolName]['ptn'] = ptn

		index = 0
		for toolName, info in self.toolNames.items():
			self.gridLayout.addWidget(info['ptn'], index, 0, 1, self.gridLayoutSpacing)
			index += 1

if __name__ == "__main__":
	app = QApplication(sys.argv)
	app.setStyle('Fusion')

	window = toolBoxEnterWidget()
	window.show()
	sys.exit(app.exec())
