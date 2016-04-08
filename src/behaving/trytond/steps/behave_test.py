# -*- mode: python; py-indent-offset: 4; coding: utf-8-unix; encoding: utf-8 -*-
"""
This is the elementary behave test from its tutorial;
see http://pythonhosted.org/behave/ or the docs/
directory in the behave source distribion.

If this test fails, behave is not properly installed.
"""

from behave import *

@step('we have behave installed')
def step_impl(context):
    """
    If behave is not installed we couldnt get here!
    """
    pass

@step('we implement a test')
def step_impl(context):
    """
    A trivial assertion.
    """
    assert True is not False

@step('behave will test it for us!')
def step_impl(context):
    """
    The trivial assertion did not fail.
    """
    assert context.failed is False
