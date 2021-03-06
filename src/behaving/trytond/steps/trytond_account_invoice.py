# -*- mode: python; py-indent-offset: 4; coding: utf-8-unix; encoding: utf-8 -*-
"""


"""
from behave import *
import proteus

import datetime
from dateutil.relativedelta import relativedelta
from decimal import Decimal

from .support import modules
from .support.tools import *
from .support.fields import string_to_python, sGetFeatureData, vSetFeatureData

TODAY = datetime.date.today()



# Create an invoice on Date "2014-07-01" with description "Jackson and Grimes 2014 Bill Adjustments" and a PaymentTerm named "Term 30 days" to supplier "Jackson and Grimes" with following |description|quantity|unit_price|account|tax_amount|base_amount|tax_code_id|base_code_id|tax_account|currency| fields'

@step('Create an Invoice on Date "{uDate}" with description "{uDescription}" and a PaymentTerm named "{uPaymentTerm}" to supplier "{uSupplier}" with following |description|quantity|unit_price|account|tax_amount|base_amount|tax_code_id|base_code_id|tax_account|currency| fields')
@step('Create an Invoice on Date "{uDate}" with description "{uDescription}" and with VAT and a PaymentTerm named "{uPaymentTerm}" to supplier "{uSupplier}" with following |description|quantity|unit_price|account|tax_amount|base_amount|tax_code_id|base_code_id|tax_account|currency| fields')
def step_impl(context, uDate, uDescription, uPaymentTerm, uSupplier):
    """
    Given \
Create an Invoice on Date "{uDate}" with description "{uDescription}" to supplier
"{uSupplier}" with following |description|quantity|unit_price|account| fields
Note that this uses the heading description rather than name
  | description       | quantity   | unit_price | account      |tax_amount|base_amount|tax_code_id|base_code_id|tax_account| currency |
  | Services Bought   | 5	   | 		|              | | | | | | |          |
  | Test     	      | 1	   | 10.00	| Main Expense | | | | | | | USD      |
    """
    sType = 'in_invoice'
    assert context.table
    oCreateAnInvoice(context, uDate, uDescription, uPaymentTerm, uSupplier, sType)


@step('Create an Invoice on Date "{uDate}" with description "{uDescription}" and a PaymentTerm named "{uPaymentTerm}" to supplier "{uSupplier}" with following |description|quantity|unit_price|account|currency| fields')
def step_impl(context, uDate, uDescription, uPaymentTerm, uSupplier):
    """
    Given \
Create an Invoice on Date "{uDate}" with description "{uDescription}" to supplier
"{uSupplier}" with following |description|quantity|unit_price|account| fields
Note that this uses the heading description rather than name
  | description       | quantity   | unit_price | account      | currency |
  | Services Bought   | 5	   | 		|              |          |
  | Test     	      | 1	   | 10.00	| Main Expense | USD      |
    """
    sType = 'in_invoice'
    assert context.table
    oCreateAnInvoice(context, uDate, uDescription, uPaymentTerm, uSupplier, sType)

@step('Create an Invoice on Date "{uDate}" with description "{uDescription}" and a PaymentTerm named "{uPaymentTerm}" to customer "{uCustomer}" with following |description|quantity|unit_price|account|tax_amount|base_amount|tax_code_id|base_code_id|tax_account|currency| fields')
@step('Create an Invoice on Date "{uDate}" with description "{uDescription}" and with VAT and a PaymentTerm named "{uPaymentTerm}" to customer "{uCustomer}" with following |description|quantity|unit_price|account|tax_amount|base_amount|tax_code_id|base_code_id|tax_account|currency| fields')
def step_impl(context, uDate, uDescription, uPaymentTerm, uCustomer):
    """
    Given \
Create an Invoice with description "{uDescription}" to customer
"{uCustomer}" with following |description|quantity|unit_price|account|currency| fields
Note that this uses the heading description rather than name
  | description       | quantity   | unit_price | account      |tax_amount|base_amount|tax_code_id|base_code_id|tax_account|currency |
  | Services Bought   | 5	   | 		|              | | | | | | |          |
  | Test     	      | 1	   | 10.00	| Main Revenue | | | | | | | USD      |
    """
    sType = 'out_invoice'
    assert context.table
    oCreateAnInvoice(context, uDate, uDescription, uPaymentTerm, uCustomer, sType)


@step('Create an Invoice on Date "{uDate}" with description "{uDescription}" and a PaymentTerm named "{uPaymentTerm}" to customer "{uCustomer}" with following |description|quantity|unit_price|account|currency| fields')
def step_impl(context, uDate, uDescription, uPaymentTerm, uCustomer):
    """
    Given \
Create an Invoice on Date "{uDate}" with description "{uDescription}" to customer
"{uCustomer}" with following |description|quantity|unit_price|account|currency| fields
Note that this uses the heading description rather than name
  | description       | quantity   | unit_price | account      | currency |
  | Services Bought   | 5	   | 		|              |          |
  | Test     	      | 1	   | 10.00	| Main Revenue | USD      |
    """
    sType = 'out_invoice'
    assert context.table
    oCreateAnInvoice(context, uDate, uDescription, uPaymentTerm, uCustomer, sType)

def oCreateAnInvoice(context, uDate, uDescription, uPaymentTerm, uParty, sType):
    current_config = context.oProteusConfig

    Party = proteus.Model.get('party.party')
    sCompanyName = sGetFeatureData(context, 'party,company_name')
    party, = Party.find([('name', '=', sCompanyName)])
    Company = proteus.Model.get('company.company')
    company, = Company.find([('party.id', '=', party.id)])

    oParty, = Party.find([('name', '=', uParty),])
    Invoice = proteus.Model.get('account.invoice')
    # creates unconditionally
    if True or not Invoice.find([('party.id',  '=', oParty.id),
                            ('company.id',  '=', company.id),
                            ('description', '=', uDescription)]):
        invoice = Invoice()
        invoice.type = sType
        if uDate.lower() == 'today' or uDate.lower() == 'now':
            oDate = TODAY
        else:
            oDate = datetime.date(*map(int, uDate.split('-')))
        invoice.invoice_date = oDate
        invoice.accounting_date = invoice.invoice_date
        invoice.description = uDescription

        if uParty:
            party, = Party.find([('name', '=', uParty)])
            invoice.party = party

        PaymentTerm = proteus.Model.get('account.invoice.payment_term')
        payment_term, = PaymentTerm.find([('name', '=', uPaymentTerm)])
        invoice.payment_term = payment_term

        Account = proteus.Model.get('account.account')
        if sType == 'in_invoice':
            sMainKind = 'payable'
            uKind = 'expense'
            # use Costs of Goods Sold 5013
            sCSogsName = sGetFeatureData(context, 'account.template,main_cogs')
        else:
            sMainKind = 'receivable'
            uKind = 'revenue'
            # use Sales of Goods 4013
            # sCSogsName = sGetFeatureData(context, 'account.template,main_sogs')
            sCSogsName = 'Sales of Goods'
        oMain, = Account.find([
            ('kind', '=', sMainKind),
            ('name', '=', sGetFeatureData(context, 'account.template,main_'+sMainKind)),
            ('company', '=', company.id),
        ])
        invoice.account = oMain
        # journal?
        # period?

        oLineDefault, = Account.find([
            ('kind', '=', uKind),
            ('name', '=', sGetFeatureData(context, 'account.template,main_'+uKind)),
            ('company', '=', company.id),
        ])

        InvoiceLine = proteus.Model.get('account.invoice.line')
        InvoiceTax = proteus.Model.get('account.invoice.tax')
        TaxCode = proteus.Model.get('account.tax.code')
        Product = proteus.Model.get('product.product')
        Currency = proteus.Model.get('currency.currency')
        for row in context.table:
            # FixMe: lines can have tax
            # FixMe: unit_digits=4
            oLine = invoice.lines.new()
            #! assert oLine.unit_digits == 4
            if u'currency' in context.table.headings and row['currency']:
                oCurrency, = Currency.find([('code', '=', row['currency'])])
                oLine.currency = oCurrency
            if u'party' in context.table.headings and row['party']:
                oLineParty, = Party.find([('name', '=', row['party'])])
                oLine.party = oLineParty
            uQuantity = row['quantity']
            if uQuantity:
                oLine.quantity = \
                    string_to_python('quantity', uQuantity, InvoiceLine)
            # Note that this uses the heading 'description' rather than 'name'
            lProducts = Product.find([('description', '=', row['description'])])
            if lProducts:
                oLine.product = lProducts[0]
                # 'unit_price' is derived from the Product
            else:
                oLine.description = row['description']
                #? need this if oLine.product too? No it's derived
                if row['account']:
                    # FixMe: domain for oLine.account is ['kind', '=', 'expense']
                    uNameOrCode = row['account']
                    # if '0' <= uNameOrCode[0] <= '9'
                    try:
                        int(uNameOrCode)
                    except ValueError:
                        oLine.account, = Account.find([
                            ('name', '=', uNameOrCode),
                            ('company.id', '=', company.id)])
                    else:
                        oLine.account, = Account.find([
                            ('code', '=', uNameOrCode),
                            ('company.id', '=', company.id)])
                    # uKind is very restrictive - must be one of
                    # revenue/expense and cannot be stock
                    # use Costs of Goods Sold 5013
                    # to hold stock sales as an expense and then JV
                    if oLine.account.kind in ['income', 'stock']:
                        oLine.account, = Account.find([
                            ('kind', '=', uKind),
                            ('name', '=', sCSogsName),
                            ('company.id', '=', company.id)])
                        assert oLine.account.kind in ['revenue', 'expense']
                        # FixMe: make the JV line for the feature
                else:
                    oLine.account = oLineDefault
                uUnitPrice = row['unit_price']
                if uUnitPrice and uUnitPrice != u'0.00':
                    oLine.unit_price = Decimal(uUnitPrice)
                #? - no - leads to AttributeErrorbecause the invoice isnt saved
                # : 'account.invoice' Model has no attribute 'state': None
                # oLine.save()

            if u'tax_account' in context.table.headings and row['tax_account']:
                # tax_amount|base_amount|tax_code_id|base_code_id|tax_account
                oInvoiceTax = invoice.taxes.new()
                # invoice.taxes.append(oInvoiceTax)
                if uQuantity:
                    oInvoiceTax.description = 'VAT'
                else:
                    oInvoiceTax.description = row['description']
                oInvoiceTax.amount = Decimal(row['tax_amount'])
                # code account.tax.code
                oInvoiceTax.base = Decimal(row['base_amount'])
                oInvoiceTax.account, = Account.find([
                        ('kind', '!=', 'view'),
                        ('code', '=', row['tax_account']),
                        ('company.id', '=', company.id)])
                oInvoiceTax.base_sign = Decimal(1) #?
                oInvoiceTax.base_code, = TaxCode.find([
                        ('code', '=', row['base_code_id']),
                        ('company.id', '=', company.id)])
                oInvoiceTax.tax_sign = Decimal(1) #?
                oInvoiceTax.tax_code, = TaxCode.find([
                        ('code', '=', row['tax_code_id']),
                        ('company.id', '=', company.id)])

        invoice.save()

    assert Invoice.find([('party.id',  '=', oParty.id),
                             ('company.id',  '=', company.id),
                             ('description', '=', uDescription)])

@step('Action "{uAct}" on Date "{uDate}" the Invoice with description "{uDescription}" as user named "{uUser}" products from party "{uSupplier}"')
def step_impl(context, uAct, uDate, uDescription, uUser, uSupplier):
    """
    Given \
    Action "post" on Date "TODAY" the Invoice with description "Invoice #1"
    as user named "Account" products from party "Supplier"

    """
    oActOnInvoice(context, uAct, uDate, uDescription, uUser, uSupplier, 'description')

def oActOnInvoice(context, uAct, uDate, uDescription, uUser, uSupplier, sUniq='description'):
    config = context.oProteusConfig

    Party = proteus.Model.get('party.party')
    sCompanyName = sGetFeatureData(context, 'party,company_name')
    party, = Party.find([('name', '=', sCompanyName)])
    Company = proteus.Model.get('company.company')
    company, = Company.find([('party.id', '=', party.id)])

    User = proteus.Model.get('res.user')

    Invoice = proteus.Model.get('account.invoice')
    # FixMe: Tryton doesnt pass the Purchase description
    # to the invoice that it generates
    supplier, = Party.find([('name', '=', uSupplier),])
    invoice, = Invoice.find([('party.id',  '=', supplier.id),
                             ('company.id',  '=', company.id),
                             (sUniq, '=', uDescription)])

    account_user, = User.find([('name', '=', uUser)])
    proteus.config.user = account_user.id
    oDate = oDateFromUDate(uDate)
    invoice.invoice_date = oDate
    invoice.accounting_date = invoice.invoice_date
    #? reference
    invoice.save()

    if uAct == u'post':
        invoice.click('post')
    elif uAct == u'validate_invoice':
        invoice.click('validate_invoice')
    else:
        raise ValueError("uAct must be one of validate_invoice or post: " + uAct)
    invoice.reload()

    user, = User.find([('login', '=', 'admin')])
    proteus.config.user = user.id

