# -*- encoding: utf-8 -*-

@works32 @works34 @works36
Feature: Behave - Behavior-driven development
Behavior-driven development (or BDD) is an agile software development
technique that encourages collaboration between developers, QA and
non-technical or business participants in a software project. 

BDD focuses on obtaining a clear understanding of desired software
behavior through discussion with stakeholders. It extends TDD by
writing test cases in a natural language that non-programmers can read.
Behavior-driven developers use their native language in combination
with the ubiquitous language of domain-driven design to describe the
purpose and benefit of their code. This allows the developers to focus
on why the code should be created, rather than the technical details,
and minimizes translation between the technical language in which the
code is written and the domain language spoken by the business, users,
stakeholders, project management, etc.

The Python package is available at https://pypi.python.org/pypi/behave
and complete documentation can be found at http://pythonhosted.org/behave/

  Scenario: To see the options to running behave, type behave --help
  """
Run a number of feature tests with behave.

positional arguments:
  paths                 Feature directory, file or file location (FILE:LINE).

optional arguments:
  -h, --help            show this help message and exit
  -c, --no-color        Disable the use of ANSI color escapes.
  --color               Use ANSI color escapes. This is the default behaviour.
                        This switch is used to override a configuration file
                        setting.
  -d, --dry-run         Invokes formatters without executing the steps.
  -D NAME=VALUE, --define NAME=VALUE
                        Define user-specific data for the config.userdata
                        dictionary. Example: -D foo=bar to store it in
                        config.userdata["foo"].
  -e PATTERN, --exclude PATTERN
                        Don't run feature files matching regular expression
                        PATTERN.
  -i PATTERN, --include PATTERN
                        Only run feature files matching regular expression
                        PATTERN.
  --no-junit            Don't output JUnit-compatible reports.
  --junit               Output JUnit-compatible reports. When junit is
                        enabled, all stdout and stderr will be redirected and
                        dumped to the junit report, regardless of the '--
                        capture' and '--no-capture' options.
  --junit-directory PATH
                        Directory in which to store JUnit reports.
  -f FORMAT, --format FORMAT
                        Specify a formatter. If none is specified the default
                        formatter is used. Pass '--format help' to get a list
                        of available formatters.
  --steps-catalog       Show a catalog of all available step definitions. SAME
                        AS: --format=steps.catalog --dry-run --no-summary -q
  -k, --no-skipped      Don't print skipped steps (due to tags).
  --show-skipped        Print skipped steps. This is the default behaviour.
                        This switch is used to override a configuration file
                        setting.
  --no-snippets         Don't print snippets for unimplemented steps.
  --snippets            Print snippets for unimplemented steps. This is the
                        default behaviour. This switch is used to override a
                        configuration file setting.
  -m, --no-multiline    Don't print multiline strings and tables under steps.
  --multiline           Print multiline strings and tables under steps. This
                        is the default behaviour. This switch is used to
                        override a configuration file setting.
  -n NAME, --name NAME  Only execute the feature elements which match part of
                        the given name. If this option is given more than
                        once, it will match against all the given names.
  --no-capture          Don't capture stdout (any stdout output will be
                        printed immediately.)
  --capture             Capture stdout (any stdout output will be printed if
                        there is a failure.) This is the default behaviour.
                        This switch is used to override a configuration file
                        setting.
  --no-capture-stderr   Don't capture stderr (any stderr output will be
                        printed immediately.)
  --capture-stderr      Capture stderr (any stderr output will be printed if
                        there is a failure.) This is the default behaviour.
                        This switch is used to override a configuration file
                        setting.
  --no-logcapture       Don't capture logging. Logging configuration will be
                        left intact.
  --logcapture          Capture logging. All logging during a step will be
                        captured and displayed in the event of a failure. This
                        is the default behaviour. This switch is used to
                        override a configuration file setting.
  --logging-level LOGGING_LEVEL
                        Specify a level to capture logging at. The default is
                        INFO - capturing everything.
  --logging-format LOGGING_FORMAT
                        Specify custom format to print statements. Uses the
                        same format as used by standard logging handlers. The
                        default is '%(levelname)s:%(name)s:%(message)s'.
  --logging-datefmt LOGGING_DATEFMT
                        Specify custom date/time format to print statements.
                        Uses the same format as used by standard logging
                        handlers.
  --logging-filter LOGGING_FILTER
                        Specify which statements to filter in/out. By default,
                        everything is captured. If the output is too verbose,
                        use this option to filter out needless output.
                        Example: --logging-filter=foo will capture statements
                        issued ONLY to foo or foo.what.ever.sub but not foobar
                        or other logger. Specify multiple loggers with comma:
                        filter=foo,bar,baz. If any logger name is prefixed
                        with a minus, eg filter=-foo, it will be excluded
                        rather than included.
  --logging-clear-handlers
                        Clear all other logging handlers.
  --no-summary          Don't display the summary at the end of the run.
  --summary             Display the summary at the end of the run.
  -o FILE, --outfile FILE
                        Write to specified file instead of stdout.
  -q, --quiet           Alias for --no-snippets --no-source.
  -s, --no-source       Don't print the file and line of the step definition
                        with the steps.
  --show-source         Print the file and line of the step definition with
                        the steps. This is the default behaviour. This switch
                        is used to override a configuration file setting.
  --stage STAGE         Defines the current test stage. The test stage name is
                        used as name prefix for the environment file and the
                        steps directory (instead of default path names).
  --stop                Stop running tests at the first failure.
  -t TAG_EXPRESSION, --tags TAG_EXPRESSION
                        Only execute features or scenarios with tags matching
                        TAG_EXPRESSION. Pass '--tags-help' for more
                        information.
  -T, --no-timings      Don't print the time taken for each step.
  --show-timings        Print the time taken, in seconds, of each step after
                        the step has completed. This is the default behaviour.
                        This switch is used to override a configuration file
                        setting.
  -v, --verbose         Show the files and features loaded.
  -w, --wip             Only run scenarios tagged with "wip". Additionally:
                        use the "plain" formatter, do not capture stdout or
                        logging output and stop at the first failure.
  -x, --expand          Expand scenario outline tables in output.
  --lang LANG           Use keywords for a language other than English.
  --lang-list           List the languages available for --lang.
  --lang-help LANG      List the translations accepted for one language.
  --tags-help           Show help for tag expressions.
  --version             Show version.
  """

      Given we have behave installed
       When we implement a test
       Then behave will test it for us!

