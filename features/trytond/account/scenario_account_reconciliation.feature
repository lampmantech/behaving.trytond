# -*- encoding: utf-8 -*-

# These are straight cut-and-paste from Trytond doctests.
# It should be improved to be more like a Behave BDD.

Feature: Run the Trytond scenario_account_reconciliation doctests
from trytond_account-2.8.1/tests/scenario_account_reconciliation.rst
Updated for 3.0 and 3.2.

   Scenario: Run the scenario_account_reconciliation

      Given Create database
        and Ensure that the "account" module is loaded
	and the "account" module is in the list of loaded modules
	and Set the default feature data
	and Create the Company with default COMPANY_NAME and Currency code "EUR"
	and Reload the default User preferences into the context
	and Create this fiscal year
	and Create a chart of accounts from template "Minimal Account Chart" with root "Minimal Account Chart"
        and Create a party named "Customer" with an account_payable attribute
       	and T/A/SAR Create Moves for direct reconciliation
       	and T/A/SAR Reconcile Lines without writeoff
       	and T/A/SAR Create Moves for writeoff reconciliation
       Then T/A/SAR Reconcile Lines with writeoff



