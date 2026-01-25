import os
import re
import sys

from tools.log.log import Logger
from tools.config.ini import IniConfig
from tools.shell.shell import run_shell, shell

THIS_FILE_NAME = os.path.basename(__file__).split('.')[0]

logger = Logger(name=THIS_FILE_NAME, to_console=True).get_logger()

class Entry():
	def __init__(self):
		pass
		self.config = {}

	''' config api '''
	def config_init(self, path:str='config.ini'):
		self.ini = IniConfig(path)
		self.ini.init()
		self.ini.dump()

	def write_result_to_excel(self, file_path: str, data: list):
		pass

	def clean_cache():
		pass

def clean_cache():
	try:
		os.system('python -m pyclean .')
	except Exception as e:
		logger.error('clean cache failed: {0}'.format(e))

if __name__ == "__main__":
	print('Hello, Yue!')

	entry = Entry()
	entry.config_init('config/config.ini')

	#logger.info(shell('ipconfig'))
	#logger.info(shell('date'))

	print(entry.ini.get('SECTION1', 'param3'))

	os.chdir(os.getcwd())

	#clean_cache()
