# -*- mode: python; py-indent-offset: 4; coding: utf-8-unix; encoding: utf-8 -*-
"""


"""
from behave import *
import proteus

import os, sys, datetime
from decimal import Decimal

from .support.fields import string_to_python, sGetFeatureData, vSetFeatureData
from .support import modules
from .support.tools import *
from .support.stepfuns import vAssertContentTable

TODAY = datetime.date.today()

#features/trytond/account_stock_anglo_saxon/?
#? shipment_method
@step('Sale on date "{uDate}" with description "{uDescription}" as user named "{uUser}" products to customer "{uCustomer}" with PaymentTerm "{uTerm}" and InvoiceMethod "{uMethod}" with |product|quantity|description| fields')
def step_impl(context, uDate, uDescription, uUser, uCustomer, uTerm, uMethod):
    """
    Sale on date "TODAY" with description "Description"
    as user named "Sale" products to customer "Customer" 
    with PaymentTerm "Direct" and InvoiceMethod "order"
    If the quantity is the word comment, the line type is set to comment.
    with |product|quantity|description| fields
      | description | quantity | line_description |
      | product | 2.0      |             |
      | product | comment  | Comment     |
      | product | 3.0      |             |
    """
    # shouls we make quantity == 'comment'
    config = context.oProteusConfig

    Sale = proteus.Model.get('sale.sale')

    Party = proteus.Model.get('party.party')
    sCompanyName = sGetFeatureData(context, 'party,company_name')
    party, = Party.find([('name', '=', sCompanyName)])
    Company = proteus.Model.get('company.company')
    company, = Company.find([('party.id', '=', party.id)])
    
    Product = proteus.Model.get('product.product')
    customer, = Party.find([('name', '=', uCustomer),])

    User = proteus.Model.get('res.user')
    sale_user, = User.find([('name', '=', uUser)])
    proteus.config.user = sale_user.id

    PaymentTerm = proteus.Model.get('account.invoice.payment_term')
    payment_term, = PaymentTerm.find([('name', '=', uTerm)])

    if not Sale.find([('description', '=', uDescription),
                      ('company.id',  '=', company.id),
                      ('party.id', '=', customer.id)]):
        sale = Sale()
        # also has shipment_method: 'manual', 'Manual', 'order', 'invoice',

        sale.party = customer
        sale.payment_term = payment_term
        sale.invoice_method = uMethod
        sale.description = uDescription
        if uDate.lower() == 'today' or uDate.lower() == 'now':
            oDate = TODAY
        else:
            oDate = datetime.date(*map(int, uDate.split('-')))
        sale.sale_date = oDate
        # sales also have warehouse, currency
        sale.save()

        SaleLine = proteus.Model.get('sale.line')
        for row in context.table:
            product, = Product.find([('description', '=', row['description'])])
            sale_line = SaleLine()
            sale.lines.append(sale_line)
            sale_line.product = product
            if row['quantity'] == 'comment':
                sale_line.type = 'comment'
            else:
                # type == 'line'
                sale_line.quantity = float(row['quantity'])
            if row['line_description']:
                sale_line.description = row['line_description'] or ''
            #? why no sale_line.save()
        sale.save()
        
    user, = User.find([('login', '=', 'admin')])
    proteus.config.user = user.id
    
    sale, = Sale.find([('description', '=', uDescription),
                       ('company.id',  '=', company.id),
                       ('party.id', '=', customer.id)])


@step('Sale "{uAct}" on date "{uDate}" the S. O. with description "{uDescription}" as user named "{uUser}" products from customer "{uCustomer}"')
def step_impl(context, uAct, uDate, uDescription, uUser, uCustomer):
    """
    Sale "quote" on date "TODAY" the S.O. with description "P. O #1" 
    as user named "Sale" products from customer "Customer"
    """
    config = context.oProteusConfig
    
    Party = proteus.Model.get('party.party')
    sCompanyName = sGetFeatureData(context, 'party,company_name')
    party, = Party.find([('name', '=', sCompanyName)])
    Company = proteus.Model.get('company.company')
    company, = Company.find([('party.id', '=', party.id)])

    User = proteus.Model.get('res.user')
    
    customer, = Party.find([('name', '=', uCustomer),])
    Sale = proteus.Model.get('sale.sale')
    sale, = Sale.find([('party.id',  '=', customer.id),
                       ('company.id',  '=', company.id),
                       ('description', '=', uDescription)])

    sale_user, = User.find([('name', '=', uUser)])
    proteus.config.user = sale_user.id
    if uAct == 'quote':
        Sale.quote([sale.id], config.context)
        assert sale.state == u'quotation'
    elif uAct == 'confirm':
        Sale.confirm([sale.id], config.context)
        assert sale.state == u'confirmed'
    elif uAct == 'process':
        Sale.process([sale.id], config.context)
        assert sale.state == u'processing'
    else:
        raise ValueError("uAct must be one of quote confirm process: " + uAct)
    sale.reload()
    user, = User.find([('login', '=', 'admin')])
    proteus.config.user = user.id

#See also @step('T/ASAS/SASAS Send 5 products on the S. O. with description "{uDescription}" to customer "{uCustomer}"')

@step('Invoice "{uAct}" on date "{uDate}" the S. O. with description "{uDescription}" as user named "{uUser}" products from customer "{uCustomer}"')
def step_impl(context, uAct, uDate, uDescription, uUser, uCustomer):
    """
    Invoice "post" on date "TODAY" the S. O. with description "S. O #1" 
    as user named "Account" products from customer "Customer"
    """
    config = context.oProteusConfig
    
    Party = proteus.Model.get('party.party')
    sCompanyName = sGetFeatureData(context, 'party,company_name')
    party, = Party.find([('name', '=', sCompanyName)])
    Company = proteus.Model.get('company.company')
    company, = Company.find([('party.id', '=', party.id)])

    User = proteus.Model.get('res.user')
    
    customer, = Party.find([('name', '=', uCustomer),])
    Sale = proteus.Model.get('sale.sale')
    sale, = Sale.find([('party.id',  '=', customer.id),
                               ('company.id',  '=', company.id),
                               ('description', '=', uDescription)])
    
    account_user, = User.find([('name', '=', uUser)])
    proteus.config.user = account_user.id
    Invoice = proteus.Model.get('account.invoice')
    invoice = Invoice(sale.invoices[0].id)
    if uDate.lower() == 'today' or uDate.lower() == 'now':
        oDate = TODAY
    else:
        oDate = datetime.date(*map(int, uDate.split('-')))
    invoice.invoice_date = oDate
    if uAct == u'post':
        invoice.click('post')
    else:
        raise ValueError("uAct must be one of post: " + uAct)
    invoice.reload()
    
    user, = User.find([('login', '=', 'admin')])
    proteus.config.user = user.id



# Customer, Sell 5 products
@step('Create a sales order with description "{uDescription}" to customer "{uCustomer}" on date "{uDate}" with |name|value| fields')
def step_impl(context, uDescription, uCustomer, uDate):
    """
    T/ASAS/SASAS Create a sales order with description "{uDescription}" to customer "{uCustomer}" with fields
	  | name              | value    |
	  | invoice_method    | shipment |
	  | payment_term      | Direct   |
    Idempotent.
    """
    current_config = context.oProteusConfig

    Sale = proteus.Model.get('sale.sale')

    Party = proteus.Model.get('party.party')
    customer, = Party.find([('name', '=', uCustomer)])
    sCompanyName = sGetFeatureData(context, 'party,company_name')
    party, = Party.find([('name', '=', sCompanyName)])
    Company = proteus.Model.get('company.company')
    company, = Company.find([('party.id', '=', party.id)])

    if not Sale.find([('description', '=', uDescription),
                      ('company', '=', company.id),
                      ('party.id', '=', customer.id)]):
        sale = Sale()
        sale.party = customer
        sale.description = uDescription
        if uDate.lower() == 'today' or uDate.lower() == 'now':
            oDate = TODAY
        else:
            oDate = datetime.date(*map(int, uDate.split('-')))
        sale.sale_date = oDate
        
        # 'payment_term', 'invoice_method'
        for row in context.table:
            setattr(sale, row['name'],
                    string_to_python(row['name'], row['value'], Sale))
        sale.save()

    oSale, = Sale.find([('description', '=', uDescription),
                      ('company', '=', company.id),
                      ('party.id', '=', customer.id)])

    
@step('Sell Products on the S. O. with description "{uDescription}" to customer "{uCustomer}" with |description|quantity| fields')
def step_impl(context, uDescription, uCustomer):
    """
    Sell products on the S. O. with description "uDescription"
    to customer "uCustomer" with quantities
	  | description     | quantity |
	  | Product Fixed   | 2.0      |
	  | Product Average | 3.0      |

    Idempotent.
    """
    current_config = context.oProteusConfig

    Sale = proteus.Model.get('sale.sale')

    Party = proteus.Model.get('party.party')
    customer, = Party.find([('name', '=', uCustomer)])
    sCompanyName = sGetFeatureData(context, 'party,company_name')
    party, = Party.find([('name', '=', sCompanyName)])
    Company = proteus.Model.get('company.company')
    company, = Company.find([('party.id', '=', party.id)])

    sale, = Sale.find([('description', '=', uDescription),
                       ('company', '=', company.id),
                       ('party.id', '=', customer.id)])
    if len(sale.lines) <= 0:
        SaleLine = proteus.Model.get('sale.line')

        Product = proteus.Model.get('product.product')
        # purchase.moves[0].product.description == u'product_fixed'
        # purchase.moves[1].product.description == u'product_average' 5.0
        for row in context.table:
            uDescription = row['description']
            fQuantity = float(row['quantity'])
            # allow 0 (<0.0001) quantity - just skip them
            if fQuantity < 0.0001: continue
            product = Product.find([('description', '=', uDescription)])[0]

            sale_line = SaleLine()
            sale.lines.append(sale_line)
            sale_line.product = product
            sale_line.quantity = fQuantity
            sale_line.description = uDescription
            #? sale_line.save()
        sale.save()

        Sale.quote([sale.id], current_config.context)
        Sale.confirm([sale.id], current_config.context)
        Sale.process([sale.id], current_config.context)

        assert sale.state == u'processing'

@step('Ship the products on the S. O. with description "{uDescription}" to customer "{uCustomer}"')
def step_impl(context, uDescription, uCustomer):
    """
    From: T/ASAS/SASAS 
    Ship the products on the S. O. with description "{uDescription}" 
    to customer "{uCustomer}"
    NOT idempotent
    """
    current_config = context.oProteusConfig

    ShipmentOut = proteus.Model.get('stock.shipment.out')

    Sale = proteus.Model.get('sale.sale')
    SaleLine = proteus.Model.get('sale.line')

    Party = proteus.Model.get('party.party')
    customer, = Party.find([('name', '=', uCustomer)])
    sCompanyName = sGetFeatureData(context, 'party,company_name')
    party, = Party.find([('name', '=', sCompanyName)])
    Company = proteus.Model.get('company.company')
    company, = Company.find([('party.id', '=', party.id)])

    sale, = Sale.find([('description', '=', uDescription),
                       ('company', '=', company.id),
                       ('party.id', '=', customer.id)])

    shipment, = sale.shipments
    #? Pass the dates in?
    if sale.sale_date and not shipment.planned_date:
        shipment.planned_date = sale.sale_date
    #? effective_date
    if not ShipmentOut.assign_try([shipment.id], current_config.context):
        sys.__stderr__.write('>>> WARN: forcing shipment for sale with description: '+uDescription+'\n')
        assert ShipmentOut.assign_force([shipment.id], current_config.context)
    #? why did this become necessary when it wasnt before?
    shipment.reload()
    # not idempotent
    assert shipment.state == u'assigned'

    shipment.reload()
    # not idempotent
    ShipmentOut.pack([shipment.id], current_config.context)
    #? why did this reload() become necessary when it wasnt before?
    #? all we did was add:
    #?    shipment.planned_date = sale.sale_date
    shipment.reload()
    assert shipment.state == u'packed'

    shipment.reload()
    # not idempotent
    ShipmentOut.done([shipment.id], current_config.context)
    #? why did this become necessary when it wasnt before?
    shipment.reload()
    assert shipment.state == u'done'

# Customer
@step('Post customer Invoice for the S. O. with description "{uDescription}" to customer "{uCustomer}"')
def step_impl(context, uDescription, uCustomer):
    """
    From T/ASAS/SASAS
    Post customer Invoice for the Sales Order with description "uDescription"
    to customer "uCustomer"

    Not idempotent.
    """
    current_config = context.oProteusConfig

    Sale = proteus.Model.get('sale.sale')

    Party = proteus.Model.get('party.party')
    customer, = Party.find([('name', '=', uCustomer)])
    sCompanyName = sGetFeatureData(context, 'party,company_name')
    party, = Party.find([('name', '=', sCompanyName)])
    Company = proteus.Model.get('company.company')
    company, = Company.find([('party.id', '=', party.id)])

    sale, = Sale.find([('invoice_method', '=', 'shipment'),
                       ('description', '=', uDescription),
                       ('company', '=', company.id),
                       ('party.id', '=', customer.id)])
    # not idempotent
    sale.reload()

    Invoice = proteus.Model.get('account.invoice')
    invoice, = sale.invoices
    #? Surprised Tryton doesnt do this
    invoice.description =  uDescription
    # not idempotent
    Invoice.post([invoice.id], current_config.context)
    invoice.reload()
    assert invoice.state == u'posted'

