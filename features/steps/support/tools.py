# -*- encoding: utf-8 -*-

"""
From OerpScenario support/tools.py
"""

import sys

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


