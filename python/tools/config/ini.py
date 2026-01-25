import os
import sys
import pdb
import configparser

from tools.log.log import Logger

THIS_FILE_NAME = os.path.basename(__file__).split('.')[0]

logger = Logger(name=THIS_FILE_NAME, to_console=True).get_logger()

class IniConfig:
	def __init__(self, file_path:str):
		self.file_path = file_path
		self.inited = False

		self.config = {
			'string': {},
			'integer': {},
			'float': {},
			'boolean': {}
		}

	def __is_init(self) -> bool:
		return self.inited

	def init(self):
		self.config = configparser.ConfigParser()
		self.config.read(self.file_path, encoding='gbk')

		self.inited = True

	def dump(self):
		if not self.__is_init():
			logger.info('ini not initialized')
			return

		for section in self.config.sections():
			logger.info('[{0}]'.format(section))
			for option in self.config.options(section):
				logger.info('    {0} = {1}'.format(option, self.config.get(section, option)))

	def get(self, section: str, option: str) -> str:
		if not self.__is_init():
			logger.info('ini not initialized')
			return None

		return self.config.get(section, option)

	#def get_config(self, config):
	#	return self.config.get(config)

	def write(self, config, value:str):
		'''
		write back to .ini
		'''

		if not self.__is_init():
			logger.info('ini not initialized')
			return None
