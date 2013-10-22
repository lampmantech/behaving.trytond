# -*- encoding: utf-8 -*-

# These are straight cut-and-paste from Trytond doctests.
# It should be improved to be more like a Behave BDD.

Feature: Run the Trytond scenario_account_stock_anglo_saxon doctests
    adapted from the file scenario_account_stock_anglo_saxon.rst
    in trytond_account_stock_anglo_saxon-2.8.0/tests/

    Scenario: Run the tests of the module named "account_stock_anglo_saxon"

      Given Create database with pool.test set to True
        and Ensure that the "account_stock_anglo_saxon" module is loaded
        and Ensure that the "sale" module is loaded
        and Ensure that the "purchase" module is loaded
	and the "account_stock_anglo_saxon" module is in the list of loaded modules
	and Create the company with default COMPANY_NAME and Currency code "EUR"
	and Reload the default User preferences into the context
	and Create an accountant user
	and Create this fiscal year with Invoicing
	and Create a chart of accounts from the MINIMAL_ACCOUNT_PARENT
        and Create a party named "Customer" with an account_payable attribute
        and Create a saved instance of "party.party" named "Supplier" 
        and Create a saved instance of "product.category" named "Category" 
#	and Create a ProductCategory named "Category"
	and Create a ProductTemplate named "product" having:
	  | name              | value |
	  | type	      | goods |
	  | cost_price_method | fixed |
	  | purchasable       | True  |
	  | salable 	      | True  |
	  | list_price 	      | 10    |
	  | cost_price 	      | 5     |
	  | delivery_time     | 0     |

	and Create a product with a cost_price_method of "average"
	and Create a PaymentTerm named "Direct" with "0" days remainder
	and Purchase 12 products from supplier "Supplier"
	and Receive 9 products from supplier "Supplier"
	and Open purchase invoice to supplier "Supplier"
	and Sell 5 products to customer "Customer"
	and Send 5 products to customer "Customer"
	and Open customer invoice
	and Now create a supplier invoice with an accountant
