# -*- mode: python; py-indent-offset: 4; coding: utf-8-unix; encoding: utf-8 -*-
"""


"""
from behave import *
import proteus

import datetime
from dateutil.relativedelta import relativedelta
from decimal import Decimal

from .support.fields import string_to_python, sGetFeatureData, vSetFeatureData
from .support import modules
from .support.tools import *

TODAY = datetime.date.today()


# TODAY, Buy the Services Bought, Term 30 days, Supplier
@step('Create an Invoice on date "{uDate}" with description "{uDescription}" and with VAT and a PaymentTerm named "{uPaymentTerm}" to supplier "{uSupplier}" with following |description|quantity|unit_price|account|VAT|currency| fields')
@step('Create an Invoice on date "{uDate}" with description "{uDescription}" and a PaymentTerm named "{uPaymentTerm}" to supplier "{uSupplier}" with following |description|quantity|unit_price|account|currency| fields')
def step_impl(context, uDate, uDescription, uPaymentTerm, uSupplier):
    r"""
    Given \
Create an Invoice on date "{uDate}" with description "{uDescription}" to supplier
"{uSupplier}" with following |description|quantity|unit_price|account| fields
Note that this uses the heading description rather than name
  | description       | quantity   | unit_price | account      | currency |
  | Services Bought   | 5	   | 		|              |          |
  | Test     	      | 1	   | 10.00	| Main Expense | USD      |
    """
    sType = 'in_invoice'
    assert context.table
    oCreateAnInvoice(context, uDate, uDescription, uPaymentTerm, uSupplier, sType)

# TODAY, Services Sold, Customer
@step('Create an Invoice on date "{uDate}" with description "{uDescription}" and with VAT and a PaymentTerm named "{uPaymentTerm}" to customer "{uCustomer}" with following |description|quantity|unit_price|account|VAT|currency| fields')
@step('Create an Invoice on date "{uDate}" with description "{uDescription}" and a PaymentTerm named "{uPaymentTerm}" to customer "{uCustomer}" with following |description|quantity|unit_price|account|currency| fields')
def step_impl(context, uDate, uDescription, uPaymentTerm, uCustomer):
    r"""
    Given \
Create an Invoice with description "{uDescription}" to customer
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

    supplier, = Party.find([('name', '=', uParty),])
    Invoice = proteus.Model.get('account.invoice')
    if not Invoice.find([('party.id',  '=', supplier.id),
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
        else:
            sMainKind = 'receivable'
            uKind = 'revenue'
        oMain, = Account.find([
            ('kind', '=', sMainKind),
            ('name', '=', sGetFeatureData(context, 'account.template,main_'+sMainKind)),
            ('company', '=', company.id),
        ])
        invoice.account = oMain

        oLineDefault, = Account.find([
            ('kind', '=', uKind),
            ('name', '=', sGetFeatureData(context, 'account.template,main_'+uKind)),
            ('company', '=', company.id),
        ])

        InvoiceLine = proteus.Model.get('account.invoice.line')
        Product = proteus.Model.get('product.product')
        Currency = proteus.Model.get('currency.currency')
        for row in context.table:
            # FixMe: lines can have currency
            line = InvoiceLine()
            invoice.lines.append(line)
            # Note that this uses the heading 'description' rather than 'name'
            lProducts = Product.find([('description', '=', row['description'])])
            if u'currency' in context.table.headings and row['currency']:
                oCurrency, = Currency.find([('code', '=', row['currency'])])
                line.currency = oCurrency
            if u'party' in context.table.headings and row['party']:
                oLineParty, = Party.find([('name', '=', row['party'])])
                line.party = oLineParty
            if lProducts:
                line.product = lProducts[0]
                # 'unit_price' is derived from the Product
            else:
                line.description = row['description']
                line.unit_price = Decimal(row['unit_price'])
                #? need this if line.product too? No it's derived
                if row['account']:
                    # FixMe: domain for line.account is ['kind', '=', 'expense']
                    line.account, = Account.find([
                        ('kind', '=', uKind),
                        ('name', '=', row['account']),
                        ('company.id', '=', company.id)])
                else:
                    line.account = oLineDefault
            line.quantity = \
                    string_to_python('quantity', row['quantity'], InvoiceLine)
        invoice.save()
        
    invoice, = Invoice.find([('party.id',  '=', supplier.id),
                             ('company.id',  '=', company.id),
                             ('description', '=', uDescription)])

@step('Action "{uAct}" on date "{uDate}" the Invoice with description "{uDescription}" as user named "{uUser}" products from party "{uSupplier}"')
def step_impl(context, uAct, uDate, uDescription, uUser, uSupplier):
    r"""
    Given \
    Action "post" on date "TODAY" the Invoice with description "Invoice #1"
    as user named "Account" products from party "Supplier"

    """
    config = context.oProteusConfig

    Party = proteus.Model.get('party.party')
    sCompanyName = sGetFeatureData(context, 'party,company_name')
    party, = Party.find([('name', '=', sCompanyName)])
    Company = proteus.Model.get('company.company')
    company, = Company.find([('party.id', '=', party.id)])

    User = proteus.Model.get('res.user')

    Invoice = proteus.Model.get('account.invoice')
    # FixMe: Tryton doesnt pass the Purchase description
    # to the invoive that it generates
    supplier, = Party.find([('name', '=', uSupplier),])
    invoice, = Invoice.find([('party.id',  '=', supplier.id),
                             ('company.id',  '=', company.id),
                             ('description', '=', uDescription)])

    account_user, = User.find([('name', '=', uUser)])
    proteus.config.user = account_user.id
    oDate = oDateFromUDate(uDate)
    invoice.invoice_date = oDate
    invoice.accounting_date = invoice.invoice_date
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

