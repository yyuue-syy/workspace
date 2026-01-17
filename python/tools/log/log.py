import os
import re
import time
import datetime

from logging import Logger
from logging.handlers import TimedRotatingFileHandler
from typing import Optional

import logging

cur_time = datetime.datetime.now().strftime('%Y-%m-%d_%H-%M-%S')

class Logger:
	def __init__(self, name='app_logger', log_file='app.log', level=logging.INFO):
		self.logger = logging.getLogger(name)
		self.logger.setLevel(level)

		# Create file handler which logs even debug messages
		fh = logging.FileHandler(log_file)
		fh.setLevel(level)

		# Create console handler with a higher log level
		ch = logging.StreamHandler()
		ch.setLevel(logging.ERROR)

		# Create formatter and add it to the handlers
		formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
		fh.setFormatter(formatter)
		ch.setFormatter(formatter)

	def add_file_handler(self, log_file: str, when: str = 'midnight', interval: int = 1, backup_count: int = 7):
		handler = TimedRotatingFileHandler(log_file, when=when, interval=interval, backupCount=backup_count)
		handler.setLevel(self.logger.level)
		formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
		handler.setFormatter(formatter)
		self.logger.addHandler(handler)

	def get_logger(self):
		return self.logger
