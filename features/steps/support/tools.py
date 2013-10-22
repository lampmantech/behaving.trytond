# -*- encoding: utf-8 -*-

"""
From OerpScenario support/tools.py
"""

import sys
import traceback

__all__ = ['puts', 'set_trace']    # + 20 'assert_*' helpers

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
    """Print the arguments, after the step is finished."""
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
        import pdb
        if tb:
            if isinstance(exc, AssertionError) and exc.args:
                # The traceback is not printed yet
                print_exc()
            pdb.post_mortem(tb)
        else:
            pdb.Pdb().set_trace(sys._getframe().f_back)
    except Exception, e:
        sys.__stderr__.write(str(e))


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
