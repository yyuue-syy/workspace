#!/bin/bash

# 遇到错误立刻退出
set -e

# 未定义变量报错
set -u

# 开启调试模式，显示执行的命令
#set -x

# 帮助信息
show_help() {
	cat << EOF
usage: $0 {kernel|user|}

cmd:
  kernel          编译内核驱动
  kernel_clean    清理内核驱动编译产物
  user            编译用户态程序
  copy            拷贝编译产物到目标位置

example:
  $0 kernel
EOF
}

build_user() {
	cd user
	gcc -o youyu_app youyu.c
}

build_kernel() {
	cd kernel
	make
}

clean_kernel() {
	cd kernel
	make clean
}

case "${1:-}" in
	kernel)
		echo "building kernel..."
		build_kernel
		;;
	kernel_clean)
		echo "cleaning kernel..."
		clean_kernel
		;;
	user)
		echo "building user space..."
		build_user
		;;
	copy)
		echo "copy output..."
		;;
	help|--help|-h)
		show_help
		exit 0
		;;
	"") # 参数缺失、显式传 ""
		show_help
		exit 1
		;;
	*) # default
		echo "error: unknown command '$1'"
		echo "cmd: start, stop, restart, status, backup"
		exit 1
		;;
esac

exit 0
