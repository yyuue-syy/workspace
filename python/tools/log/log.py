import os
import re
import time
import logging
import datetime

from logging import Logger
from logging.handlers import TimedRotatingFileHandler
from typing import Optional

THIS_TIME = datetime.datetime.now().strftime('%Y_%m%d_%H%M%S')
DEFAULT_LOG_NAME = 'app.log'
DEFAULT_LOG_DIR = 'log'

class Logger():
	def __init__(self, name=None, dir:str=None, level=logging.INFO, to_file=True, to_console=False):
		self.dir = dir if dir else DEFAULT_LOG_DIR
		self.name = name if name else DEFAULT_LOG_NAME
		self.fmt = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
		self.fh = None
		self.sh = None
		
		self.dir = os.path.join(os.getcwd(), self.dir).replace('\\', '/') \
			if os.path.isabs(self.dir) is False else self.dir

		self.log_file = self.dir + '/{0}/'.format(THIS_TIME) + self.name
		self.log_file += '.log'

		self.log_level = level

		print('log dir set to: {0}'.format(self.log_file))

		self.logger = logging.getLogger(name)
		self.logger.setLevel(level)

		self.add_file_handler() if to_file else None
		self.add_stream_handler() if to_console else None

	def add_file_handler(self):
		if not os.path.exists(os.path.dirname(self.log_file)):
			os.makedirs(os.path.dirname(self.log_file))

		self.fh = logging.FileHandler(self.log_file, encoding='utf-8')
		self.fh.setLevel(self.log_level)
		self.fh.setFormatter(self.fmt)

		self.logger.addHandler(self.fh)

	def add_stream_handler(self):
		self.sh = logging.StreamHandler()
		self.sh.setLevel(self.log_level)
		self.sh.setFormatter(self.fmt)

		self.logger.addHandler(self.sh)

	def get_logger(self):
		return self.logger
