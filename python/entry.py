import os
import re
import sys

from tools.log.log import Logger
from tools.config.ini import IniConfig
from tools.shell.shell import run_shell, shell

logger = Logger(name='entry', dir='log', to_console=True).get_logger()

class Entry():
	def __init__(self):
		pass
		self.config = {}

	''' config api '''
	def config_init(self, path:str='config.ini'):
		ini = IniConfig('path')

	def write_result_to_excel(self, file_path: str, data: list):
		pass

	def clean_cache():
		pass

if __name__ == "__main__":
	print('Hello, Yue!')

	entry = Entry()
	#entry.config_init('config.ini1')

	logger.info(shell('ipconfig'))
	logger.info(shell('date'))


	os.chdir(os.getcwd())
	os.system('pyclean .')
