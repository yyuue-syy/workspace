import os
import re
import time
import logging
import datetime

from logging.handlers import TimedRotatingFileHandler
from typing import Optional

THIS_TIME = datetime.datetime.now().strftime('%Y_%m%d_%H%M%S')

"""
RootLogger 是 logging 中所有 Logger 的最终父级, 它没有名字(name 属性为空字符串 ''), 是整个 Logger 层级体系的根节点。
当通过 logging.getLogger(name) 创建任意 Logger 时:
    - 如果 name 是空字符串，返回的就是 RootLogger 实例;
    - 如果 name 是非空字符串（比如 'app'、'app.db'），返回的是普通 Logger 实例，且这个实例会隐式继承 RootLogger 的配置。

Logger 的继承关系是基于 '.' 分隔名称的, 如：
    - logging.getLogger('app') 的父级是 RootLogger;
    - logging.getLogger('app.db') 的父级是 logging.getLogger('app'), 最终父级是 RootLogger。

继承的核心作用：如果一个普通 Logger 没有设置 Handler / Level 等配置，它会向上委托给父级 Logger, 直到 RootLogger 处理日志。
"""

class YueLogger():
    def __init__(self, name: str = None, dir: str = None,level = logging.INFO,
                            to_file: bool = True, to_console: bool = False):

        self.dir        = dir if dir is not None else 'output/log'
        self.name       = name if name is not None else 'default'
        self.to_file    = to_file
        self.to_console = to_console

        self.fmt  = logging.Formatter('%(asctime)s %(levelname)s %(filename)15s%(funcName)15s: %(message)s')

        self.__fh = None
        self.__sh = None

        self.dir = os.path.join(os.getcwd(), self.dir).replace('\\', '/') \
            if os.path.isabs(self.dir) is False else self.dir

        self.log_file = self.dir + '/{0}/'.format(THIS_TIME) + self.name
        self.log_file += '.log'

        self.log_level = level

        print('log dir set to: {0}'.format(self.log_file))

        self.logger = logging.getLogger(name)
        self.logger.setLevel(level)

        self.file_handler_init()
        self.stream_handler_init()

    def file_handler_init(self):
        if not self.to_file:
            return

        if self.__fh is not None:
            return

        if not os.path.exists(os.path.dirname(self.log_file)):
            os.makedirs(os.path.dirname(self.log_file))

        self.__fh = logging.FileHandler(self.log_file, encoding='utf-8')
        self.__fh.setLevel(self.log_level)
        self.__fh.setFormatter(self.fmt)

        self.logger.addHandler(self.__fh)

    def stream_handler_init(self):
        if not self.to_console:
            return

        if self.__sh is not None:
            print('stream handler already exists')
            return

        self.__sh = logging.StreamHandler()
        self.__sh.setLevel(self.log_level)
        self.__sh.setFormatter(self.fmt)

        self.logger.addHandler(self.__sh)

    def get_logger(self):
        return self.logger

if __name__ == "__main__":
    logger1 = logging.getLogger()
    logger2 = logging.getLogger('test')

    logger1.info('111')
    print(logger1.parent)
    print(logger2.parent)
