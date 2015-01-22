# -*- encoding: utf-8 -*-

# These are straight cut-and-paste from Trytond tests.

Feature: Run the Trytond scenario_bank tests
trytond_bank-3.2.0/tests/test_bank.py

   Scenario: Create a bank

      Given Ensure that the "bank" module is loaded
	and the "bank" module is in the list of loaded modules
	and Create a party named "HSBCLondon"
# Create a bank named "HSBCBank" associated to a party "HSBCBanker" with optional BIC "{uBic}"
