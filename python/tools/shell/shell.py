import os
import sys
import pdb
import logging
import subprocess

sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..'))

from tools.log.log import Logger

def run_shell(cmd: str, cwd: str = None, timeout: int = 3, logger = None) -> tuple[str, str]:

    process = subprocess.Popen(cmd, cwd=cwd,
                        stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                        encoding='gbk', errors='ignore', shell=True)
    try:
        out, err = process.communicate(timeout=timeout)
    
    except subprocess.TimeoutExpired:
        process.kill()
        out, err = 'shell timeout: {0}'.format(cmd), ''

    except Exception as e:
        process.kill()
        out, err = 'shell fail: {0}'.format(cmd), str(e)

    return out, err

def shell(cmd:str, cwd=None,timeout:int=3) -> str:
    out, _ = run_shell(cmd, cwd=cwd, timeout=timeout)
    return out

if __name__ == "__main__":
    print('Hello, Yue!')

    pdb.set_trace()

    logger = Logger(name='shell_test', to_console=True).get_logger()

    logger.info(shell('ipconfig'))
    logger.info(shell('date'))
