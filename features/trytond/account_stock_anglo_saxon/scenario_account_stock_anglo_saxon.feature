# -*- encoding: utf-8 -*-

@works32
Feature: Run the Trytond scenario_account_stock_anglo_saxon doctests
    adapted from the file scenario_account_stock_anglo_saxon.rst
    in trytond_account_stock_anglo_saxon-2.8.0/tests/

    Scenario: Setup the tests of the module named "account_stock_anglo_saxon"

      Given Create database with pool.test set to True
        and Ensure that the "account_stock_anglo_saxon" module is loaded
        and Ensure that the "sale" module is loaded
        and Ensure that the "purchase" module is loaded
	and Set the default feature data
# These are in by trytond_account_stock_continental/account.xml
# which is pulled in by trytond_account_stock_anglo_saxon
	and Set the feature data with values
	     | name                                  | value                |
	     | account.template,main_cogs            | COGS                 |
	     | account.template,stock                | Stock                |
	     | account.template,stock_customer       | Stock Customer       |
	     | account.template,stock_lost_found     | Stock Lost and Found |
	     | account.template,stock_production     | Stock Production     |
	     | account.template,stock_supplier       | Stock Supplier       |
       then the "account_stock_anglo_saxon" module is in the list of loaded modules

    Scenario: Create the company to test the module named "account_stock_anglo_saxon"

      Given Create the company with default COMPANY_NAME and Currency code "EUR"
	and Reload the default User preferences into the context
	and Create this fiscal year with Invoicing
	and Create a chart of accounts from template "Minimal Account Chart" with root "Minimal Account Chart"
        and Create a saved instance of "party.party" named "Supplier"
        and Create a saved instance of "product.category" named "Category"
        and Create a party named "Customer" with an account_payable attribute


    Scenario: Buy the products from the supplier, testing the module named "account_stock_anglo_saxon"

      Given Create a user named "Accountant" with the fields
	  | name	| value		  |
	  | login	| accountant	  |
	  | password	| accountant	  |
	  | group	| Account	  |
	and Create a PaymentTerm named "Direct" with "0" days remainder
	and Create a ProductTemplate named "product" with stock accounts from features from a ProductCategory named "Category" with |name|value| fields
	  | name              | value |
	  | type	      | goods |
	  | cost_price_method | fixed |
	  | purchasable       | True  |
	  | salable 	      | True  |
	  | list_price 	      | 10    |
	  | cost_price 	      | 5     |
	  | delivery_time     | 0     |
	  | default_uom	      | Unit  |
	  | account_expense   | Main Expense |
	  | account_revenue   | Main Revenue |
	and T/ASAS/SASAS Create products of type "goods" from the ProductTemplate named "product" with fields
	  | name                | cost_price_method | description         |
	  | product_fixed	| fixed   	    | Product Fixed       |
	  | product_average	| average 	    | Product Average     |
	and Create a Purchase Order with description "12 products" from Supplier "Supplier" with fields
	  | name              | value    |
	  | invoice_method    | shipment |
	  | payment_term      | Direct 	 |
	  | purchase_date     | TODAY	 |
#?	  | currency          | EUR	 |
	and T/ASAS/SASAS Purchase products on the P. O. with description "12 products" from supplier "Supplier" with quantities
	  | description  	| quantity | unit_price |
	  | Product Fixed	| 5.0	   | 4		|
	  | Product Average	| 7.0	   | 6		|
	and T/ASAS/SASAS Quote and Confirm a P. O. with description "12 products" from supplier "Supplier"
	and T/ASAS/SASAS Receive 9 products from the P. O. with description "12 products" from supplier "Supplier" with quantities
	  | description     | quantity |
	  | Product Fixed   | 4.0      |
	  | Product Average | 5.0      |
	and T/ASAS/SASAS After receiving 9 products assert the account credits and debits
	and T/ASAS/SASAS Open a purchase invoice to pay for what we received from the P. O. with description "12 products" to supplier "Supplier" with prices
	  | description     | unit_price |
	  | Product Fixed   | 6.00     	 |
	  | Product Average | 4.00     	 |
	and T/ASAS/SASAS After paying for what we received assert the account credits and debits

    Scenario: Sell the products to the customer, testing the module named "account_stock_anglo_saxon"

      Given Create a sales order with description "Sell 5 products" to customer "Customer" with fields
	  | name              | value    |
	  | invoice_method    | shipment |
	  | payment_term      | Direct   |
	and Sell Products on the S. O. with description "Sell 5 products" to customer "Customer" with |description|quantity| fields 
	  | description     | quantity |
	  | Product Fixed   | 2.0      |
	  | Product Average | 3.0      |
	and Ship the products on the S. O. with description "Sell 5 products" to customer "Customer"
	and T/ASAS/SASAS After shipping to customer assert the account credits and debits
	and Post customer Invoice for the S. O. with description "Sell 5 products" to customer "Customer"
	and T/ASAS/SASAS After posting the invoice to customer assert the account credits and debits
	and T/ASAS/SASAS Create an invoice to supplier "Supplier" with PaymentTerm "Direct" by an accountant with quantities
	  | description     | quantity	| unit_price |
	  | Product Fixed   | 5.0      	| 4.00	     |
