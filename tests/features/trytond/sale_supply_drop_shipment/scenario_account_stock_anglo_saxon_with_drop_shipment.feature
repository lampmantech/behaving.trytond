# -*- encoding: utf-8 -*-

@works32 @works34 @broken36
Feature:    Run the Trytond scenario_account_stock_anglo_saxon doctests
    adapted from {{{trytond_account_stock_anglo_saxon-3.2.1/tests/}}}
    [[https://github.com/lampmantech/trytond_scenari/master/raw/tests/features/trytond/sale_supply_drop_shipment/scenario_account_stock_anglo_saxon_with_drop_shipment.rst|scenario_account_stock_anglo_saxon_with_drop_shipment.rst]]

    Works, but still UNFINISHED.
    
  Scenario: Setup the tests of the module named "account_stock_anglo_saxon"

      Given Create database with pool.test set to True
        And Ensure that the "account_stock_anglo_saxon" module is loaded
        And Ensure that the "sale_supply_drop_shipment" module is loaded
        And Ensure that the "sale" module is loaded
        And Ensure that the "purchase" module is loaded
        And Set the default feature data
# These are in by trytond_account_stock_continental/account.xml
# which is pulled in by trytond_account_stock_anglo_saxon
        And Set the feature data with values
            | name                                  | value                	|
            | account.template,main_cogs            | COGS                 	|
            | account.template,stock                | Stock                	|
            | account.template,stock_customer       | Stock Customer       	|
            | account.template,stock_lost_found     | Stock Lost and Found 	|
            | account.template,stock_production     | Stock Production     	|
            | account.template,stock_supplier       | Stock Supplier       	|
       Then the "account_stock_anglo_saxon" module is in the list of loaded modules

  Scenario: Create the company to test scenario_account_stock_anglo_saxon_with_drop_shipment
      Given Create parties
        And Create the company with default COMPANY_NAME and Currency code "USD"
        And Reload the default User preferences into the context
        And Create this fiscal year with Invoicing
        And Create a sale user
        And Create a purchase user
        And Create a stock user
        And Create a account user
        And Create a default Minimal Account Chart
        And Set the default credit and debit accounts on the cash Journal

  Scenario: Create the products that we will purchase
    
      Given Create a saved instance of "product.category" named "Category"
        And Create a ProductTemplate named "Product Template" with stock accounts from features from a ProductCategory named "Category" with |name|value| fields
            | name              | value 	|
            | type	      | goods 	|
            | cost_price_method | fixed 	|
            | purchasable       | True  	|
            | salable 	      | True  	|
            | list_price 	      | 10    	|
            | cost_price 	      | 5     	|
            | delivery_time     | 0     	|
            | default_uom	      | Unit  	|
            | account_expense   | Main Expense 	|
            | account_revenue   | Main Revenue 	|
            | account_cogs      | COGS 	|
            | stock_journal     | STO   	|
            | supply_on_sale    | True 	|
        And Create a product with description "T/ASASDS Product Description" from template "Product Template"   
#        and Create a ProductSupplier with description "T/ASASDS Product Description" from a ProductTemplate named "Product Template" with supplier named "Supplier" with |name|value| fields
#	  | name              | value   	|
#	  | drop_shipment     | True    	|
#          | delivery_time     | 0       	|
        And Create a PaymentTerm named "Direct" with "0" days remainder
	
  Scenario: Unfinished - the rest still needs breaking out

      Given T/ASASDS Account Stock Anglo-Saxon with Drop Shipment Scenario
 
