import os
import sys
import pdb
import subprocess

from tools.log.log import Logger

def run_shell(cmd:str, cwd=None, timeout:int=3, logger:Logger=None) -> tuple[str, str]:
	process = subprocess.Popen(cmd, cwd=cwd,
		stdout=subprocess.PIPE, stderr=subprocess.PIPE,
		encoding='gbk', errors='ignore',
		shell=True)

	try:
		out, err = process.communicate(timeout=timeout)
	except Exception as e:
		process.kill()
		out, err = 'shell fail: {0}'.format(cmd), str(e)

	return out, err

def shell(cmd:str, cwd=None,timeout:int=3) -> str:
	out, _ = run_shell(cmd, cwd=cwd, timeout=timeout)
	return out
