import logging

from collections import defaultdict
from squad.plugins import Plugin as BasePlugin
from squad.core.models import SuiteMetadata
from squad.plugins.log_parser_lib import LogParserLib, REGEX_NAME
from squad.plugins.log_parser_test_lib import REGEXES, LogParserTestLib

logger = logging.getLogger()


class Plugin(BasePlugin):

    def __create_tests(self, testrun, suite, test_name, lines):
        """
        There will be at least one test per regex. If there were any match for a given
        regex, then a new test will be generated using test_name + shasum. This helps
        comparing kernel logs accross different builds
        """
        metadata, _ = SuiteMetadata.objects.get_or_create(suite=suite.slug, name=test_name, kind='test')
        testrun.tests.create(
            suite=suite,
            result=(len(lines) == 0),
            log='\n'.join(lines),
            metadata=metadata,
            build=testrun.build,
            environment=testrun.environment,
        )

        # Some lines of the matched regex might be the same, and we don't want to create
        # multiple tests like test1-sha1, test1-sha1, etc, so we'll create a set of sha1sums
        # then create only new tests for unique sha's
        shas = defaultdict(set)
        for line in lines:
            sha = LogParserLib.create_shasum(line)
            shas[sha].add(line)

        for sha, lines in shas.items():
            name = f'{test_name}-{sha}'
            metadata, _ = SuiteMetadata.objects.get_or_create(suite=suite.slug, name=name, kind='test')
            testrun.tests.create(
                suite=suite,
                result=False,
                log='\n---\n'.join(lines),
                metadata=metadata,
                build=testrun.build,
                environment=testrun.environment,
            )

    def postprocess_testrun(self, testrun):
        if testrun.log_file is None:
            return

        boot_log, test_log = LogParserTestLib.cutoff_boot_log(testrun.log_file)
        logs = {
            'boot': boot_log,
            'test': test_log,
        }

        for log_type, log in logs.items():
            log = LogParserTestLib.kernel_msgs_only(log)
            suite, _ = testrun.build.project.suites.get_or_create(slug=f'log-parser-{log_type}')

            regex = LogParserLib.compile_regexes(REGEXES)
            matches = regex.findall(log)
            snippets = LogParserLib.join_matches(matches, REGEXES)

            for regex_id in range(len(REGEXES)):
                test_name = REGEXES[regex_id][REGEX_NAME]
                self.__create_tests(testrun, suite, test_name, snippets[regex_id])
