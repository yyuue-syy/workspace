import os
import toml
import sys
import pdb

from tools.log.log import YueLogger

THIS_FILE_NAME = os.path.basename(__file__).split('.')[0]

logger = YueLogger(name=THIS_FILE_NAME, to_console=True).get_logger()

class TomlParser:
    def __init__(self, file_path:str):
        self.file_path = file_path
        self.inited = False

    def init(self):
        with open(self.file_path, 'r', encoding='utf-8') as f:
            self.config = toml.load(f)

        self.inited = True

    def dump(self):
        if not self.inited:
            logger.error('TomlParser not inited!')
            return

        for section, params in self.config.items():
            for key, value in params.items():
                logger.info('TOML Config - [{0}] {1} = {2}'.format(section, key, value))
                yield (section, key, value)

        #logger.info('TOML Config Dump:')
        #for section, params in self.config.items():
        #    logger.info('[{0}]'.format(section))
        #    for key, value in params.items():
        #        logger.info('  {0} = {1}'.format(key, value))
