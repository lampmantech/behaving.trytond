# -*- coding: utf-8 -*-
"""Enhancements for Behave.

Some of them might be proposed upstream
"""

import re
from behave import formatter
from behave import matchers
from behave import model
from behave import runner
from behave import parser

__all__ = ['patch_all']
_behave_patched = False


def patch_all():
    global _behave_patched
    if not _behave_patched:
        patch_matchers_get_matcher()
        patch_model_Table_raw()
#        formatter.formatters.register(PrettyFormatter)
        _behave_patched = True


def patch_matchers_get_matcher():
    # Detect the regex expressions
    # https://github.com/jeamland/behave/issues/73
    def get_matcher(func, string):
        if string[:1] == string[-1:] == '/':
            return matchers.RegexMatcher(func, string[1:-1])
        return matchers.current_matcher(func, string)
    matchers.get_matcher = get_matcher


def patch_model_Table_raw():
    # Add attribute Table.raw
    def raw(self):
        yield list(self.headings)
        for row in self.rows:
            yield list(row)
    model.Table.raw = property(raw)




# monkey patch Runner so that feature files are sorted
import os, sys
from behave.runner import exec_file
from behave import step_registry
def _patched_feature_files(self):
    files = []
    for path in self.config.paths:
        if os.path.isdir(path):
            for dirpath, dirnames, filenames in os.walk(path):
                dirnames.sort()
                for filename in sorted(filenames):
                    if filename.endswith('.feature'):
                        files.append(os.path.join(dirpath, filename))
        elif path.startswith('@'):
            files.extend([filename.strip() for filename in open(path)])
        elif os.path.exists(path):
            files.append(path)
        else:
            raise Exception("Can't find path: " + path)
    return files

def _patched_load_step_definitions(self, extra_step_paths=None):
    steps_dir = os.path.join(self.base_dir, 'steps')
    if extra_step_paths is None:
        extra_step_paths = []
        for path in self.config.paths[1:]:
            dirname = os.path.abspath(path)
            for dirname, subdirs, _fnames in os.walk(dirname):
                if 'steps' in subdirs:
                    extra_step_paths.append(os.path.join(dirname, 'steps'))
                    subdirs.remove('steps') # prune search
    # allow steps to import other stuff from the steps dir
    sys.path.insert(0, steps_dir)

    step_globals = {
        'step_matcher': matchers.step_matcher,
    }

    for step_type in ('given', 'when', 'then', 'step'):
        decorator = getattr(step_registry, step_type)
        step_globals[step_type] = decorator
        step_globals[step_type.title()] = decorator

    for path in [steps_dir] + list(extra_step_paths):
        for name in os.listdir(path):
            if name.endswith('.py'):
                exec_file(os.path.join(path, name), step_globals)

    # clean up the path
    sys.path.pop(0)


runner.Runner.feature_files = _patched_feature_files
runner.Runner.load_step_definitions = _patched_load_step_definitions

# trytond_scenari addition

def _parse_file(filename, language=None):
    with open(filename, 'rb') as f:
        # file encoding is assumed to be utf8. Oh, yes.
        data = f.read().decode('utf8')
    # change a trailing line backslash and space both sides of it into a space
    # this make it prettier to use long steps
    data = re.sub('\\s*\\\\\n\\s*', ' ', data)
    return parser.parse_feature(data, language, filename)

parser.parse_file = _parse_file
