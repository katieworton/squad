
import hashlib
import re
from squad.plugins import Plugin as BasePlugin


REGEX_NAME = 0
REGEX_BODY = 1


class LogParserLib:
    @classmethod
    def compile_regexes(self, regexes):
        combined = [r"(%s)" % r[REGEX_BODY] for r in regexes]
        return re.compile(r"|".join(combined), re.S | re.M)

    @classmethod
    def create_shasum(self, snippet):
        sha = hashlib.sha256()
        without_numbers = re.sub(r'(0x[a-f0-9]+|[<\[][0-9a-f]+?[>\]]|\d+)', '', snippet)
        without_time = re.sub(r'^\[[^\]]+\]', '', without_numbers)
        sha.update(without_time.encode())
        return sha.hexdigest()

    @classmethod
    def join_matches(self, matches, regexes):
        """
            group regex in python are returned as a list of tuples which each
            group match in one of the positions in the tuple. Example:
            regex = r'(a)|(b)|(c)'
            matches = [
                ('match a', '', ''),
                ('', 'match b', ''),
                ('match a', '', ''),
                ('', '', 'match c')
            ]
        """
        snippets = {regex_id: [] for regex_id in range(len(regexes))}
        for match in matches:
            for regex_id in range(len(regexes)):
                if len(match[regex_id]) > 0:
                    snippets[regex_id].append(match[regex_id])
        return snippets

    @classmethod
    def parse_log(self, log, regexes):
        regex = LogParserLib.compile_regexes(regexes)
        matches = regex.findall(log)
        snippets = LogParserLib.join_matches(matches, regexes)

        return snippets


class Plugin(BasePlugin):
    pass