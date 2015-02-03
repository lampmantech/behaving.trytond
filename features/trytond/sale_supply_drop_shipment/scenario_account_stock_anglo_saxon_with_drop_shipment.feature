# -*- encoding: utf-8 -*-

@works32
Feature: Run the Trytond scenario_account_stock_anglo_saxon doctests
    adapted from scenario_account_stock_anglo_saxon_with_drop_shipment.rst
    in trytond_account_stock_anglo_saxon-3.2.1/tests/
    Works, but still UNFINISHED.
    
    Scenario: Setup the tests of the module named "account_stock_anglo_saxon"

      Given Create database with pool.test set to True
        and Ensure that the "account_stock_anglo_saxon" module is loaded
        and Ensure that the "sale_supply_drop_shipment" module is loaded
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

    Scenario: Create the company to test scenario_account_stock_anglo_saxon_with_drop_shipment
      Given Create parties
	and Create the company with default COMPANY_NAME and Currency code "USD"
	and Reload the default User preferences into the context
	and Create this fiscal year with Invoicing
        and Create a sale user
	and Create a purchase user
	and Create a stock user
	and Create a account user
	and Create a default Minimal Account Chart
	and Set the default credit and debit accounts on the cash Journal

    Scenario: Create the products that we will purchase
    
      Given Create a saved instance of "product.category" named "Category"
        and Create a ProductTemplate named "Product Template" with stock accounts from features from a ProductCategory named "Category" with |name|value| fields
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
	  | account_cogs      | COGS |
          | stock_journal     | STO   |
          | supply_on_sale    | True |
	and Create a product with description "T/ASASDS Product Description" from template "Product Template"   
#        and Create a ProductSupplier with description "T/ASASDS Product Description" from a ProductTemplate named "Product Template" with supplier named "Supplier" with |name|value| fields
#	  | name              | value   |
#	  | drop_shipment     | True    |
#          | delivery_time     | 0       |
	and Create a PaymentTerm named "Direct" with "0" days remainder
	
    Scenario: Unfinished - the rest still needs breaking out

      Given T/ASASDS Account Stock Anglo-Saxon with Drop Shipment Scenario
 