# -*- encoding: utf-8 -*-

# These are straight cut-and-paste from Trytond doctests.
# It should be improved to be more like a Behave BDD.

@works32
Feature: Run the Trytond scenario doctests (e.g. from
   trytond_account-2.8.1/tests/scenario_account_reconciliation.rst )

   Scenario: Run the company creation boilerplate

      Given Ensure that the "account" module is loaded
	and Set the default feature data
	and Create the Company with default COMPANY_NAME and Currency code "EUR"
	and Reload the default User preferences into the context
	and Create this fiscal year
	and Create a chart of accounts from template "Minimal Account Chart" with root "Minimal Account Chart"
