
import re

from squad.plugins import Plugin as BasePlugin

MULTILINERS = [
    ('check-kernel-exception', r'-+\[? cut here \]?-+.*?-+\[? end trace \w* \]?-+'),
    ('check-kernel-kasan', r'=+\n\[[\s\.\d]+\]\s+BUG: KASAN:.*?=+'),
    ('check-kernel-kfence', r'=+\n\[[\s\.\d]+\]\s+BUG: KFENCE:.*?=+'),
]

ONELINERS = [
    ('check-kernel-oops', r'^[^\n]+Oops(?: -|:).*?$'),
    ('check-kernel-fault', r'^[^\n]+Unhandled fault.*?$'),
    ('check-kernel-warning', r'^[^\n]+WARNING:.*?$'),
    ('check-kernel-bug', r'^[^\n]+(?: kernel BUG at|BUG:).*?$'),
    ('check-kernel-invalid-opcode', r'^[^\n]+invalid opcode:.*?$'),
    ('check-kernel-panic', r'Kernel panic - not syncing.*?$'),
]

# Tip: broader regexes should come first
REGEXES = MULTILINERS + ONELINERS


class LogParserTestLib:

    @classmethod
    def cutoff_boot_log(self, log):
        # Attempt to split the log in " login:"
        logs = log.split(' login:', 1)

        # 1 string means no split was done, consider all logs as test log
        if len(logs) == 1:
            return '', log

        boot_log = logs[0]
        test_log = logs[1]
        return boot_log, test_log

    @classmethod
    def kernel_msgs_only(self, log):
        kernel_msgs = re.findall(r'(\[[ \d]+\.[ \d]+\] .*?)$', log, re.S | re.M)
        return '\n'.join(kernel_msgs)


class Plugin(BasePlugin):
    pass