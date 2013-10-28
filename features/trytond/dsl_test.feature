# -*- encoding: utf-8 -*-

# This is the advanced syntax behave test of trytond.
# This test  is not properly finished yet.

Feature: showing off trytond dsl from OpenERPScenario

   Scenario: run a simple test with the party module and an instance with a full_name
      Given Ensure that the "party" module is loaded
        and I need a "party.party" with name: MyParty
        and having
	    | name	| value		| 
	    | full_name | My Party 	|
       then there are some instances of "party.party"
