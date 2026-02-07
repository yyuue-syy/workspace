#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <sys/socket.h>
#include <linux/netlink.h>

#define NETLINK_USER 30
#define MAX_PAYLOAD 1024

// 消息处理函数
void handle_netlink_message(char *msg, int len) {
	printf("收到Netlink消息: %.*s\n", len, msg);

	if (strstr(msg, "LED_ON")) {
		printf("case1\n");
	} else if (strstr(msg, "LED_OFF")) {
		printf("case2\n");
	} else {

	}
}

int main(int argc, char *argv[])
{
	printf("Hello youyu!\n");

	while(1) {

	}

	return 0;
}
