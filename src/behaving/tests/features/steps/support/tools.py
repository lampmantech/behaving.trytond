# -*- mode: python; py-indent-offset: 4; coding: utf-8-unix; encoding: utf-8 -*-

"""
From OerpScenario support/tools.py
"""

import sys
import traceback
import datetime
import pdb

TODAY = datetime.date.today()

__all__ = ['model', 'puts', 'set_trace', 'vRestoreStdoutErr', 'set_trace_with_pdb', 'set_trace_with_pydbgr', 'oDateFromUDate']


from unittest2 import TestCase
ut = type('unittest', (TestCase,), {'any': any})('any')
for oper in ('equal', 'not_equal', 'true', 'false', 'is', 'is_not', 'is_none',
             'is_not_none', 'in', 'not_in', 'is_instance', 'not_is_instance',
             'raises', 'almost_equal', 'not_almost_equal', 'sequence_equal',
             'greater', 'greater_equal', 'less', 'less_equal'):
    funcname = 'assert_' + oper
    globals()[funcname] = getattr(ut, 'assert' + oper.title().replace('_', ''))
    __all__.append(funcname)
del TestCase, ut, oper, funcname

def print_exc():
    """Print exception, and its relevant stack trace."""
    tb = sys.exc_info()[2]
    length = 0
    while tb and '__unittest' not in tb.tb_frame.f_globals:
        length += 1
        tb = tb.tb_next
    traceback.print_exc(limit=length)


# -------
# HELPERS
# -------

def _get_context(level=2):
    caller_frame = sys._getframe(level)
    while caller_frame:
        try:
            # Find the context in the caller's frame
            varname = caller_frame.f_code.co_varnames[0]
            ctx = caller_frame.f_locals[varname]
            if ctx._is_context:
                return ctx
        except Exception:
            pass
        # Go back in the stack
        caller_frame = caller_frame.f_back


def model(name):
    """Return an erppeek.Model instance."""
    ctx = _get_context()
    return ctx and ctx.client.model(name)


def puts(*args):
    """Print the arguments, after the step is finished."""
    ctx = _get_context()
    if ctx:
        # Append to the list of messages
        ctx._messages.extend(args)
    else:
        # Context not found
        for arg in args:
            print(arg)


# From 'nose.tools': https://github.com/nose-devs/nose/tree/master/nose/tools


def vRestoreStdoutErr ():
    for stream in 'stdout', 'stderr':
        output = getattr(sys, stream)
        orig_output = getattr(sys, '__%s__' % stream)
        if output != orig_output:
            # Flush the output before entering pdb
            if hasattr(output, 'getvalue'):
                orig_output.write(output.getvalue())
                orig_output.flush()
            setattr(sys, stream, orig_output)

class MyPdb(pdb.Pdb):
    def __init__(self, **kw_args):
        pdb.Pdb.__init__(self, **kw_args)

    def handle_command_def(self,line):
        """Handles one command line during command list definition."""
        cmd, arg, line = self.parseline(line)
        if not cmd:
            return
        if cmd == 'silent':
            self.commands_silent[self.commands_bnum] = True
            return # continue to handle other cmd def in the cmd list
        elif cmd == 'end':
            self.cmdqueue = []
            return 1 # end of cmd list
        cmdlist = self.commands[self.commands_bnum]
        if arg:
            cmdlist.append(cmd+' '+arg)
        else:
            cmdlist.append(cmd)
        # Determine if we must stop
        if hasattr(self, 'do_' + cmd):
            func = getattr(self, 'do_' + cmd)
        else:
            func = self.default
        # one of the resuming commands
        if func.func_name in self.commands_resuming:
            self.commands_doprompt[self.commands_bnum] = False
            self.cmdqueue = []
            return 1
        return

def post_mortem(t=None):
    # handling the default
    if t is None:
        # sys.exc_info() returns (type, value, traceback) if an exception is
        # being handled, otherwise it returns None
        t = sys.exc_info()[2]
        if t is None:
            raise ValueError("A valid traceback must be passed if no "
                                               "exception is being handled")

    p = MyPdb()
    p.reset()
    p.interaction(None, t)

def pm():
    post_mortem(sys.last_traceback)

def set_trace():
    """Call pdb.set_trace in the caller's frame.

    First restore sys.stdout and sys.stderr.  Note that the streams are
    NOT reset to whatever they were before the call once pdb is done!
    """
    import pdb
    for stream in 'stdout', 'stderr':
        output = getattr(sys, stream)
        orig_output = getattr(sys, '__%s__' % stream)
        if output != orig_output:
            # Flush the output before entering pdb
            if hasattr(output, 'getvalue'):
                orig_output.write(output.getvalue())
                orig_output.flush()
            setattr(sys, stream, orig_output)
    exc, tb = sys.exc_info()[1:]
    if tb:
        if isinstance(exc, AssertionError) and exc.args:
            # The traceback is not printed yet
            print_exc()
        pdb.post_mortem(tb)
    else:
        pdb.Pdb().set_trace(sys._getframe().f_back)


def set_trace_with_pdb():
    return set_trace()

def set_trace_with_pydbgr():
    return set_trace()

# misc convenience funtions
def oDateFromUDate(uDate):
    if uDate.lower() == 'today' or uDate.lower() == 'now':
        oDate = TODAY
    else:
        oDate = datetime.date(*map(int, uDate.split('-')))
    return oDate
