# -*- encoding: utf-8 -*-

@works32
Feature:    Run the Trytond scenario_invoice_supplier doctests
    adapted from the file scenario_invoice_supplier.rst
    in trytond_account_invoice-3.0.0/tests/

  Scenario: Setup the tests of the module named "account_invoice"

      Given Create database with pool.test set to True
        And Ensure that the "account_invoice" module is loaded
        And Set the default feature data
       Then the "account_invoice" module is in the list of loaded modules

      Given Create the company with default COMPANY_NAME and Currency code "USD"
        And Reload the default User preferences into the context
        And Create this fiscal year with Invoicing
        And Create a chart of accounts \
	    from template "Minimal Account Chart" \
	    with root "Minimal Account Chart"
        And Create a saved instance of "party.party" named "Supplier"
        And Create a PaymentTerm named "Term" with "0" days remainder
        And Create a tax named "10% Sales Tax" with fields
            | name                  | value            	|
            | description           | 10% Sales Tax    	|
            | type 	            | percentage       	|
            | rate 	            | .10	       	|
            | invoice_base_code     | invoice base     	|
            | invoice_tax_code      | invoice tax      	|
            | credit_note_base_code | credit note base 	|
            | credit_note_tax_code  | credit note tax  	|
        And Create a ProductTemplate named "Service Product" \
	    with supplier_tax named "10% Sales Tax" with |name|value| fields
            | name              | value        	|
            | type	      | service      	|
            | list_price 	      | 40           	|
            | cost_price 	      | 20           	|
            | default_uom	      | Unit         	|
            | account_expense   | Main Expense 	|
            | account_revenue   | Main Revenue 	|
            | cost_price_method | fixed        	|
        And Create a product with description "Services Bought" \
	    from template "Service Product"
        And Create an Invoice on date "TODAY" \
	    with description "Buy the Services Bought" \
        And a PaymentTerm named "Term" to supplier "Supplier" with \
	    following |description|quantity|unit_price|account|currency| fields
# Note that this uses the heading description rather than name
            | description       | quantity | unit_price | account      | currency 	|
            | Services Bought   | 5	   | 	        |              |          	|
            | Test     	        | 1	   | 10.00      | Main Expense |          	|
       Then TS/AIS Post the invoice with description "Buy the Services Bought" and assert the taxes named "10% Sales Tax" are right
        And TS/AIS Create a credit note for the invoice \
	    with description "Buy the Services Bought" and assert the amounts
