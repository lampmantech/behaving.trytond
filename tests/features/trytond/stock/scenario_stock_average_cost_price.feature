# -*- encoding: utf-8 -*-

@works32 @works34 @works36
Feature:    Stock Average Cost Price Scenario

  These are straight cut-and-paste from Trytond doctests from
  {{{trytond_stock-3.2.3/tests/}}}
  [[https://github.com/lampmantech/trytond_scenari/master/raw/tests/features/trytond/stock/scenario_stock_average_cost_price.rst|scenario_stock_average_cost_price.rst]]


  Scenario: test stock
    
      Given Create database with pool.test set to True
        And Ensure that the "account" module is loaded
        And Ensure that the "stock" module is loaded
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
    	      We have no chart of accounts.
	      
      Given Create the company with default COMPANY_NAME and Currency code "USD"
        And Reload the default User preferences into the context
	
  Scenario: Create the ProductTemplate for the products that we will stock
    	      We have no chart of accounts.
	      
      Given Create an instance of "product.template" \
      	    named "T/SACP Product Template" with |name|value| fields
            | name              | value   	|
            | type	      | goods   	|
            | list_price 	      | 300     	|
            | cost_price 	      | 80      	|
            | default_uom	      | Unit    	|
            | cost_price_method | average 	|
        And Stock Move of product of ProductTemplate named "T/SACP Product Template"\
	    between locations with |name|value| fields
            | name                | value 	|
            | uom 	        | Unit  	|
            | quantity 	        | 1     	|
            | from_location 	| SUP 		|
            | to_location 	| STO 		|
            | planned_date 	| TODAY 	|
            | effective_date 	| TODAY 	|
            | unit_price 		| 100 		|
            | currency 		| USD 		|
        And T/SACP Check Cost Price is 100
        And Stock Move of product of ProductTemplate named "T/SACP Product Template"\
	    between locations with |name|value| fields
            | name                | value 	|
            | uom 	        | Unit  	|
            | quantity 	        | 1     	|
            | from_location 	| SUP 		|
            | to_location 	| STO 		|
            | planned_date 	| TODAY 	|
            | effective_date 	| TODAY 	|
            | unit_price 		| 200 		|
            | currency 		| USD 		|
        And T/SACP Check Cost Price is 150
