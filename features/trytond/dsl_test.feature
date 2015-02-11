# -*- encoding: utf-8 -*-
    
@works32
Feature:    showing off trytond dsl from OpenERPScenario
This is the monkey-patched syntax of behave The change is to change
a trailing line backslash and space both sides of it into a space.
This make it prettier to use long steps.

  Scenario: run a test of our behave monkey-patching for backslashes
      Given Ensure that the "party" module is loaded
        And I need a "party.party" \
	    with name: MyParty
        And having
            | name	| value			|
            | full_name | My Party 		|
       Then there are some instances of "party.party"
