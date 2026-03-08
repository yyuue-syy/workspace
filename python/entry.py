import os
import re
import sys

from tools.log.log import YueLogger
from tools.shell.shell import run_shell, shell

from tools.config.ini_parser import IniConfig
from tools.config.toml_parser import TomlParser

THIS_FILE_NAME = os.path.basename(__file__).split('.')[0]

logger = YueLogger(name=THIS_FILE_NAME, to_console=True).get_logger()

class Entry():
    def __init__(self):
        pass
        self.config = {}

        self.config_ini = None
        self.config_json = None
        self.config_toml = None

    ''' ini config api '''
    def config_init(self, path:str='config.ini', config_type:str='ini'):
        if config_type == 'ini':
            self.config_ini = IniConfig(path)
            self.config_ini.init()
            self.config_ini.dump()
        elif config_type == 'json':
            pass
        elif config_type == 'toml':
            self.toml_parser = TomlParser(path)
            self.toml_parser.init()
            self.toml_parser.dump()

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
    # entry.config_init('config/config.ini', config_type='ini')
    entry.config_init('config/config.toml', config_type='toml')

    #logger.info(shell('ipconfig'))
    #logger.info(shell('date'))

    os.chdir(os.getcwd())

    #clean_cache()
