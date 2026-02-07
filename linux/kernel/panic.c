#include <linux/module.h>
#include <linux/kernel.h>
#include <linux/panic_notifier.h>
#include <linux/reboot.h>
#include <linux/delay.h>

#ifndef pr_fmt
#define pr_fmt(fmt) "[yuyue27]:" fmt
#else
#undef pr_fmt
#define pr_fmt(fmt) "[yuyue27]:" fmt
#endif

static int panic_notify_callback(struct notifier_block *nb, unsigned long action, void *data)
{
	pr_info("enter ==>\n");

	return NOTIFY_OK;
}

static struct notifier_block panic_nb = {
	.notifier_call = panic_notify_callback,
	.priority = INT_MAX,
};

static int __init panic_notify_init(void)
{
	int ret;
 
	ret = atomic_notifier_chain_register(&panic_notifier_list, &panic_nb);
	if (ret != 0) {
		pr_err("Failed to register panic notify! ret=%d\n", ret);
		return ret;
	}

	pr_info("enter ==>\n");
	return 0;
}

static void __exit panic_notify_exit(void)
{
	atomic_notifier_chain_unregister(&panic_notifier_list, &panic_nb);
	pr_info("enter ==>\n");
}

module_init(panic_notify_init);
module_exit(panic_notify_exit);

MODULE_LICENSE("GPL");	
MODULE_AUTHOR("yuyue27");
MODULE_DESCRIPTION("Raspberry Pi 5 Panic Notify Kernel Module");
MODULE_VERSION("1.0");
