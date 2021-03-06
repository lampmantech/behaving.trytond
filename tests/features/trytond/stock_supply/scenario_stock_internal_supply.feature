# -*- encoding: utf-8 -*-

# These are straight cut-and-paste from Trytond doctests from
# trytond_stock_supply-3.2.2/tests/scenario_stock_internal_supply.rst


@wip
Feature:    Stock Shipment Out Scenario

  Scenario: test stock_supply
    
      Given Create database with pool.test set to True
        And Ensure that the "account" module is loaded
        And Ensure that the "stock_supply" module is loaded
        And Create parties
        And Set the default feature data
        And Set the feature data with values
            | name                                  | value                	|
            | account.template,main_cogs            | COGS                 	|
            | account.template,stock                | Stock                	|
            | account.template,stock_customer       | Stock Customer       	|
            | account.template,stock_lost_found     | Stock Lost and Found 	|
            | account.template,stock_production     | Stock Production     	|
            | account.template,stock_supplier       | Stock Supplier       	|

  Scenario: Create the company to test the module

      Given Create the company with default COMPANY_NAME and Currency code "USD"
        And Reload the default User preferences into the context
        And Create a purchase user
        And Create a stock user
        And Create a stock_admin user
        And Create a product user
      Given Create an instance of "product.template" \
      	    named "T/SSIS Product Template" with |name|value| fields
            | name              | value   	|
            | type	      | goods   	|
            | list_price 	      | 20      	|
            | cost_price 	      | 8       	|
            | default_uom	      | Unit    	|
            | cost_price_method | average        	|
        And Create a product with description "Product Description" \
	    from template "T/SSIS Product Template"
      
  Scenario: Unfinished
    
      Given T/SSOS Stock Shipment Out Scenario
