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

from css.cssQPushButton import *

tool_version = '0.0.1'

BAUDRATE = 115200

class updater_uart():
	def __init__(self, port='', buadrate=None):
		self.port = port
		self.baudrate = buadrate
		self.serial = None
		self.is_open = False

	def open(self):
		try:
			self.serial = serial.Serial(self.port, self.baudrate, timeout=1)
		except Exception as e:
			return -1, str(e)

		self.serial.timeout = 0.1
		self.serial.write_timeout = 0.1
		self.is_open = True

		return 0, 'success'

	def hard_reset(self):
		self.serial.rts = 1
		self.serial.rts = 0

	def close(self):
		self.serial.close()
		self.serial = None
		self.is_open = False

	def reset(self):
		self.serial.reset_input_buffer()
		self.serial.reset_output_buffer()

	def read(self, num, timeout=0):
		if timeout:
			self.serial.timeout = timeout

		return self.serial.read(num)

	def read_line(self):
		return self.serial.readline().decode('utf-8', errors='replace').strip()
		# return self.serial.readline()

	def read_all(self):
		return self.serial.read_all()

	def read_until(self, pattern, timeout=0):
		start = time.time()
		recv = self.serial.read(1)
		while(time.time() - start < timeout):
			if pattern in recv:
				return recv
			recv += self.serial.read(1)
		return None

	def cancel_read(self):
		self.serial.cancel_read()

	def write(self, s, timeout=0):
		if timeout:
			self.serial.timeout = timeout

		return self.serial.write(s)

	def flush(self):
		self.serial.read_all()
		self.serial.flush()

	def change_baudrate(self, baudrate):
		if self.baudrate != baudrate:
			self.baudrate = baudrate
			self.serial.baudrate = self.baudrate

	def set_buf_size(self, size):
		if platform.system() == 'Windows':
			self.serial.set_buffer_size(size)

class my_ptn(QPushButton):
	def __init__(self, title, parent=None):
		super().__init__(parent)

		self.setText(title)
		#self.setMinimumHeight(40)
		#self.setMinimumWidth(80)
		self.setStyleSheet(css_btn_cancel)
		self.setCheckable(True)

	def is_checked(self):
		return self.isChecked()

class serialReadThread(QThread):
	log = pyqtSignal(str)
	err_log = pyqtSignal(str)

	def __init__(self, file_path, port:updater_uart=None, file_data:bytes=None):
		super().__init__()
		self.port = port
		self.file_path = file_path
		self.file_data = file_data

	def open_port(self):
		ret, err = self.port.open()
		if ret < 0:
			self.err_log.emit(err)
			self.port = None
			return ret
		else:
			self.port.set_buf_size(4 * 1024 * 1024)
		
		return 0

	def _getc(self, size, timeout=1):
		return self.port.read(size) or None

	def _putc(self, data, timeout=1):
		return self.port.write(data) or None

	def disconnect(self):
		if self.port:
			self.port.close()

	def send_cmd(self, cmd:str):
		cmd = cmd + '\n'
		cmd = cmd.encode(encoding='utf-8')
		self.port.write(cmd)
		# print('cmd:', cmd)

	def check_uart_exist(self):
		return 0

	def run(self):
		self.running = True

		while self.running:
			if self.port.serial.in_waiting:
				uart_data = self.port.serial.read(self.port.serial.in_waiting)
				self.log.emit(uart_data.decode('utf-8', errors='replace'))

			self.msleep(1)

	def stop(self):
		self.running = False
		self.quit()
		if self.wait(5000):
			print("thread stop done")
		else:
			print('thread stop timeout')

class serialToolMainWindow(QMainWindow):
	def __init__(self):
		super().__init__()

		self.ptnCmdList = [
			my_ptn('cmd0'), my_ptn('cmd1'), my_ptn('cmd2'), my_ptn('cmd3'), my_ptn('cmd4'),
			my_ptn('cmd5'), my_ptn('cmd6'), my_ptn('cmd7'), my_ptn('cmd8'), my_ptn('cmd9'),
			my_ptn('cmd10'), my_ptn('cmd11'), my_ptn('cmd12'), my_ptn('cmd13'), my_ptn('cmd14'),
			my_ptn('cmd15'), my_ptn('cmd16'), my_ptn('cmd17'), my_ptn('cmd18'), my_ptn('cmd19'),
		]

		self.port = None
		self.serial_ports = []

		self.history = []  # 存储历史命令
		self.inputHistoryIndex = -1  # 当前历史记录索引

		self.thread_serial_download = None

		self.uartOutputTextEditCss = ""

		self.toolBarIsShow = True
		self.uiInit()
		self.serial_ports_refresh()
		# self.serial_ports_open()

	def fileOpenActionTriggered(self):
		QMessageBox.information(self, 'info', 'file open')

	def fileSaveActionTriggered(self):
		QMessageBox.information(self, 'info', 'file save')

	def showToolBarActionTriggered(self):
		if self.toolBarIsShow == True:
			self.toolBar.setVisible(False)
			self.toolBarIsShow = False
			self.showToolBarAction.setText('show tool bar')
		else:
			self.toolBar.setVisible(True)
			self.toolBarIsShow = True
			self.showToolBarAction.setText('close tool bar')

	def uartOutputTextEditFontPtnClicked(self):
		font, ok = QFontDialog.getFont()
		if not ok:
			print('QFontDialog.getFont() fail')

		fontFamily = font.family()
		fontSize = '{0}pt'.format(font.pointSize())
		fontWeight = "bold" if font.bold() else "normal"
		fontStyle = "italic" if font.italic() else "normal"

		self.uartOutputTextEditCss = ''
		self.uartOutputTextEditCss += 'font-family: {0};'.format(fontFamily)
		self.uartOutputTextEditCss += 'font-size: {0};'.format(fontSize)
		self.uartOutputTextEditCss += 'font-weight: {0};'.format(fontWeight)
		self.uartOutputTextEditCss += 'font-style: {0};'.format(fontStyle)

		print(self.uartOutputTextEditCss)
		self.uartOutputTextEdit.setStyleSheet(self.uartOutputTextEditCss)

	def uartOutputTextEditFontColorPtnClicked(self):
		color = QColorDialog.getColor()
		if color.isValid():
			self.uartOutputTextEditCss += 'color: {0};'.format(color.name())
			self.uartOutputTextEdit.setStyleSheet(self.uartOutputTextEditCss)

	def uartOutputTextEditBackgroundColorPtnClicked(self):
		color = QColorDialog.getColor()
		if color.isValid():
			self.uartOutputTextEditCss += 'background-color: {0};'.format(color.name())
			self.uartOutputTextEdit.setStyleSheet(self.uartOutputTextEditCss)

	def uartOutputTextEditAlignmentComboBoxIndexChange(self):
		alignments = {
			'左对齐': Qt.AlignmentFlag.AlignLeft,
			'居中对齐': Qt.AlignmentFlag.AlignCenter,
			'右对齐': Qt.AlignmentFlag.AlignRight,
			'两端对齐': Qt.AlignmentFlag.AlignJustify
		}

		currentText = self.uartOutputTextEditAlignmentComboBox.currentText()
		self.uartOutputTextEdit.setAlignment(alignments[currentText])

	def uiMenuBarInit(self):
		self.fileMenu = self.menuBar().addMenu('File')
		self.settingsMenu = self.menuBar().addMenu('Settings')
		self.helpMenu = self.menuBar().addMenu('help')

		self.fileOpenAction = QAction('open', self)
		self.fileOpenAction.setShortcut(QKeySequence('Ctrl+O'))
		self.fileOpenAction.setStatusTip('打开文件')
		self.fileOpenAction.triggered.connect(self.fileOpenActionTriggered)
		self.fileMenu.addAction(self.fileOpenAction)

		self.fileSaveAction = QAction('save', self)
		self.fileSaveAction.setShortcut(QKeySequence('Ctrl+S'))
		self.fileSaveAction.setStatusTip('保存文件')
		self.fileSaveAction.triggered.connect(self.fileSaveActionTriggered)
		self.fileMenu.addAction(self.fileSaveAction)

		self.showToolBarAction = QAction('show tool bar', self)
		self.showToolBarAction.triggered.connect(self.showToolBarActionTriggered)

		self.setFontAction = QAction('Font', self)
		self.setColorAction = QAction('color', self)

		self.settingsMenu.addAction(self.showToolBarAction)
		self.settingsMenu.addAction(self.setFontAction)
		self.settingsMenu.addAction(self.setColorAction)

		if self.toolBarIsShow == True:
			self.showToolBarAction.setText('close tool bar')
		else:
			self.showToolBarAction.setText('show tool bar')

	def uiToolBarInit(self):
		self.toolBar = QToolBar('tool bar', self)
		self.addToolBar(self.toolBar)

		self.toolBar.addAction(self.fileOpenAction)
		self.toolBar.addAction(self.fileSaveAction)

	def uiStatusBarInit(self):
		self.statusBar().showMessage(
			'app version: {0}, qt version: {1}, pyqt version: {2}'.format(
				tool_version, QT_VERSION_STR, PYQT_VERSION_STR))

	def uiDockWidgetInit(self):
		self.dockWidget = QDockWidget('DockWidget', self)

		### add widget here
		self.dockWidget.setWidget(QLabel('DockWidget content', self))
		self.dockWidget.setAllowedAreas(Qt.DockWidgetArea.AllDockWidgetAreas)

		self.addDockWidget(Qt.DockWidgetArea.LeftDockWidgetArea, self.dockWidget)

	def uiGridLayoutInit(self):
		self.gridLayout = QGridLayout()
		self.gridLayout.setSpacing(10)
		for i in range(10):
			self.gridLayout.setColumnStretch(i, 1)
			self.gridLayout.setRowStretch(i, 1)

		self.uartNameLbl = QLabel('串口号')
		self.uartNameComboBox = QComboBox()
		self.uartNameComboBox.currentTextChanged.connect(lambda: self.serial_ports_change())

		self.uartBaudrateLbl = QLabel('波特率')
		self.uartBaudrateComboBox = QComboBox()
		self.uartBaudrateComboBox.addItems(['115200', '2000000', '3000000'])
		self.uartBaudrateComboBox.setCurrentText('115200')
		self.uartBaudrateComboBox.currentTextChanged.connect(lambda: self.serial_ports_baudrate_change())

		self.uartStopBitslbl = QLabel('停止位')
		self.uartStopBitsComboBox = QComboBox()
		self.uartStopBitsComboBox.addItems(['1', '1.5', '2'])
		self.uartStopBitsComboBox.setCurrentText('1')

		self.uartDataBitsLbl = QLabel('数据位')
		self.uartDataBitsComboBox = QComboBox()
		self.uartDataBitsComboBox.addItems(['8', '7', '6', '6'])
		self.uartDataBitsComboBox.setCurrentText('8')

		self.uartParityLbl = QLabel('奇偶校验')
		self.uartParityComboBox = QComboBox()
		self.uartParityComboBox.addItems(['无', '奇校验', '偶校验'])
		self.uartParityComboBox.setCurrentText('无')

		self.uartOutputTextEdit = QTextEdit()
		self.uartOutputTextEdit.setReadOnly(True)
		self.uartOutputTextEdit.setFont(QFont("Consolas", 10))

		self.uartOutputTextEditFontPtn = my_ptn('选择字体')
		self.uartOutputTextEditFontPtn.clicked.connect(
					self.uartOutputTextEditFontPtnClicked)

		self.uartOutputTextEditFontColorPtn = my_ptn('字体颜色')
		self.uartOutputTextEditFontColorPtn.clicked.connect(
					self.uartOutputTextEditFontColorPtnClicked)

		self.uartOutputTextEditBackgroundColorPtn = my_ptn('选择背景色')
		self.uartOutputTextEditBackgroundColorPtn.clicked.connect(
					self.uartOutputTextEditBackgroundColorPtnClicked)

		self.uartOutputTextEditAlignmentComboBox = QComboBox()
		self.uartOutputTextEditAlignmentComboBox.addItems([
			'左对齐', '居中对齐', '右对齐', '两端对齐'
		])
		self.uartOutputTextEditAlignmentComboBox.setCurrentIndex(0)
		self.uartOutputTextEditAlignmentComboBox.currentTextChanged.connect(
							self.uartOutputTextEditAlignmentComboBoxIndexChange)

		self.uartOutputTextEditBorderStyleComboBox = QComboBox()
		self.uartOutputTextEditBorderStyleComboBox.addItems([
			'无', '实线', '虚线', '点线', '双线'
		])

		color = "#F09E42"
		self.uartInputLineEdit = QLineEdit()
		self.uartInputLineEdit.installEventFilter(self)
		colorCss = 'background-color: {0}'.format(color)

		self.uartInputLineEdit.setStyleSheet(colorCss)
		#self.uartInputLineEdit.setStyleSheet(
		#	'''
		#	QLineEdit {
		#		background-color: #71FA9F
		#	}
		#	''')
		self.uartInputLineEdit.returnPressed.connect(self.sendCmd)

		self.uartInputCheckPtn = my_ptn('确认')
		self.uartInputCheckPtn.clicked.connect(lambda: self.sendCmd())

		self.uartOutputSavePtn = my_ptn('save output')

		self.uartOutputClearPtn = my_ptn('clear output')

		self.gridLayout.addWidget(self.uartOutputTextEditFontPtn, 0, 0, 1, 1)
		self.gridLayout.addWidget(self.uartOutputTextEditFontColorPtn, 0, 1, 1, 1)
		self.gridLayout.addWidget(self.uartOutputTextEditBackgroundColorPtn, 0, 2, 1, 1)
		self.gridLayout.addWidget(self.uartOutputTextEditAlignmentComboBox, 0, 3, 1, 1)
		self.gridLayout.addWidget(self.uartOutputTextEditBorderStyleComboBox, 0, 4, 1, 1)
		self.gridLayout.addWidget(self.uartOutputTextEdit, 1, 0, 6, 8)
		self.gridLayout.addWidget(self.uartOutputSavePtn, 5, 8, 1, 1)
		self.gridLayout.addWidget(self.uartOutputClearPtn, 5, 9, 1, 1)

		self.gridLayout.addWidget(self.uartInputLineEdit, 7, 0, 1, 9)
		self.gridLayout.addWidget(self.uartInputCheckPtn, 7, 9, 1, 1)

		self.gridLayout.addWidget(self.uartNameLbl, 0, 8, 1, 1, Qt.AlignmentFlag.AlignCenter)
		self.gridLayout.addWidget(self.uartNameComboBox, 0, 9, 1, 1)
		self.gridLayout.addWidget(self.uartBaudrateLbl, 1, 8, 1, 1, Qt.AlignmentFlag.AlignCenter)
		self.gridLayout.addWidget(self.uartBaudrateComboBox, 1, 9, 1, 1)
		self.gridLayout.addWidget(self.uartStopBitslbl, 2, 8, 1, 1, Qt.AlignmentFlag.AlignCenter)
		self.gridLayout.addWidget(self.uartStopBitsComboBox, 2, 9, 1, 1)
		self.gridLayout.addWidget(self.uartDataBitsLbl, 3, 8, 1, 1, Qt.AlignmentFlag.AlignCenter)
		self.gridLayout.addWidget(self.uartDataBitsComboBox, 3, 9, 1, 1)
		self.gridLayout.addWidget(self.uartParityLbl, 4, 8, 1, 1, Qt.AlignmentFlag.AlignCenter)
		self.gridLayout.addWidget(self.uartParityComboBox, 4, 9, 1, 1)

		row = 8
		column = 0
		for btn in self.ptnCmdList:
			btn.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
			btn.customContextMenuRequested.connect(self.showContextMenu)

			self.gridLayout.addWidget(btn, row, column, 1, 1)
			btn.clicked.connect(lambda: self.cmd_do_things())
			column += 1

			row = row + 1 if column == 10 else row
			column = 0 if column == 10 else column

	def uiCentralWidgetInit(self):
		self.centralWidget = QWidget()
		self.setCentralWidget(self.centralWidget)
		self.mainLayout = QVBoxLayout(self.centralWidget)

	def uiInit(self):
		self.setWindowTitle("SERIAL TOOL v0.0.1")
		self.setGeometry(300, 300, 1300, 800)

		self.setMouseTracking(True)

		self.uiCentralWidgetInit()
		self.uiMenuBarInit()
		self.uiToolBarInit()
		self.uiStatusBarInit()
		self.uiDockWidgetInit()
		self.uiGridLayoutInit()

		self.openFilePtn = my_ptn('bin file')
		self.openFilePtn.clicked.connect(lambda: self.file_open())

		self.openFilePathLbl = QLabel('未选择bin文件')

		self.loadFilePtn = my_ptn('load')
		self.loadFilePtn.clicked.connect(lambda: self.file_load())

		self.uartRefreshPtn = my_ptn('refresh')
		self.uartRefreshPtn.clicked.connect(lambda: self.serial_ports_refresh())

		self.topHboxLayout = QHBoxLayout()
		self.topHboxLayout.addWidget(self.openFilePtn)
		self.topHboxLayout.addWidget(self.openFilePathLbl)
		self.topHboxLayout.addStretch(4)
		self.topHboxLayout.addWidget(self.loadFilePtn)
		self.topHboxLayout.addWidget(self.uartRefreshPtn)

		self.mainLayout.addLayout(self.topHboxLayout)
		self.mainLayout.addLayout(self.gridLayout)

	def cmd_do_things(self):
		sender = self.sender() # same as button.text()
		# print(sys._getframe().f_code.co_name, 'sender is', sender.text())

		try:
			self.thread_serial_download.send_cmd(sender.text())
		except Exception as e:
			if self.thread_serial_download == None:
				QMessageBox().critical(self, 'error', 'please load bin file')
			elif self.port == None:
				QMessageBox().critical(self, 'error', 'please choose port')
			self.update_log(str(e) + '\n')

	def showContextMenu(self, position):
		sender = self.sender()

		# 创建上下文菜单
		menu = QMenu()
		edit_action = menu.addAction('编辑命令')

		action = menu.exec(sender.mapToGlobal(position))

		# 处理菜单选择
		if action == edit_action:
			# 创建输入对话框
			text, ok = QInputDialog.getText(
				self, '编辑命令', '输入新的命令', QLineEdit.EchoMode.Normal, sender.text())

			if ok and text:
				sender.setText(text)

	def navigate_history(self, direction):
		if not self.history:
			return

		# 更新历史索引
		self.inputHistoryIndex += direction

		# 限制索引范围
		if self.inputHistoryIndex < 0:
			self.inputHistoryIndex = 0
		if self.inputHistoryIndex > len(self.history):
			self.inputHistoryIndex = len(self.history)

		# 根据索引设置文本
		if self.inputHistoryIndex == len(self.history):
			self.uartInputLineEdit.clear()  # 显示当前输入
		else:
			self.uartInputLineEdit.setText(self.history[self.inputHistoryIndex])

	def eventFilter(self, obj, event):
		if obj == self.uartInputLineEdit and event.type() == event.Type.KeyPress:
			# 获取按下的键
			key = event.key()

			# 检测方向键
			if key == Qt.Key.Key_Up:
				# print("你按下了 上 方向键")
				self.navigate_history(-1)
				return True
			elif key == Qt.Key.Key_Down:
				# print("你按下了 下 方向键")
				self.navigate_history(1)
				return True
			# elif key == Qt.Key.Key_Left:
			# 	print("你按下了 左 方向键")
			# 	return True
			# elif key == Qt.Key.Key_Right:
			# 	print("你按下了 右 方向键")
			# 	return True
			elif event.key() == Qt.Key.Key_Return or event.key() == Qt.Key.Key_Enter:
				# 保存当前输入到历史记录
				text = self.uartInputLineEdit.text().strip()
				self.sendCmd()
				self.uartInputLineEdit.clear()
				if text:
					if len(self.history) == 0:
						self.history.append(text)
						self.inputHistoryIndex = len(self.history)
					else:
						if text != self.history[-1]:
							self.history.append(text)
							self.inputHistoryIndex = len(self.history)
					
					# print(self.history)

		# 其他事件继续正常处理
		return super().eventFilter(obj, event)

	def display_binary_file(self, data):
		self.bytes_per_line = 16
		hex_output = []

		# 逐行处理数据
		for i in range(0, len(data), self.bytes_per_line):
			line_data = data[i:i+self.bytes_per_line]
			
			# 生成十六进制表示
			hex_line = []
			for byte in line_data:
				hex_line.append('{0:02x}'.format(byte))
			# 补齐空格
			hex_line_str = ' '.join(hex_line).ljust(self.bytes_per_line * 3)
			hex_output.append(hex_line_str)

		# 显示结果
		self.uartOutputTextEdit.append('\n'.join(hex_output))

	def update_log(self, log):
		self.uartOutputTextEdit.moveCursor(QTextCursor.MoveOperation.End)
		self.uartOutputTextEdit.insertPlainText(log)
		self.uartOutputTextEdit.moveCursor(QTextCursor.MoveOperation.End)

	def stop_serial_thread(self, log):
		self.loadFilePtn.setText('load')
		self.thread_serial_download.stop()
		self.update_log(log)
		self.serial_ports_refresh()

	def serialReadThreadRun(self, is_test=False):
		self.update_log('thread start ...\n')

		if is_test == True:
			self.thread_serial_download = serialReadThread(None, self.port)
		else:
			self.thread_serial_download = serialReadThread(self.openFilePathLbl.text(), self.port)
	
		self.thread_serial_download.log.connect(self.update_log)
		self.thread_serial_download.start()
		self.loadFilePtn.setText('stop')

	def serialReadThreadStop(self):
		if self.thread_serial_download == None:
			return

		self.update_log('thread stop ...\n')

		if self.thread_serial_download.running == True:
			self.thread_serial_download.stop()

		self.thread_serial_download = None
		self.loadFilePtn.setText('load')

	def file_load(self):
		if self.loadFilePtn.text() == 'load':
			is_test = False
			if self.openFilePathLbl.text() == '未选择bin文件':
				reply = QMessageBox.question(self, 'info', 'bin is none, enter test mode?',
						QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No, QMessageBox.StandardButton.No)
				
				if reply == QMessageBox.StandardButton.Yes:
					is_test = True
				elif reply == QMessageBox.StandardButton.No:
					return

			if self.port == None:
				QMessageBox.critical(self, 'error', 'no port')
				return

			self.serialReadThreadRun(is_test=is_test)
		else:
			self.serialReadThreadStop()

	def file_open(self):
		bin_file_path, _ = QFileDialog.getOpenFileName(
			self, "选择BIN文件", "", "BIN文件 (*.bin);;所有文件 (*)")

		if bin_file_path:
			self.current_file = bin_file_path
			self.openFilePathLbl.setText(bin_file_path)
			self.statusBar().showMessage(bin_file_path)

			if not os.path.exists(os.path.join(self.current_file)):
				QMessageBox.critical(self, '错误', '找不到文件: {0}'.format(self.current_file))

			try:
				with open(self.current_file, 'rb') as file:
					self.display_binary_file(file.read())
				file.close()
			except Exception as e:
				QMessageBox.critical(self, '错误', '无法打开文件: {0}'.format(str(e)))

	def sendCmd(self):
		cmd = self.uartInputLineEdit.text()

		try:
			self.thread_serial_download.send_cmd(cmd)
		except Exception as e:
			errLog = 'internel error: ' + str(e) + '\n'
			self.update_log(errLog)

	def serial_ports_change(self):
		print('event: port name change')
		if self.uartNameComboBox.currentText() == '':
			print('uart port is None')
			return

		self.serialReadThreadStop()

		self.serial_ports_close()
		self.serial_ports_open()

	def serial_ports_baudrate_change(self):
		print('event: port baudrate change')
		port_name = self.uartNameComboBox.currentText()
		port_baudrate = self.uartBaudrateComboBox.currentText()
		if self.port != None:
			if port_name == self.port.port and port_baudrate == self.port.baudrate:
				print('port name and baudrate not change')
				return
			else:
				if port_name == self.port.port:
					print('{0}::{1} baudrate change to {0}::{2}'.format(self.port.port, self.port.baudrate, port_baudrate))
					self.port.change_baudrate(port_baudrate)
					return

		self.serial_ports_close()
		self.serial_ports_open()

	def serial_ports_close(self):
		if self.port != None:
			self.port.close()
			print('{0}::{1} close'.format(self.port.port, self.port.baudrate))

		self.port = None

	def serial_ports_open(self):
		port_name = self.uartNameComboBox.currentText()
		port_baudrate = self.uartBaudrateComboBox.currentText()

		if port_name == '' or port_baudrate == '':
			self.port.close() if self.port != None else None
			return

		self.port = updater_uart(port_name, port_baudrate)

		ret, err = self.port.open()
		if ret < 0:
			QMessageBox().critical(self, 'error', 'open {0}::{1} fail, {2}'.format(port_name, port_baudrate, err))
			print('{0}::{1} open fail, {2}'.format(port_name, port_baudrate, err))
			self.port = None
			return
		print('{0}::{1} open success'.format(port_name, port_baudrate))

	def serial_ports_refresh(self):
		ports = serial.tools.list_ports.comports()

		serial_ports = []

		if not ports:
			self.uartNameComboBox.clear()
			self.serial_ports = []
			return

		for port, desc, hwid in sorted(ports):
			if platform.system() == 'Windows' and not port.startswith('COM'):
				continue
			elif platform.system() == 'Linux' and not port.startswith('/dev/ttyUSB'):
				continue

			serial_ports.append(port)

			if port not in self.serial_ports:
				self.uartNameComboBox.addItem(port)
				print('port new {0}'.format(port))
				self.serial_ports.append(port)

		for port in self.serial_ports:
			if port not in serial_ports:
				self.uartNameComboBox.removeItem(self.uartNameComboBox.findText(port))
				self.serial_ports.remove(port)
				print('port remove {0}'.format(port))

	# def enterEvent(self, event):
	# 	print('enter event')
	# 	event.accept()

	def closeEvent(self, event):
		print('close event')

		if self.thread_serial_download != None and self.thread_serial_download.running == True:
			self.thread_serial_download.stop()

		event.accept()

if __name__ == "__main__":
	app = QApplication(sys.argv)
	app.setStyle('Fusion')

	window = serialToolMainWindow()
	window.show()
	sys.exit(app.exec())
