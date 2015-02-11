# -*- encoding: utf-8 -*-

@works32
@idempotent
Feature:    Load Holidays into the Accountants calendar
Run trytond_AccountantsCalendar.feature before this to create the calendar.
This isn't working really because we still don't have recurrence rules.

  Scenario: Set the default feature data for the Accountants calendar

# FixMe: This needs wiring up so that it's derived from the user
      Given Set the feature data with values
            | name                                  | value                    	|
            | user,Accountant,name                  | Accountant		    	|
            | user,Accountant,login                 | accountant               	|
            | user,Accountant,password              | accountant               	|
            | user,Accountant,email                 | accountant@example.com   	|

  Scenario: Create the holidays
    
      Given I need a set of "Holiday" annual events \
      	    in the calendar named "AccountantsCal" \
	    owned by the user named "Accountant" with fields:
            | name		   	  | date       	|
            | New Years                  | 2000-01-01 	|
            | Epiphany                   | 2000-01-06 	|
            | Assumption    		  | 2000-08-15 	|
            | Michaelmus    		  | 2000-09-29 	|
            | Christmas Eve 	  	  | 2000-12-24 	|
            | Christmas 	  	  | 2000-12-25 	|
            | St. Stephens 	  	  | 2000-12-26 	|

