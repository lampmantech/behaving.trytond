# -*- encoding: utf-8 -*-

@works36
Feature:    Run the Trytond scenario_account_statement doctests

  Account Statement Scenario
  from trytond_account_statement-3.6.0/tests/scenario_account_statement.rst
  Works, but still not broken up yet.

  Scenario: Setup the tests of the module named "account_invoice"

      Given Create database with pool.test set to True
        And Ensure that the "account_invoice" module is loaded
        And Set the default feature data
       Then the "account_statement" module is in the list of loaded modules

      Given Create the company with default COMPANY_NAME and Currency code "USD"
        And Reload the default User preferences into the context
        And Create this fiscal year with Invoicing
        And Create a chart of accounts \
	    from template "Minimal Account Chart" \
	    with root "Minimal Account Chart"
        And Create a saved instance of "party.party" named "Supplier"
        And Create a saved instance of "party.party" named "Customer"
        And Create a PaymentTerm named "Term" with "0" days remainder

      Given T/SASt Scenario Account Statement
#        And T/SASt Testing balance validation
#        And T/SASt Testing amount validation
#        And T/SASt Test number of lines validation
