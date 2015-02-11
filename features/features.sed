s/^[ 	]*Feature: */Feature:    /
s/^[ 	][ 	]*Scenario: */  Scenario: /
s/^[ 	][ 	]*Scenario Outline: */  Scenario Outline: /
s/^[ 	][ 	]*Examples: */  Examples: /
s/^[ 	][ 	]*[gG]iven */      Given /
s/^[ 	][ 	]*[tT]hen */       Then /
s/^[ 	][ 	]*[wW]hen */       When /
s/^[ 	][ 	]*[aA]nd */        And /
s/^[ 	][ 	]*[|] */            | /
s/[|] *$/	|/
