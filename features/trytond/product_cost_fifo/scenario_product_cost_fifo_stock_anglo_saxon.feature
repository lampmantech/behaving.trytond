# -*- encoding: utf-8 -*-

# These are straight cut-and-paste from Trytond doctests.
# It should be improved to be more like a Behave BDD.

Feature: Run the Trytond scenario_account_stock_anglo_saxon doctests
    adapted from the file scenario_account_stock_anglo_saxon.rst
    in trytond_account_stock_anglo_saxon-2.8.0/tests/ but with the
    "product_cost_fifo" module loaded and see what happens!

    @wip
    Scenario: Run the tests of the module named "product_cost_fifo"

      Given Create database with pool.test set to True
        and we ensure that the "account_stock_anglo_saxon" module is loaded
        and we ensure that the "product_cost_fifo" module is loaded
        and we ensure that the "sale" module is loaded
        and we ensure that the "purchase" module is loaded
	and the "account_stock_anglo_saxon" module is in the list of loaded modules
	and Create company
	and Reload the context
	and Create an accountant user
	and Create this fiscal year with Invoicing
	and Create a chart of accounts from the MINIMAL_ACCOUNT_PARENT
        and Create a party named "Customer" with an account_payable attribute
        and Create a saved instance of "party.party" named "Supplier" 
	and Create a ProductCategory named "Category"
	and Create a ProductTemplate named "product" with a cost_price_method of "fifo"
	and Create a product with a cost_price_method of "fifo"
	and Create a payment term named "Direct" with "0" days remainder
	and Purchase 12 products
	and Receive 9 products
	and Open supplier invoice
	and Sale 5 products
	and Send 5 products
	and Open customer invoice
	and Now create a supplier invoice with an accountant
