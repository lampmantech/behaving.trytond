# -*- encoding: utf-8 -*-

# These are straight cut-and-paste from Trytond doctests.
# It should be improved to be more like a Behave BDD.


Feature: Run the Trytond scenario_account_stock_anglo_saxon doctests with the
    "product_cost_fifo" module loaded and with a cost_price_method of "fifo.
    This FAILS on the asserts as it should for now because it is a copy
    changed to use FIFO, but the accounting results have not yet been updated.

    @wip
    Scenario: Run the tests of the module named "product_cost_fifo"

      Given Create database with pool.test set to True
        and Ensure that the "account_stock_anglo_saxon" module is loaded
        and Ensure that the "product_cost_fifo" module is loaded
        and Ensure that the "sale" module is loaded
        and Ensure that the "purchase" module is loaded
	and Set the default feature data
# These are in by trytond_account_stock_continental/account.xml
# which is pulled in by trytond_account_stock_anglo_saxon
	and Set the feature data with values
	     | name                                  | value                |
	     | account.template,COGS                 | COGS                 |
	     | account.template,stock                | Stock                |
	     | account.template,stock_customer       | Stock Customer       |
	     | account.template,stock_lost_found     | Stock Lost and Found |
	     | account.template,stock_production     | Stock Production     |
	     | account.template,stock_supplier       | Stock Supplier       |
       then the "account_stock_anglo_saxon" module is in the list of loaded modules

    Scenario: Create the company to test the module named "product_cost_fifo"

      Given Create the company with default COMPANY_NAME and Currency code "EUR"
	and Reload the default User preferences into the context
	and Create this fiscal year with Invoicing
	and Create a chart of accounts from template "Minimal Account Chart" with root "Minimal Account Chart"
        and Create a saved instance of "party.party" named "Supplier"
        and Create a saved instance of "product.category" named "Category"
        and Create a party named "Customer" with an account_payable attribute


    Scenario: Buy the products from the supplier, testing the module named "product_cost_fifo"
      Given Create a user named "Accountant" with the fields
	  | name	| value		  |
	  | login	| accountant	  |
	  | password	| accountant	  |
	  | group	| Account	  |
	and Create a PaymentTerm named "Direct" with "0" days remainder
	and T/ASAS/SASAS Create a ProductTemplate named "product" with fields
	  | name              | value |
	  | type	      | goods |
	  | cost_price_method | fifo  |
	  | purchasable       | True  |
	  | salable 	      | True  |
	  | list_price 	      | 10    |
	  | cost_price 	      | 5     |
	  | delivery_time     | 0     |
	and T/ASAS/SASAS Create two products of type "goods" from the ProductTemplate named "product" with fields
	  | name                | cost_price_method |
	  | product_fixed	| fifo   	    |
	  | product_average	| fifo		    |
	and Create a Purchase Order with description "12 products" from Supplier "Supplier" with fields
	  | name              | value    |
	  | invoice_method    | shipment |
	  | payment_term      | Direct 	 |
	  | purchase_date     | TODAY	 |
	and T/ASAS/SASAS Purchase products on the P. O. with description "12 products" from supplier "Supplier" with quantities
	  | description  	| quantity | unit_price |
	  | product_fixed	| 5.0	   | 4		|
	  | product_average	| 7.0	   | 6		|
	and T/ASAS/SASAS Quote and Confirm a P. O. with description "12 products" from supplier "Supplier"
	and T/ASAS/SASAS Receive 9 products from the P. O. with description "12 products" from supplier "Supplier" with quantities
	  | description     | quantity |
	  | product_fixed   | 4.0      |
	  | product_average | 5.0      |
	and T/ASAS/SASAS After receiving 9 products assert the account credits and debits
	and T/ASAS/SASAS Open a purchase invoice to pay for what we received from the P. O. with description "12 products" to supplier "Supplier"
	and T/ASAS/SASAS After paying for what we received assert the account credits and debits

    Scenario: Sell the products to the customer, testing the module named "product_cost_fifo"
       Given T/ASAS/SASAS Create a sales order with description "Sell 5 products" to customer "Customer" with fields
	  | name              | value    |
	  | invoice_method    | shipment |
	  | payment_term      | Direct   |
	and T/ASAS/SASAS Sell products on the S. O. with description "Sell 5 products" to customer "Customer" with quantities
	  | description     | quantity |
	  | product_fixed   | 2.0      |
	  | product_average | 3.0      |
	and T/ASAS/SASAS Send 5 products on the S. O. with description "Sell 5 products" to customer "Customer"
	and T/ASAS/SASAS After shipping to customer assert the account credits and debits
	and T/ASAS/SASAS Open customer invoice for the S. O. with description "Sell 5 products" to customer "Customer"
	and T/ASAS/SASAS After posting the invoice to customer assert the account credits and debits
	and T/ASAS/SASAS Now create a supplier invoice with an accountant
