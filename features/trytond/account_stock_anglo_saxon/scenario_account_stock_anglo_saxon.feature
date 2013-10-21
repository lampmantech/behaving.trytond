# -*- encoding: utf-8 -*-

# These are straight cut-and-paste from Trytond doctests.
# It should be improved to be more like a Behave BDD.

Feature: Run the Trytond scenario_account_stock_anglo_saxon doctests

   @wip
   Scenario: Run the trytond_account_stock_anglo_saxon-2.8.0/tests/scenario_account_stock_anglo_saxon.rst

      Given Create database with pool.test set to True
#        and Install the test module named "account_stock_anglo_saxon"
        and we ensure that the "account_stock_anglo_saxon" module is loaded
        and we ensure that the "sale" module is loaded
        and we ensure that the "purchase" module is loaded
	and the "account_stock_anglo_saxon" module is in the list of loaded modules
	and Create company
	and Reload the context
	and Create an accountant user
	and Create fiscal year with Invoicing
	and Create a chart of accounts from the MINIMAL_ACCOUNT_PARENT
        and Create a party named "Customer" with an account_payable attribute
        and Create a saved instance of "party.party" named "Supplier" 
	and Create a ProductCategory named "Category"
	and Create a ProductTemplate named "product"
	and Create a product
	and Create a Direct payment term
	and Purchase 12 products
	and Receive 9 products

