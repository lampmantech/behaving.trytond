# -*- encoding: utf-8 -*-

@works32 @works34 @works36
Feature:    Run the Trytond scenario_payment doctests
    adapted from the file in {{{trytond_account_payment-3.2.1/tests/}}}
    [[https://github.com/lampmantech/trytond_scenari/master/raw/tests/features/trytond/account_payment/scenario_account_payment.rst|scenario_account_payment.rst]]


  Scenario: Setup the tests of the module named "account_payment"

      Given Create database with pool.test set to True
        And Ensure that the "account_payment" module is loaded
        And Set the default feature data
       Then the "account_payment" module is in the list of loaded modules

      Given Create the company with default COMPANY_NAME and Currency code "USD"
        And Reload the default User preferences into the context
        And Create this fiscal year without Invoicing
        And Create a chart of accounts \
	    from template "Minimal Account Chart" \
	    with root "Minimal Account Chart"
        And Create a saved instance of "party.party" named "Supplier"
	And T/AP Create a PaymentJournal named "Manual" of type "manual"


  Scenario: Unfinished

      Given T/AP Unfinished
      
