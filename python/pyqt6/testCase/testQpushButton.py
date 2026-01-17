import sys
import os
import serial
import serial.tools.list_ports
import platform
import time
import xmodem
import logging

from PyQt6.QtGui import QFont
from PyQt6.QtGui import QAction
from PyQt6.QtGui import QTextCursor
from PyQt6.QtGui import QKeySequence

from PyQt6.QtCore import Qt
from PyQt6.QtCore import QTimer
from PyQt6.QtCore import QThread
from PyQt6.QtCore import pyqtSignal
from PyQt6.QtCore import QT_VERSION_STR
from PyQt6.QtCore import PYQT_VERSION_STR

from PyQt6.QtWidgets import (
	# 
	QApplication,

	# layout
	QMainWindow,
	QVBoxLayout,
	QHBoxLayout,
	QFormLayout,
	QGridLayout,
	QStackedLayout,

	# widget
	QWidget,
	QTreeWidget,
	QTreeWidgetItem,
	QListWidget,
	QDockWidget,
	QTabWidget,

	QPushButton,
	QRadioButton,

	QButtonGroup,

	QMenu,
	QLabel,
	QSplitter,
	QSizePolicy,

	QCheckBox,
	QComboBox,
	QMessageBox,

	QLineEdit,
	QTextEdit,

	QToolTip,
	QToolBar,

	QFileDialog,
	QInputDialog,
	QFontDialog,
	QColorDialog,
)

#background: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #556, stop:1 #112);

testQPushButtonCss00 ='''
	QPushButton {                      /* 正常状态 */
		color: white;                  /* 文本颜色 */
		background-color: #4CAF50;     /* 背景颜色 */
		border: 2px solid #45a049;     /* 边框样式（宽度、类型、颜色） */
		border-radius: 10px;           /* 边框圆角 */
		padding: 5px 15px;             /* 内边距（上下、左右） */
		margin: 2px;                   /* 外边距 */
		font: bold 18px Arial;         /* 字体（粗细、大小、字体族） */
		min-width: 80px;               /* 最小宽度 */
		max-width: 200px;              /* 最大宽度 */
		min-height: 30px;              /* 最小高度 */
		max-height: 50px;              /* 最大高度 */
		opacity: 0.9;                  /* 透明度(0.0~1.0) */
		text-align: center;            /* 文本对齐方式 */
		text-decoration: underline;    /* 文本装饰（下划线等） */
		text-transform: uppercase;     /* 文本转换（大写、小写等） */
	}
	QPushButton:hover {                /* 鼠标悬停 */
		background-color: #F09E42; 
	}
	QPushButton:pressed {              /* 按钮按下 */
		background-color: #3d8b40;
		border-style: inset;
	}
	QPushButton:checked {              /* 选中状态 setCheckable(True) */
		background-color: #2E7D32;
	}
	QPushButton:disabled {             /* 禁用状态 */
		color: #cccccc;
		background-color: #f0f0f0;
	}
	QPushButton:focus {                /* 获得焦点 */
		outline: 2px solid #64B5F6;
	}
	QPushButton:default {              /* 默认按钮 setDefault(True) */
		border: 2px solid navy;
	}
'''

class testQpushButton(QMainWindow):
	def __init__(self, upWindow:QWidget=None):
		super().__init__()

		self.upWindow = upWindow

		self.ptnSignalMap = {
			'clicked': QComboBox(),
			'pressed': QComboBox(),
			'released': QComboBox(),
			'toggled': QComboBox(),

			'checkable': QComboBox(),
		}

		self.cssStateRadioBtnMap = {
			'normal': QRadioButton(),
			'hover': QRadioButton(),
			'pressed': QRadioButton(),
			'checked': QRadioButton(),
			'disable': QRadioButton(),
			'default': QRadioButton(),
		}

		self.cssTabs = {
			'背景与颜色': QWidget(),
			'边框样式': QWidget(),
			'字体与文本': QWidget(),
			'间距与尺寸': QWidget(),
			'其他样式': QWidget(),
		}

		self.uiInit()

	def uiCentralWidgetInit(self):
		self.setGeometry(300, 300, 1300, 800)
		self.centralWidget = QWidget()
		self.setCentralWidget(self.centralWidget)

		self.gridLayout = QGridLayout(self.centralWidget)

	def uiInit(self):
		self.uiCentralWidgetInit()
		self.testInit()

	def onBtnClicked(self):
		print('btn clicked')

	def onBtnPressed(self):
		print('btn pressed')

	def onBtnReleased(self):
		print('btn released')

	def onBtnToggled(self):
		print('btn toggled')

	def testSignalEnable(self, text:str):
		sender:QComboBox = self.sender()

		currentSigName = None

		for _, comboBox in self.ptnSignalMap.items():
			if sender == comboBox:
				currentSigName = comboBox.objectName()
				break

		print(currentSigName, text)

		if currentSigName == 'clicked':
			self.testQpushButton.clicked.connect(self.onBtnClicked) \
				if text == 'enable' else self.testQpushButton.clicked.disconnect()
		elif currentSigName == 'pressed':
			self.testQpushButton.pressed.connect(self.onBtnPressed) \
				if text == 'enable' else self.testQpushButton.pressed.disconnect()
		elif currentSigName == 'released':
			self.testQpushButton.released.connect(self.onBtnReleased) \
				if text == 'enable' else self.testQpushButton.released.disconnect()
		elif currentSigName == 'toggled':
			self.testQpushButton.toggled.connect(self.onBtnToggled) \
				if text == 'enable' else self.testQpushButton.toggled.disconnect()
		elif currentSigName == 'checkable':
			self.testQpushButton.setCheckable(True) \
				if text == 'enable' else self.testQpushButton.setCheckable(False)

	def testInit(self):
		self.testQpushButton = QPushButton('button')

		self.ptnSignalFormLayout = QFormLayout()
		for sigName, comboBox in self.ptnSignalMap.items():
			comboBox.currentTextChanged.connect(self.testSignalEnable)
			comboBox.setObjectName(sigName)
			comboBox.addItems(['enable', 'disable'])
			comboBox.setCurrentIndex(0)
			self.ptnSignalFormLayout.addRow(QLabel(sigName), comboBox)

		self.cssChooseComboBox = QComboBox() # for choose css
		self.cssChooseComboBox.currentTextChanged.connect(self.cssChooseComboBoxTestChange)
		self.cssChooseComboBox.addItems([
			'css00', 'css01', 'css02', 'css03', 'css04',
			'css05', 'css06', 'css07', 'css08', 'css09',
		])
		self.cssChooseComboBox.setCurrentIndex(0)

		self.gridLayout.addWidget(self.testQpushButton, 2, 0, 1, 1)
		self.gridLayout.addWidget(self.cssChooseComboBox, 6, 0, 1, 1)
		self.gridLayout.addLayout(self.ptnSignalFormLayout, 7, 0, 1, 1)

		self.cssInfoGridLayout = QGridLayout()
		self.cssInfoGridLayout.setSpacing(10)
		for i in range(10):
			self.cssInfoGridLayout.setColumnStretch(i, 1)
			self.cssInfoGridLayout.setRowStretch(i, 1)

		self.gridLayout.addLayout(self.cssInfoGridLayout, 0, 3, 10, 7)

		self.cssTabWidget = QTabWidget()
		for name, widget in self.cssTabs.items():
			self.cssTabWidget.addTab(widget, name)

			layout = QFormLayout()
			if name == '背景与颜色':
				for i in range(50):
					openColorDialogPtn = QPushButton('color')
					layout.addRow(QLabel('color'), openColorDialogPtn)

			widget.setLayout(layout)

		radioGroup = QButtonGroup()
		index = 0
		for name, btn in self.cssStateRadioBtnMap.items():
			btn.setText(name)
			radioGroup.addButton(btn)
			self.cssInfoGridLayout.addWidget(btn, 0, index)
			index += 1

		self.cssInfoGridLayout.addWidget(self.cssTabWidget, 1, 0, 10, 10)

	def ptnSignalComboBoxTextChanged(self, text:str):
		print(text)

	def cssShowCheckableComboBoxTextChanged(self, text:str):
		if text == 'Checkable':
			self.testQpushButton.setCheckable(True)
		elif text == 'Un-Checkable':
			self.testQpushButton.setCheckable(False)

	def cssChooseComboBoxTestChange(self, text:str):
		self.currentCss = ''
		if text == 'css00':
			self.currentCss = testQPushButtonCss00
		self.testQpushButton.setStyleSheet(self.currentCss)

	def closeEvent(self, event):
		if self.upWindow != None:
			self.upWindow.show()

		return super().closeEvent(event)
