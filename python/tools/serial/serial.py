import os
import sys
import threading

try:
    import serial
except:
    os.system('python -m pip install pyserial')

from typing import NamedTuple

class SerialConfig(NamedTuple):
    port      : str
    baudrate  : int
    descript  : str

class SerialData(NamedTuple):
    config    : SerialConfig
    init      : bool
    error     : bool

class YueSerial():
    def __init__(self, config: SerialConfig):
        pass
