# -*- encoding: utf-8 -*-
"""
This is the elementary behave test from its tutorial;
see http://pythonhosted.org/behave/ or the docs/
directory in the behave source distribion.

If this test fails, behave is not properly installed.
"""

from behave import *

@given('we have behave installed')
def step_impl(context):
    pass

@when('we implement a test')
def step_impl(context):
    assert True is not False

@then('behave will test it for us!')
def step_impl(context):
    assert context.failed is False

