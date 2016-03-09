# -*- encoding: utf-8 -*-

# These are straight cut-and-paste from Trytond doctests.
# It should be improved to be more like a Behave BDD.

@works32 @works34 @works36
Feature:    Run the Trytond scenario_account_reconciliation doctests
from trytond_account-2.8.1/tests/scenario_account_reconciliation.rst

  Scenario: Run the scenario_account_reconciliation

      Given Ensure that the "account" module is loaded
        And Set the default feature data
        And Create the Company with default COMPANY_NAME and Currency code "EUR"
        And Reload the default User preferences into the context
        And Create this fiscal year
        And Create a chart of accounts \
	    from template "Minimal Account Chart" \
	    with root "Minimal Account Chart"
        And Create a party named "Customer" \
	    with payable and receivable properties
        And T/A/SAR Create Moves for direct reconciliation
        And T/A/SAR Reconcile Lines without writeoff
        And T/A/SAR Create Moves for writeoff reconciliation
       Then T/A/SAR Reconcile Lines with writeoff



