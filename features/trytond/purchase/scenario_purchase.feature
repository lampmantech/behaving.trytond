# -*- encoding: utf-8 -*-

@works32
Feature:    Run the Trytond scenario_purchase doctests
    adapted from 
    in 
    Works, but still UNFINISHED.
    
  Scenario: Setup the tests of the purchase module

      Given Create database with pool.test set to True
        And Ensure that the "account_invoice_stock" module is loaded
        And Ensure that the "sale" module is loaded
        And Ensure that the "purchase" module is loaded
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
        And Create this fiscal year with Invoicing
        And Create a sale user
        And Create a purchase user
        And Create a stock user
        And Create a account user
        And Create a default Minimal Account Chart
        And Set the default credit and debit accounts on the cash Journal

  Scenario: Create the products that we will purchase
    """
    We'll put a hack to work on systems without a CoTs:
    just call the tax "NO Sales Tax".
    """
    
      Given Create a saved instance of "product.category" named "Category"
# see also: and Create a ProductTemplate named "product" with stock accounts from features from a ProductCategory named "Category" with |name|value| fields
        And Create a ProductTemplate named "product" \
	    with supplier_tax named "NO Sales Tax" with |name|value| fields
            | name              | value 	|
            | type	      | goods 	|
            | cost_price_method | fixed 	|
            | default_uom       | Unit  	|
            | purchasable       | True  	|
            | salable 	      | True  	|
            | list_price 	      | 10    	|
            | cost_price 	      | 5     	|
            | delivery_time     | 0     	|
            | account_expense   | Main Expense 	|
            | account_revenue   | Main Revenue 	|
        And Create a ProductTemplate named "service" \
	    with supplier_tax named "NO Sales Tax" with |name|value| fields
            | name              | value 	|
            | type	      | service 	|
            | cost_price_method | fixed 	|
            | default_uom       | Unit  	|
            | purchasable       | True  	|
            | list_price 	      | 10    	|
            | cost_price 	      | 10    	|
            | delivery_time     | 0     	|
            | account_expense   | Main Expense 	|
            | account_revenue   | Main Revenue 	|
        And Create a PaymentTerm named "Direct" with "0" days remainder
    
  Scenario: Create the stock and inventory

      Given Create an Inventory as user named "Stock" \
      	    with storage at the location coded "STO"
       Then Add to inventory as user named "Stock" \
       	    with storage at the location coded "STO" \
	    ProductTemplates with |product|quantity|expected_quantity| fields
            | name | quantity | expected_quantity 	|
            | product | 100.0    | 0.0               	|

  Scenario: Create the first purchase order

      Given Purchase on date "TODAY" with description "P. O. #1" \
      	    with their reference "Ref1" as user named "Purchase" \
	    in Currency coded "USD" ProductTemplates from supplier "Supplier" \
	    with PaymentTerm "Direct" and InvoiceMethod "order" \
	    with |name|quantity|description| fields
            | name    | quantity | line_description 	|
            | product | 2.0      |             	|
            | product | comment  | Comment     	|
            | product | 3.0      |             	|
        And Purchase "quote" on date "TODAY" the P. O. \
	    with description "P. O. #1" as user named "Purchase" \
	    products from supplier "Supplier"
        And Purchase "confirm" on date "TODAY" the P. O. \
	    with description "P. O. #1" as user named "Purchase" \
	    products from supplier "Supplier"
        And T/PUR Assert the Purchase lines in the P. O. \
	    with description "P. O. #1" for products from supplier "Supplier"
        And T/PUR Assert the Invoice lines are linked to stock move in the \
	    P. O. with description "P. O. #1" for products from supplier "Supplier"
        And Action "post" on date "TODAY" the Invoice \
	    with description "P. O. #1" as user named "Account" \
	    products from party "Supplier"
        And T/PUR Check no new invoices in the P. O. \
	    with description "P. O. #1" for products from supplier "Supplier"
    
  Scenario: Create the second purchase order

      Given Purchase on date "TODAY" with description "P. O. #2" \
      	    with their reference "Ref2" as user named "Purchase" \
	    in Currency coded "USD" ProductTemplates from supplier "Supplier" \
	    with PaymentTerm "Direct" and InvoiceMethod "shipment" \
	    with |name|quantity|description| fields
            | name | quantity | line_description 	|
            | product | 2.0      |             	|
            | product | comment  | Comment     	|
            | product | 3.0      |             	|
        And Purchase "quote" on date "TODAY" \
	    the P. O. with description "P. O. #2" as user named "Purchase" \
	    products from supplier "Supplier"
        And Purchase "confirm" on date "TODAY" \
	    the P. O. with description "P. O. #2" as user named "Purchase" \
	    products from supplier "Supplier"
        And T/PUR Assert not yet linked to invoice lines P. O. \
	    with description "P. O. #2" for products from supplier "Supplier"
        And Validate shipments on "TODAY" for P. O. with description "P. O. #2" \
	    as user named "Stock" for products from supplier "Supplier"
	
  Scenario: Unfinished - the rest still needs breaking out

      Given T/PUR Purchase Scenario
