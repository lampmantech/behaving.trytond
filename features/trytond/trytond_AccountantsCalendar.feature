# -*- encoding: utf-8 -*-

@works32
@idempotent
Feature: Create an Accountant user and give him a calendar

    Scenario: Create an Accountant user for various things

       Given Ensure that the "calendar" module is loaded
         and Ensure that the "party_vcarddav" module is loaded
         and Create a user named "Accountant" with the fields:
	  | name	| value		  		|
	  | login	| accountant	  		|
	  | password	| accountant			|
	  | email	| accountant@example.com	|

    Scenario: Set the Accountant feature data

# FixMe: This needs wiring up so that it's derived from the user
       Given Set the feature data with values
         | name                                  | value                    |
         | user,Accountant,name                  | Accountant		    |
         | user,Accountant,login                 | accountant               |
         | user,Accountant,password              | accountant               |
         | user,Accountant,email                 | accountant@example.com   |

    Scenario: Create the calendar

       Given Create a calendar named "AccountantsCal" owned by the user "Accountant"

