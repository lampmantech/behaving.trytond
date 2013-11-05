# -*- encoding: utf-8 -*-
"""

=========================
Invoice Supplier Scenario
=========================

This is a straight cut-and-paste from
trytond_account_invoice-3.0.0/tests/scenario_invoice_supplier.rst

It should be improved to be more like a Behave BDD.
"""

from behave import *

import time
import datetime
from dateutil.relativedelta import relativedelta
from decimal import Decimal
from operator import attrgetter
from proteus import config, Model, Wizard

from .support.fields import string_to_python, sGetFeatureData, vSetFeatureData
from .support import modules
from .support import tools

# Warning - these are hardwired from the Tryton code
from .trytond_constants import *

today = datetime.date.today()

# 10% Sales Tax
@step('TS/AIS Create a tax named "{uTaxName}" with fields')
def step_impl(context, uTaxName):

    Party = Model.get('party.party')
    sCompanyName = sGetFeatureData(context, 'party,company_name')
    party, = Party.find([('name', '=', sCompanyName)])
    Company = Model.get('company.company')
    company, = Company.find([('party.id', '=', party.id)])

    Account = Model.get('account.account')
    account_tax, = Account.find([
        ('kind', '=', 'other'),
        ('name', '=', sGetFeatureData(context, 'account.template,main_tax')),
        ('company', '=', company.id),
        ])

    Tax = Model.get('account.tax')
    if not Tax.find([('name', '=', uTaxName)]):
        
        TaxCode = Model.get('account.tax.code')
        
        tax = Tax()
        tax.name = uTaxName
        tax.invoice_account = account_tax
        tax.credit_note_account = account_tax
        for row in context.table:
            if row['name'] == 'invoice_base_code' or \
                   row['name'] == 'invoice_tax_code' or \
                   row['name'] == 'credit_note_base_code' or \
                   row['name'] == 'credit_note_tax_code':
                # create these if they dont exist
                l = TaxCode.find([('name', '=', row['value'])])
                if l:
                    tax_code = l[0]
                else:
                    tax_code = TaxCode(name=row['value'])
                    tax_code.save()
                setattr(tax, row['name'], tax_code)
            else:
                setattr(tax, row['name'],
                    string_to_python(row['name'], row['value'], Tax))

        tax.save()

# Service Product
@step('TS/AIS Create a ProductTemplate named "{uTemplateName}" with supplier_tax named "{uTaxName}" with fields')
def step_impl(context, uTemplateName, uTaxName):


    ProductTemplate = Model.get('product.template')

    Party = Model.get('party.party')
    sCompanyName = sGetFeatureData(context, 'party,company_name')
    party, = Party.find([('name', '=', sCompanyName)])
    Company = Model.get('company.company')
    company, = Company.find([('party.id', '=', party.id)])

    if not ProductTemplate.find([('name', '=', uTemplateName)]):
        template = ProductTemplate()
        template.name = uTemplateName
        # type, cost_price_method, default_uom, list_price, cost_price
        for row in context.table:
            setattr(template, row['name'],
                    string_to_python(row['name'], row['value'], ProductTemplate))
        Account = Model.get('account.account')
        expense, = Account.find([
            ('kind', '=', 'expense'),
            ('name', '=', sGetFeatureData(context, 'account.template,main_expense')),
            ('company', '=', company.id),
            ])
        revenue, = Account.find([
            ('kind', '=', 'revenue'),
            ('name', '=', sGetFeatureData(context, 'account.template,main_revenue')),
            ('company', '=', company.id),
            ])
        
        template.account_expense = expense
        template.account_revenue = revenue
        
        Tax = Model.get('account.tax')
        # FixMe: need to handle supplier_tax as an append in string_to_python
        tax, = Tax.find([('name', '=', uTaxName)])
        template.supplier_taxes.append(tax)
        
        template.save()

# Services Bought, Service Product
@step('TS/AIS Create a product with description "{uDescription}" from template "{uTemplateName}"')
def step_impl(context, uDescription, uTemplateName):

    ProductTemplate = Model.get('product.template')
    template, = ProductTemplate.find([('name', '=', uTemplateName)])
    
    Product = Model.get('product.product')
    if not Product.find([('description', '=', uDescription)]):
        product = Product()
        product.template = template
        product.description = uDescription
        product.save()


# Buy the Services Bought, Supplier
@step('TS/AIS Create an invoice with description "{uDescription}" to supplier "{uSupplier}" with fields')
def step_impl(context, uDescription, uSupplier):
    current_config = context.oProteusConfig

    Party = Model.get('party.party')
    sCompanyName = sGetFeatureData(context, 'party,company_name')
    party, = Party.find([('name', '=', sCompanyName)])
    Company = Model.get('company.company')
    company, = Company.find([('party.id', '=', party.id)])

    Invoice = Model.get('account.invoice')
    if not Invoice.find(['description', '=', uDescription]):
        invoice = Invoice()
        invoice.type = 'in_invoice'
        invoice.invoice_date = today
        invoice.accounting_date = invoice.invoice_date
        invoice.description = uDescription
        
        PaymentTerm = Model.get('account.invoice.payment_term')
        payment_term, = PaymentTerm.find([('name', '=', 'Term')])
        party, = Party.find([('name', '=', uSupplier)])
        invoice.party = party
        invoice.payment_term = payment_term

        Account = Model.get('account.account')    
        expense, = Account.find([
            ('kind', '=', 'expense'),
            ('name', '=', sGetFeatureData(context, 'account.template,main_expense')),
            ('company', '=', company.id),
            ])

        InvoiceLine = Model.get('account.invoice.line')
        Product = Model.get('product.product')
        for row in context.table:
            line = InvoiceLine()
            invoice.lines.append(line)
            # Note that this uses the heading 'description' rather than 'name'
            lProducts = Product.find([('description', '=', row['description'])])
            if lProducts:
                line.product = lProducts[0]
                # 'unit_price' is derived from the Product
            else:
                line.account = expense
                line.description = row['description']
                line.unit_price = Decimal(row['unit_price'])
            line.quantity = \
                    string_to_python('quantity', row['quantity'], InvoiceLine)

        invoice.save()

# Buy the Services Bought, 10% Sales Tax
@step('TS/AIS Post the invoice with description "{uDescription}" and assert the taxes named "{uTaxName}" with fields')
def step_impl(context, uDescription, uTaxName):
    current_config = context.oProteusConfig

    Party = Model.get('party.party')
    sCompanyName = sGetFeatureData(context, 'party,company_name')
    party, = Party.find([('name', '=', sCompanyName)])
    Company = Model.get('company.company')
    company, = Company.find([('party.id', '=', party.id)])

    Invoice = Model.get('account.invoice')
    invoice, = Invoice.find(['description', '=', uDescription])
        
    assert invoice.untaxed_amount == Decimal(110)
    assert invoice.tax_amount == Decimal(10)
    assert invoice.total_amount == Decimal(120)
    Invoice.post([invoice.id], current_config.context)
    
    invoice.reload()
    assert invoice.state ==u'posted'
    assert invoice.untaxed_amount == Decimal(110)
    assert invoice.tax_amount == Decimal(10)
    assert invoice.total_amount == Decimal(120)
    
    Account = Model.get('account.account')    
    payable, = Account.find([
        ('kind', '=', 'payable'),
        ('name', '=', sGetFeatureData(context, 'account.template,main_payable')),
        ('company', '=', company.id),
        ])
    payable.reload()
    assert (payable.debit, payable.credit) == \
        (Decimal(0), Decimal(120))
    
    expense, = Account.find([
        ('kind', '=', 'expense'),
        ('name', '=', sGetFeatureData(context, 'account.template,main_expense')),
        ('company', '=', company.id),
        ])
    expense.reload()
    assert (expense.debit, expense.credit) == \
        (Decimal(110), Decimal(0))
    
    account_tax, = Account.find([
        ('kind', '=', 'other'),
        ('name', '=', sGetFeatureData(context, 'account.template,main_tax')),
        ('company', '=', company.id),
        ])
    account_tax.reload()
    assert (account_tax.debit, account_tax.credit) == \
           (Decimal(10), Decimal(0))

    Tax = Model.get('account.tax')
    tax, = Tax.find([('name', '=', uTaxName)])
    invoice_base_code = tax.invoice_base_code
    invoice_base_code.reload()
    assert invoice_base_code.sum == Decimal(100)
    
    invoice_tax_code = tax.invoice_tax_code
    invoice_tax_code.reload()
    assert invoice_tax_code.sum == Decimal(10)
    
    credit_note_base_code = tax.credit_note_base_code
    credit_note_base_code.reload()
    assert credit_note_base_code.sum == Decimal(0)
    
    credit_note_tax_code = tax.credit_note_tax_code
    credit_note_tax_code.reload()
    assert credit_note_tax_code.sum == Decimal(0)

# Buy the Services Bought
@step('TS/AIS Create a credit note for the invoice with description "{uDescription}" and assert the amounts')
def step_impl(context, uDescription):
    current_config = context.oProteusConfig

    Invoice = Model.get('account.invoice')
    invoice, = Invoice.find(['description', '=', uDescription])

    credit = Wizard('account.invoice.credit', [invoice])
    credit.form.with_refund = False
    credit.execute('credit')
    
    credit_note, = Invoice.find([('type', '=', 'in_credit_note')])
    assert credit_note.state == u'draft'
    assert credit_note.untaxed_amount == invoice.untaxed_amount
    assert credit_note.tax_amount == invoice.tax_amount
    assert credit_note.total_amount == invoice.total_amount
