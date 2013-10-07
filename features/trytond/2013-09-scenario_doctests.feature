# -*- encoding: utf-8 -*-

# These are straight cut-and-paste from Trytond doctests.
# It should be improved to be more like a Behave BDD.

Feature: Run the Trytond scenario doctests

   Scenario: Run the company creation boilerplate (e.g. from
   trytond_account-2.8.1/tests/scenario_account_reconciliation.rst )

      Given Create database
        and Install account
	and Create company
	and Reload the context
	and Create fiscal year
