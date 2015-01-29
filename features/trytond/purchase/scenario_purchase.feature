# -*- encoding: utf-8 -*-

@works32
Feature: Run the Trytond scenario_purchase doctests
    adapted from 
    in 
    Works, but still UNFINISHED.
    
    Scenario: Setup the tests of the purchase module

      Given Create database with pool.test set to True
        and Ensure that the "account_invoice_stock" module is loaded
        and Ensure that the "sale" module is loaded
        and Ensure that the "purchase" module is loaded
	and Create parties
	and Set the default feature data
	and Set the feature data with values
	     | name                                  | value                |
	     | account.template,main_cogs            | COGS                 |
	     | account.template,stock                | Stock                |
	     | account.template,stock_customer       | Stock Customer       |
	     | account.template,stock_lost_found     | Stock Lost and Found |
	     | account.template,stock_production     | Stock Production     |
	     | account.template,stock_supplier       | Stock Supplier       |

    Scenario: Create the company to test the module

      Given Create the company with default COMPANY_NAME and Currency code "USD"
	and Reload the default User preferences into the context
	and Create this fiscal year with Invoicing
        and Create a sale user
	and Create a purchase user
	and Create a stock user
	and Create a account user
	and Create a default Minimal Account Chart
	and Set the default credit and debit accounts on the cash Journal

    Scenario: Create the products that we will purchase
    """
    We'll put a hack to work on systems without a CoTs:
    just call the tax "NO Sales Tax".
    """
    
      Given Create a saved instance of "product.category" named "Category"
#	and T/PUR Create ProductTemplate
        and Create a ProductTemplate named "product" with supplier_tax named "NO Sales Tax" with |name|value| fields
	  | name              | value |
	  | type	      | goods |
	  | cost_price_method | fixed |
          | default_uom       | Unit  |
	  | purchasable       | True  |
	  | salable 	      | True  |
	  | list_price 	      | 10    |
	  | cost_price 	      | 5     |
	  | delivery_time     | 0     |
	  | account_expense   | Main Expense |
	  | account_revenue   | Main Revenue |
        and Create a ProductTemplate named "service" with supplier_tax named "NO Sales Tax" with |name|value| fields
	  | name              | value |
	  | type	      | service |
	  | cost_price_method | fixed |
          | default_uom       | Unit  |
	  | purchasable       | True  |
	  | list_price 	      | 10    |
	  | cost_price 	      | 10    |
	  | delivery_time     | 0     |
	  | account_expense   | Main Expense |
	  | account_revenue   | Main Revenue |
	and Create a PaymentTerm named "Direct" with "0" days remainder
    
    Scenario: Unfinished - the rest still needs breaking out

      Given T/PUR Purchase Scenario
      