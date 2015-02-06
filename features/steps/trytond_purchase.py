# -*- mode: python; py-indent-offset: 4; coding: utf-8-unix; encoding: utf-8 -*-
"""


"""
from behave import *
import proteus

import datetime
from decimal import Decimal

from .support.fields import string_to_python, sGetFeatureData, vSetFeatureData
from .support import modules
from .support.tools import *
from .support.stepfuns import vAssertContentTable

TODAY = datetime.date.today()

@step('Create a Purchase Order with description "{uDescription}" from supplier "{uSupplier}" with fields')
def step_impl(context, uDescription, uSupplier):
    """
    Create a Purchase Order from a supplier with a description.
    It expects a |name|value| table; the fields typically include:
    'payment_term', 'invoice_method', 'purchase_date', 'currency'
	  | invoice_method    | shipment |
	  | payment_term      | Direct 	 |
	  | purchase_date     | TODAY	 |
	  | currency          | EUR	 |
    Idempotent.
    """
    current_config = context.oProteusConfig

    Purchase = proteus.Model.get('purchase.purchase')

    Party = proteus.Model.get('party.party')
    sCompanyName = sGetFeatureData(context, 'party,company_name')
    party, = Party.find([('name', '=', sCompanyName)])
    Company = proteus.Model.get('company.company')
    company, = Company.find([('party.id', '=', party.id)])
    supplier, = Party.find([('name', '=', uSupplier)])

    # comment currency warehouse
    if not Purchase.find([('description', '=', uDescription),
                          ('company.id',  '=', company.id),
                          ('party.id', '=', supplier.id)]):
        purchase = Purchase()
        purchase.party = supplier
        purchase.description = uDescription
        for row in context.table:
            if row['name'] == u'purchase_date':
                uDate = row['value']
                if uDate.lower() == 'today' or uDate.lower() == 'now':
                    oDate = TODAY
                else:
                    oDate = datetime.date(*map(int, uDate.split('-')))
                purchase.purchase_date = oDate
                continue
            setattr(purchase, row['name'],
                    string_to_python(row['name'], row['value'], Purchase))

        purchase.save()
    assert Purchase.find([('description', '=', uDescription),
                          ('company.id',  '=', company.id),
                          ('party.id', '=', supplier.id)])


@step('Purchase on date "{uDate}" with description "{uDescription}" as user named "{uUser}" ProductTemplates from supplier "{uSupplier}" with PaymentTerm "{uTerm}" and InvoiceMethod "{uMethod}" with |name|quantity|description| fields')
def step_impl(context, uDate, uDescription, uUser, uSupplier, uTerm, uMethod):
    """
    Purchase on date "TODAY" with description "Description"
    as user named "Purchase" ProductTemplates from supplier "Supplier" 
    with PaymentTerm "Direct" and InvoiceMethod "order"
    If the quantity is the word comment, the line type is set to comment.
    with |name|quantity|description| fields
      | name | quantity | line_description |
      | product | 2.0      |             |
      | product | comment  | Comment     |
      | product | 3.0      |             |
    """
    # shouls we make quantity == 'comment'
    config = context.oProteusConfig

    Purchase = proteus.Model.get('purchase.purchase')

    Party = proteus.Model.get('party.party')
    sCompanyName = sGetFeatureData(context, 'party,company_name')
    party, = Party.find([('name', '=', sCompanyName)])
    Company = proteus.Model.get('company.company')
    company, = Company.find([('party.id', '=', party.id)])
    
    Product = proteus.Model.get('product.product')
    supplier, = Party.find([('name', '=', uSupplier),])

    User = proteus.Model.get('res.user')
    purchase_user, = User.find([('name', '=', uUser)])
    proteus.config.user = purchase_user.id

    PaymentTerm = proteus.Model.get('account.invoice.payment_term')
    payment_term, = PaymentTerm.find([('name', '=', uTerm)])

    if not Purchase.find([('description', '=', uDescription),
                          ('company.id',  '=', company.id),
                          ('party.id', '=', supplier.id)]):
        purchase = Purchase()
        purchase.party = supplier
        purchase.payment_term = payment_term
        purchase.invoice_method = uMethod
        purchase.description = uDescription
        if uDate.lower() == 'today' or uDate.lower() == 'now':
            oDate = TODAY
        else:
            oDate = datetime.date(*map(int, uDate.split('-')))
        purchase.purchase_date = oDate
        # purchases also have warehouse, currency
        purchase.save()

        PurchaseLine = proteus.Model.get('purchase.line')
        for row in context.table:
            # BUG? Product.find([('name' should FAIL
            product, = Product.find([('name', '=', row['name'])])
            purchase_line = PurchaseLine()
            purchase.lines.append(purchase_line)
            purchase_line.product = product
            if row['quantity'] == 'comment':
                purchase_line.type = 'comment'
            else:
                # type == 'line'
                purchase_line.quantity = float(row['quantity'])
            if row['line_description']:
                purchase_line.description = row['line_description']
            #? why no purchase_line.save()
        purchase.save()
        
    user, = User.find([('login', '=', 'admin')])
    proteus.config.user = user.id
    
    assert Purchase.find([('description', '=', uDescription),
                          ('company.id',  '=', company.id),
                          ('party.id', '=', supplier.id)])

@step('Purchase on date "{uDate}" with description "{uDescription}" as user named "{uUser}" Products from supplier "{uSupplier}" with PaymentTerm "{uTerm}" and InvoiceMethod "{uMethod}" with |description|quantity|line_description| fields')
def step_impl(context, uDate, uDescription, uUser, uSupplier, uTerm, uMethod):
    """
    Purchase on date "TODAY" with description "Description"
    as user named "Purchase" Products from supplier "Supplier" 
    with PaymentTerm "Direct" and InvoiceMethod "order"
    If the quantity is the word comment, the line type is set to comment.
    with |description|quantity|line_description| fields
      | description | quantity | line_description |
      | product | 2.0      |             |
      | product | comment  | Comment     |
      | product | 3.0      |             |
    """
    # shouls we make quantity == 'comment'
    config = context.oProteusConfig

    Purchase = proteus.Model.get('purchase.purchase')

    Party = proteus.Model.get('party.party')
    sCompanyName = sGetFeatureData(context, 'party,company_name')
    party, = Party.find([('name', '=', sCompanyName)])
    Company = proteus.Model.get('company.company')
    company, = Company.find([('party.id', '=', party.id)])
    
    Product = proteus.Model.get('product.product')
    supplier, = Party.find([('name', '=', uSupplier),])

    User = proteus.Model.get('res.user')
    purchase_user, = User.find([('name', '=', uUser)])
    proteus.config.user = purchase_user.id

    PaymentTerm = proteus.Model.get('account.invoice.payment_term')
    payment_term, = PaymentTerm.find([('name', '=', uTerm)])

    if not Purchase.find([('description', '=', uDescription),
                          ('company.id',  '=', company.id),
                          ('party.id', '=', supplier.id)]):
        purchase = Purchase()
        purchase.party = supplier
        purchase.payment_term = payment_term
        purchase.invoice_method = uMethod
        purchase.description = uDescription
        if uDate.lower() == 'today' or uDate.lower() == 'now':
            oDate = TODAY
        else:
            oDate = datetime.date(*map(int, uDate.split('-')))
        purchase.purchase_date = oDate
        # purchases also have warehouse, currency
        purchase.save()

        PurchaseLine = proteus.Model.get('purchase.line')
        for row in context.table:
            # BUG? Product.find([('name' should FAIL
            product, = Product.find([('description', '=', row['description'])])
            purchase_line = PurchaseLine()
            purchase.lines.append(purchase_line)
            purchase_line.product = product
            if row['quantity'] == 'comment':
                purchase_line.type = 'comment'
            else:
                # type == 'line'
                purchase_line.quantity = float(row['quantity'])
            if row['line_description']:
                purchase_line.description = row['line_description']
            #? why no purchase_line.save()
        purchase.save()
        
    user, = User.find([('login', '=', 'admin')])
    proteus.config.user = user.id
    
    assert Purchase.find([('description', '=', uDescription),
                          ('company.id',  '=', company.id),
                          ('party.id', '=', supplier.id)])

@step('Purchase "{uAct}" on date "{uDate}" the P. O. with description "{uDescription}" as user named "{uUser}" products from supplier "{uSupplier}"')
def step_impl(context, uAct, uDate, uDescription, uUser, uSupplier):
    """
    Purchase "quote" on date "TODAY" the P. O. with description "P. O #1" 
    as user named "Purchase" products from supplier "Supplier"
    """
    config = context.oProteusConfig
    
    Party = proteus.Model.get('party.party')
    sCompanyName = sGetFeatureData(context, 'party,company_name')
    party, = Party.find([('name', '=', sCompanyName)])
    Company = proteus.Model.get('company.company')
    company, = Company.find([('party.id', '=', party.id)])

    User = proteus.Model.get('res.user')
    
    supplier, = Party.find([('name', '=', uSupplier),])
    Purchase = proteus.Model.get('purchase.purchase')
    purchase, = Purchase.find([('party.id',  '=', supplier.id),
                               ('company.id',  '=', company.id),
                               ('description', '=', uDescription)])

    purchase_user, = User.find([('name', '=', uUser)])
    proteus.config.user = purchase_user.id
    if uAct == 'quote':
        Purchase.quote([purchase.id], config.context)
        assert purchase.state == u'quotation'
    elif uAct == 'confirm':
        Purchase.confirm([purchase.id], config.context)
        assert purchase.state == u'confirmed'
    else:
        raise ValueError("uAct must be one of quote or confirm: " + uAct)
    purchase.reload()
    user, = User.find([('login', '=', 'admin')])
    proteus.config.user = user.id

@step('Invoice "{uAct}" on date "{uDate}" the P. O. with description "{uDescription}" as user named "{uUser}" products from supplier "{uSupplier}"')
def step_impl(context, uAct, uDate, uDescription, uUser, uSupplier):
    """
    Invoice "post" on date "TODAY" the P. O. with description "P. O #1" 
    as user named "Account" products from supplier "Supplier"
    """
    config = context.oProteusConfig
    
    Party = proteus.Model.get('party.party')
    sCompanyName = sGetFeatureData(context, 'party,company_name')
    party, = Party.find([('name', '=', sCompanyName)])
    Company = proteus.Model.get('company.company')
    company, = Company.find([('party.id', '=', party.id)])

    User = proteus.Model.get('res.user')
    
    supplier, = Party.find([('name', '=', uSupplier),])
    Purchase = proteus.Model.get('purchase.purchase')
    purchase, = Purchase.find([('party.id',  '=', supplier.id),
                               ('company.id',  '=', company.id),
                               ('description', '=', uDescription)])
    
    account_user, = User.find([('name', '=', uUser)])
    proteus.config.user = account_user.id
    Invoice = proteus.Model.get('account.invoice')
    invoice = Invoice(purchase.invoices[0].id)
    if uDate.lower() == 'today' or uDate.lower() == 'now':
        oDate = TODAY
    else:
        oDate = datetime.date(*map(int, uDate.split('-')))
    invoice.invoice_date = oDate
    #? Surprised Tryton doesnt do this
    invoice.description = uDescription
    if uAct == u'post':
        invoice.click('post')
    else:
        raise ValueError("uAct must be one of post: " + uAct)
    invoice.reload()
    
    user, = User.find([('login', '=', 'admin')])
    proteus.config.user = user.id

@step('Validate shipments for P. O. with description "{uDescription}" as user named "{uUser}" for products from supplier "{uSupplier}"')
def step_impl(context, uDescription, uUser, uSupplier):
    config = context.oProteusConfig
    
    ShipmentIn = proteus.Model.get('stock.shipment.in')

    Party = proteus.Model.get('party.party')
    sCompanyName = sGetFeatureData(context, 'party,company_name')
    party, = Party.find([('name', '=', sCompanyName)])
    Company = proteus.Model.get('company.company')
    company, = Company.find([('party.id', '=', party.id)])

    supplier, = Party.find([('name', '=', uSupplier),])
    Purchase = proteus.Model.get('purchase.purchase')
    purchase, = Purchase.find([('party.id',  '=', supplier.id),
                               ('company.id',  '=', company.id),
                               ('description', '=', uDescription)])

    User = proteus.Model.get('res.user')
    stock_user, = User.find([('name', '=', uUser)])
    proteus.config.user = stock_user.id
    
    Move = proteus.Model.get('stock.move')
    shipment = ShipmentIn()
    shipment.supplier = supplier
    for move in purchase.moves:
        incoming_move = Move(id=move.id)
        shipment.incoming_moves.append(incoming_move)
    shipment.save()
    
    assert shipment.origins == purchase.rec_name
    ShipmentIn.receive([shipment.id], config.context)
    ShipmentIn.done([shipment.id], config.context)
    purchase.reload()
    
    assert len(purchase.shipments) >= 1
    assert len(purchase.shipment_returns) == 0

