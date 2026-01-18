import configparser
from os import path

class IniConfig:
	def __init__(self, file_path:str):
		if not path.exists(file_path):
			raise FileNotFoundError('Config file not found: {0}'.format(file_path))

		self.config = configparser.ConfigParser()
		self.config.read(file_path)

	def get(self, section: str, option: str) -> str:
		return self.config.get(section, option)
