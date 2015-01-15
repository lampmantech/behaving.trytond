# -*- encoding: utf-8 -*-

@works32
Feature: Run the Trytond scenario_invoice_supplier doctests
    adapted from the file scenario_invoice_supplier.rst
    in trytond_account_invoice-3.0.0/tests/

    Scenario: Setup the tests of the module named "account_invoice"

      Given Create database with pool.test set to True
        and Ensure that the "account_invoice" module is loaded
	and Set the default feature data
       then the "account_invoice" module is in the list of loaded modules

      Given Create the company with default COMPANY_NAME and Currency code "USD"
	and Reload the default User preferences into the context
	and Create this fiscal year with Invoicing
	and Create a chart of accounts from template "Minimal Account Chart" with root "Minimal Account Chart"
	and Create a saved instance of "party.party" named "Supplier"
	and Create a PaymentTerm named "Term" with "0" days remainder
	and Create a tax named "10% Sales Tax" with fields
	    | name                  | value            |
	    | description           | 10% Sales Tax    |
	    | type 	            | percentage       |
	    | rate 	            | .10	       |
	    | invoice_base_code     | invoice base     |
	    | invoice_tax_code      | invoice tax      |
	    | credit_note_base_code | credit note base |
	    | credit_note_tax_code  | credit note tax  |
# FixMe: need to handle supplier_tax named "10% Sales Tax" in string_to_python
	and TS/AIS Create a ProductTemplate named "Service Product" with supplier_tax named "10% Sales Tax" with fields
	  | name              | value   |
	  | type	      | service |
	  | list_price 	      | 40      |
	  | cost_price 	      | 20      |
	  | default_uom	      | Unit    |
#	  | cost_price_method | fixed   |
	and TS/AIS Create a product with description "Services Bought" from template "Service Product"
	and TS/AIS Create an invoice with description "Buy the Services Bought" to supplier "Supplier" with fields
# Note that this uses the heading description rather than name
	  | description       | quantity   | unit_price |
	  | Services Bought   | 5	   | 		|
	  | Test     	      | 1	   | 10.00	|
       Then TS/AIS Post the invoice with description "Buy the Services Bought" and assert the taxes named "10% Sales Tax" are right
        and TS/AIS Create a credit note for the invoice with description "Buy the Services Bought" and assert the amounts