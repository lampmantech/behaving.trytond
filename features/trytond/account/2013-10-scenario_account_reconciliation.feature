# -*- encoding: utf-8 -*-

# These are straight cut-and-paste from Trytond doctests.
# It should be improved to be more like a Behave BDD.

Feature: Run the Trytond scenario_account_reconciliation doctests

   Scenario: Run the trytond_account-2.8.1/tests/scenario_account_reconciliation.rst

      Given Create database
        and we ensure that the "account" module is loaded
	and the "account" module is in the list of loaded modules
        and Install account
	and Create company
	and Reload the context
	and Create fiscal year
	and Create chart of accounts
        and Create parties
       Then there are some instances of "party.party"

      

