# -*- encoding: utf-8 -*-

# This is the elementary behave test from its tutorial.
# If this test fails, behave is not properly installed.
# See http://pypi.python.org/pypi/behave

@works32
Feature: showing off behave

   Scenario: run a simple test
      Given we have behave installed
       when we implement a test
       then behave will test it for us!

