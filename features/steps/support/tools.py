# -*- mode: python; py-indent-offset: 4; coding: utf-8-unix; encoding: utf-8 -*-

"""
From OerpScenario support/tools.py
"""

import sys
import traceback
import pdb

__all__ = ['puts', 'vRestoreStdoutErr', 'set_trace_with_pdb', 'set_trace_with_pydbgr']    # + 20 'assert_*' 


# Expose assert* from unittest.TestCase with pep8 style names
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


def puts(*args):
    """
    Print the arguments, after the step is finished.
    """
    ctx = _get_context()
    if ctx:
        # Append to the list of messages
        ctx._messages.extend(args)
    else:
        # Context not found
        for arg in args:
            print(arg)

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

def set_trace_with_pydbgr():
    """Call pdb.set_trace in the caller's frame.
    
    First restore sys.stdout and sys.stderr.  Note that the streams are
    NOT reset to whatever they were before the call once pydbgr is done!
    """
    exc, tb = sys.exc_info()[1:]
    vRestoreStdoutErr()    
    output=sys.__stdout__
    output.flush()
    try:
        output.write(u'Invoking the interactive debugger pydbgr\n')
        output.flush()
        import pydbgr
        if tb:
            if isinstance(exc, AssertionError) and exc.args:
                # The traceback is not printed yet
                print_exc()
            pydbgr.post_mortem(exc)
        else:
            # FixMe: Is this right?
            pydbgr.post_mortem(exc, frameno=1)
    except Exception, e:
        sys.__stderr__.write(str(e))

def set_trace_with_pdb():
    """Call pdb.set_trace in the caller's frame.
    
    First restore sys.stdout and sys.stderr.  Note that the streams are
    NOT reset to whatever they were before the call once pdb is done!
    """
    exc, tb = sys.exc_info()[1:]
    vRestoreStdoutErr()    
    output=sys.__stdout__
    output.flush()
    try:
        output.write(u'Invoking the interactive debugger pdb\n')
        output.flush()
        if tb:
            if isinstance(exc, AssertionError) and exc.args:
                # The traceback is not printed yet
                print_exc()
            pdb.post_mortem(tb)
        else:
            pdb.Pdb().set_trace(sys._getframe().f_back)
    except Exception, e:
        sys.__stderr__.write(str(e))


# patch for stdlib cmd.py
import cmd
class Cmd(cmd.Cmd):
    """A simple framework for writing line-oriented command interpreters.
    """
    def onecmd(self, line):
        """Interpret the argument as though it had been typed in response
        to the prompt.

        This may be overridden, but should not normally need to be;
        see the precmd() and postcmd() methods for useful execution hooks.
        The return value is a flag indicating whether interpretation of
        commands by the interpreter should stop.

        """
        cmd, arg, line = self.parseline(line)
        if not line:
            return self.emptyline()
        if cmd is None:
            return self.default(line)
        self.lastcmd = line
        if cmd == '':
            return self.default(line)
        else:
            # Fixed: using hassatr helps reduce error stack pollution
            if not hasattr(self, 'do_' + cmd):
                return self.default(line)
            try:
                func = getattr(self, 'do_' + cmd)
            except AttributeError:
                return self.default(line)
            return func(arg)

class Pdb(pdb.Pdb):
    def __init__(self, **kw_args):
        pdb.Pdb.__init__(self, **kw_args)

    def onecmd(self, line):
        """Interpret the argument as though it had been typed in response
        to the prompt.

        Checks whether this line is typed at the normal prompt or in
        a breakpoint command list definition.
        """
        if not self.commands_defining:
            # Fixed: use our Cmd instead of cmd.Cmd
            return Cmd.onecmd(self, line)
        else:
            return self.handle_command_def(line)
    
def post_mortem(t=None):
    # handling the default
    if t is None:
        # sys.exc_info() returns (type, value, traceback) if an exception is
        # being handled, otherwise it returns None
        t = sys.exc_info()[2]
        if t is None:
            raise ValueError("A valid traceback must be passed if no " + \
                             "exception is being handled")

    p = Pdb()
    p.reset()
    p.interaction(None, t)

def pm():
    post_mortem(sys.last_traceback)

