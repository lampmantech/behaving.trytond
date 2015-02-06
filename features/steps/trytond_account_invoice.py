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
@step('Create an invoice on date "{uDate}" with description "{uDescription}" and a PaymentTerm named "{uPaymentTerm}" to supplier "{uSupplier}" with following |description|quantity|unit_price|account|currency| fields')
def step_impl(context, uDate, uDescription, uPaymentTerm, uSupplier):
    """
Create an invoice with description "{uDescription}" to supplier
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
@step('Create an invoice on date "{uDate}" with description "{uDescription}" and a PaymentTerm named "{uPaymentTerm}" to customer "{uCustomer}" with following |description|quantity|unit_price|account|currency| fields')
def step_impl(context, uDate, uDescription, uPaymentTerm, uCustomer):
    """
Create an invoice with description "{uDescription}" to customer
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

    Invoice = proteus.Model.get('account.invoice')
    #? company.id
    if not Invoice.find(['description', '=', uDescription]):
        invoice = Invoice()
        invoice.type = sType
        if uDate.lower() == 'today' or uDate.lower() == 'now':
            oDate = TODAY
        else:
            oDate = datetime.date(*map(int, uDate.split('-')))
        invoice.invoice_date = oDate
        invoice.accounting_date = invoice.invoice_date
        invoice.description = uDescription

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
        for row in context.table:
            # lines can have currency
            line = InvoiceLine()
            invoice.lines.append(line)
            # Note that this uses the heading 'description' rather than 'name'
            lProducts = Product.find([('description', '=', row['description'])])
            if row['currency']:
                # FixMe: row['currency']
                pass
            if lProducts:
                line.product = lProducts[0]
                # 'unit_price' is derived from the Product
            else:
                line.description = row['description']
                line.unit_price = Decimal(row['unit_price'])
                #? need this if line.product too? No it's derived
                if row['account']:
                    # FixMe: domain for line.account is ['kind', '=', 'expense']
                    line.account, = Account.find([('kind', '=', uKind),
                                                 ('name', '=', row['account']),
                                                 ('company.id', '=', company.id)])
                else:
                    line.account = oLineDefault
            line.quantity = \
                    string_to_python('quantity', row['quantity'], InvoiceLine)

        invoice.save()

@step('Action "{uAct}" on date "{uDate}" the Invoice with description "{uDescription}" as user named "{uUser}" products from party "{uSupplier}"')
def step_impl(context, uAct, uDate, uDescription, uUser, uSupplier):
    """
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
    
    supplier, = Party.find([('name', '=', uSupplier),])
    Invoice = proteus.Model.get('account.invoice')
    # Groddy but Tryton doesnt pass the Pruchase description
    # to the invoive that it generates
    l = Invoice.find([('party.id',  '=', supplier.id),
                      ('company.id',  '=', company.id),
                      ('description', '=', uDescription)])
    if l:
        invoice = l[0]
    else:
        l = Invoice.find([('party.id',  '=', supplier.id),
                          ('company.id',  '=', company.id),])
        if l:
            invoice = l[0]
            #? maybe set the description here?
            invoice.description = uDescription
        else:
            raise UserError('Invoice not found with description "%s"' % (
                uDescription,))
    
    account_user, = User.find([('name', '=', uUser)])
    proteus.config.user = account_user.id
    if uDate.lower() == 'today' or uDate.lower() == 'now':
        oDate = TODAY
    else:
        oDate = datetime.date(*map(int, uDate.split('-')))
    invoice.invoice_date = oDate

    cls_transitions = (
        ('draft', 'validated'),
        ('validated', 'posted'),
        ('draft', 'posted'),
        ('posted', 'paid'),
        ('validated', 'draft'),
        ('paid', 'posted'),
        ('draft', 'cancel'),
        ('validated', 'cancel'),
        ('posted', 'cancel'),
        ('cancel', 'draft'),
    )

    if uAct == u'post':
        invoice.click('post')
    elif uAct == u'validate_invoice':
        invoice.click('validate_invoice')
    else:
        raise ValueError("uAct must be one of validate_invoice or post: " + uAct)
    invoice.reload()
    
    user, = User.find([('login', '=', 'admin')])
    proteus.config.user = user.id

