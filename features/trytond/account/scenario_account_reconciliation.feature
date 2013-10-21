# -*- encoding: utf-8 -*-

# These are straight cut-and-paste from Trytond doctests.
# It should be improved to be more like a Behave BDD.

Feature: Run the Trytond scenario_account_reconciliation doctests
from trytond_account-2.8.1/tests/scenario_account_reconciliation.rst

   Scenario: Run the scenario_account_reconciliation

      Given Create database
        and we ensure that the "account" module is loaded
	and the "account" module is in the list of loaded modules
	and Create company
	and Reload the context
	and Create this fiscal year
	and Create a chart of accounts from the MINIMAL_ACCOUNT_PARENT
        and Create a party named "Customer" with an account_payable attribute
       	and Create Moves for direct reconciliation
       	and Reconcile Lines without writeoff
       	and Create Moves for writeoff reconciliation
       	and Reconcile Lines with writeoff
       Then there are some instances of "party.party"

      

