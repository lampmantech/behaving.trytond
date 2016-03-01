# -*- mode: python; py-indent-offset: 4; coding: utf-8-unix; encoding: utf-8 -*-
"""


"""
from __future__ import print_function

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
    r"""
    Given \
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
    purchase, = Purchase.find([('description', '=', uDescription),
                               ('company.id',  '=', company.id),
                               ('party.id', '=', supplier.id)])


@step('Purchase on date "{uDate}" with description "{uDescription}" with their reference "{uRef}" as user named "{uUser}" in Currency coded "{uCur}" ProductTemplates from supplier "{uSupplier}" with PaymentTerm "{uTerm}" and InvoiceMethod "{uMethod}" with |name|quantity|line_description| fields')
def step_impl(context, uDate, uDescription, uRef, uUser, uCur, uSupplier, uTerm, uMethod):
    r"""
    Purchase on date "TODAY" with description "Description" \
    with their reference "{uRef}" \
    as user named "Purchase" in Currency coded "{uCur}"  \
    ProductTemplates from supplier "Supplier" \
    with PaymentTerm "Direct" and InvoiceMethod "order" \
    with |name|quantity|line_description| fields

    If the quantity is the word comment, the line type is set to comment.
    with |name|quantity|description| fields
      | name    | quantity | line_description |
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

    if not Purchase.find([('description', '=', uDescription),
                          ('company.id',  '=', company.id),
                          ('party.id', '=', supplier.id)]):
        purchase = Purchase()
        purchase.party = supplier
        
        PaymentTerm = proteus.Model.get('account.invoice.payment_term')
        payment_term, = PaymentTerm.find([('name', '=', uTerm)])
        purchase.payment_term = payment_term
        purchase.invoice_method = uMethod
        purchase.description = uDescription
        Currency = proteus.Model.get('currency.currency')
        oCurrency, = Currency.find([('code', '=', uCur)])
        purchase.currency = oCurrency
        purchase.supplier_reference = uRef
        if uDate.lower() == 'today' or uDate.lower() == 'now':
            oDate = TODAY
        else:
            oDate = datetime.date(*map(int, uDate.split('-')))
        purchase.purchase_date = oDate
        # purchases also have warehouse
        #? purchase.save()

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
                # type == 'line' float?!
                purchase_line.quantity = Decimal(row['quantity'])
            if row['line_description']:
                purchase_line.description = row['line_description']
            #? purchase_line.save()
        purchase.save()

    user, = User.find([('login', '=', 'admin')])
    proteus.config.user = user.id

    purchase, = Purchase.find([('description', '=', uDescription),
                               ('company.id',  '=', company.id),
                               ('party.id', '=', supplier.id)])


@step('Purchase "{uAct}" on date "{uDate}" the P. O. with description "{uDescription}" as user named "{uUser}" products from supplier "{uSupplier}"')
def step_impl(context, uAct, uDate, uDescription, uUser, uSupplier):
    r"""
    Given \
    Purchase "quote" on date "TODAY" the P. O. with description "P. O No.1"
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

    if uUser != u'Administrator':
        purchase_user, = User.find([('name', '=', uUser)])
        proteus.config.user = purchase_user.id
    if uAct == 'quote':
        Purchase.quote([purchase.id], config.context)
        # FixMe: 3.4ism
        assert purchase.state in [ u'quotation', u'processing', u'done']
    elif uAct == 'confirm':
        Purchase.confirm([purchase.id], config.context)
        assert purchase.state in [u'confirmed', u'processing', u'done']
        # this will help us find the invoice later
        if purchase.invoices:
            invoice, = purchase.invoices
            assert invoice.origins == purchase.rec_name
            if not invoice.description:
                invoice.description = purchase.description
                invoice.save()
    elif uAct == 'process':
        purchase.click(uAct)
        assert purchase.state in [u'processing', u'done']
    else:
        raise ValueError("uAct must be one of quote or confirm or process: " + uAct)
    purchase.reload()
    
    if uUser != u'Administrator':
        user, = User.find([('login', '=', 'admin')])
        proteus.config.user = user.id

@step('Invoice "{uAct}" on date "{uDate}" the P. O. with description "{uDescription}" as user named "{uUser}" products from supplier "{uSupplier}"')
def step_impl(context, uAct, uDate, uDescription, uUser, uSupplier):
    r"""
    Given \
    Invoice "post" on date "TODAY" the P. O. with description "P. O No.1"
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
    lPurchaseInvoices = purchase.invoices
    assert lPurchaseInvoices
    invoice = Invoice(lPurchaseInvoices[0].id)
    oDate = oDateFromUDate(uDate)
    invoice.invoice_date = oDate
    invoice.accounting_date = oDate
    #? Surprised Tryton doesnt do this
    invoice.description = uDescription
    invoice.save()
    print('INFO: trytond_purchase,' +uDate +" "+ uDescription +" "+ invoice.type)
    if uAct == u'post':
        invoice.click('post')
    else:
        raise ValueError("uAct must be one of post: " + uAct)
    invoice.reload()

    user, = User.find([('login', '=', 'admin')])
    proteus.config.user = user.id

@step('Validate shipments on "{uDate}" for P. O. with description "{uDescription}" as user named "{uUser}" for products from supplier "{uSupplier}"')
def step_impl(context, uDate, uDescription, uUser, uSupplier):
    r"""
   Validate shipments on "TODAY" for P. O. with description "Description" \
   as user named "Administrator" for products from supplier "Supplier"
   """
    config = context.oProteusConfig

    ShipmentIn = proteus.Model.get('stock.shipment.in')

    Party = proteus.Model.get('party.party')
    sCompanyName = sGetFeatureData(context, 'party,company_name')
    party, = Party.find([('name', '=', sCompanyName)])
    Company = proteus.Model.get('company.company')
    company, = Company.find([('party.id', '=', party.id)])

    supplier, = Party.find([('name', '=', uSupplier),])
    Purchase = proteus.Model.get('purchase.purchase')
    #FixMe: Use the dates in to identify the purchase
    purchase, = Purchase.find([('party.id',  '=', supplier.id),
                               ('company.id',  '=', company.id),
                               ('description', '=', uDescription)])

    User = proteus.Model.get('res.user')
    stock_user, = User.find([('name', '=', uUser)])
    proteus.config.user = stock_user.id

    Move = proteus.Model.get('stock.move')
    shipment = ShipmentIn()
    shipment.supplier = supplier
    if hasattr(shipment, 'warehouse'):
        shipment.warehouse = purchase.warehouse
    oDate = oDateFromUDate(uDate)
    #? if purchase.purchase_date: oDate = purchase.purchase_date
    shipment.effective_date = oDate
    #? and not shipment.planned_date
    shipment.planned_date = oDate
    for move in purchase.moves:
        incoming_move = Move(id=move.id)
        incoming_move.supplier = supplier
        #? reference
        shipment.incoming_moves.append(incoming_move)
    shipment.save()

    assert shipment.origins == purchase.rec_name
    ShipmentIn.receive([shipment.id], config.context)
    ShipmentIn.done([shipment.id], config.context)
    purchase.reload()

    assert len(purchase.shipments) >= 1
    assert len(purchase.shipment_returns) == 0

# split to be isomorphic with sale -
# unfinished, untested
@step('Create a Purchase order with description "{uDescription}" in Currency coded "{uCur}" from supplier "{uSupplier}" on Date "{uDate}" with |name|value| fields')
def step_impl(context, uDescription, uCur, uSupplier, uDate):
    r"""
    Create a Purchase order with description "{uDescription}" \
    in Currency coded "%(sCur)s" from supplier "{uSupplier}" \
    on Date "{uDate}" with |name|value| fields
	  | name              | value    |
	  | invoice_method    | order    |
	  | payment_term      | Direct   |
	  | reference         | TheirRef |
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
    if not Purchase.find([('description', '=', uDescription),
                          ('company', '=', company.id),
                          ('party.id', '=', supplier.id)]):
        purchase = Purchase()
        purchase.party = supplier
        purchase.description = uDescription
        Currency = proteus.Model.get('currency.currency')
        oCurrency, = Currency.find([('code', '=', uCur)])
        purchase.currency = oCurrency
        if uDate.lower() == 'today' or uDate.lower() == 'now':
            oDate = TODAY
        else:
            oDate = datetime.date(*map(int, uDate.split('-')))
        purchase.purchase_date = oDate

        # 'payment_term', 'invoice_method'
        for row in context.table:
            setattr(purchase, row['name'],
                    string_to_python(row['name'], row['value'], Purchase))
        purchase.save()

    oPurchase, = Purchase.find([('description', '=', uDescription),
                                ('company', '=', company.id),
                                ('party.id', '=', supplier.id)])


# unfinished, untested
@step('Buy Products on the P. O. with description "{uDescription}" from supplier "{uSupplier}" with |description|quantity|unit_price| fields')
def step_impl(context, uDescription, uSupplier):
    r"""
    Buy Products on the P. O. with description "uDescription" \
    from supplier "uSupplier" with quantities
	  | description     | quantity | unit_price |
	  | Product Fixed   | 2.0      | 10.00      |
	  | Product Average | 3.0      | 10.00      |

    Idempotent.
    """
    current_config = context.oProteusConfig
    oPurchase = oBuyProductsPurchaseOrder(context, uDescription, uSupplier)
    sModel = 'purchase.purchase'

    Klass = proteus.Model.get(sModel)
    Klass.quote([oPurchase.id], current_config.context)
    Klass.confirm([oPurchase.id], current_config.context)
    Klass.process([oPurchase.id], current_config.context)

    assert oPurchase.state == u'processing'

# unfinished, untested
@step('Buy Products on the P. O. with description "{uDescription}" from supplier "{uSupplier}" with |description|quantity| fields')
def step_impl(context, uDescription, uSupplier):
    r"""
    Given \
    Buy products on the P. O. with description "uDescription" \
    from supplier "uSupplier" with quantities
	  | description     | quantity |
	  | Product Fixed   | 2.0      |
	  | Product Average | 3.0      |

    Idempotent.
    """
    current_config = context.oProteusConfig
    oPurchase = oBuyProductsPurchaseOrder(context, uDescription, uSupplier)
    sModel = 'purchase.purchase'
    Klass = proteus.Model.get(sModel)
    Klass.quote([oPurchase.id], current_config.context)
    Klass.confirm([oPurchase.id], current_config.context)
    Klass.process([oPurchase.id], current_config.context)

    assert oPurchase.state == u'processing'

def oBuyProductsPurchaseOrder(context, uDescription, uSupplier):
    current_config = context.oProteusConfig
    Purchase = proteus.Model.get('purchase.purchase')

    Party = proteus.Model.get('party.party')
    supplier, = Party.find([('name', '=', uSupplier)])
    sCompanyName = sGetFeatureData(context, 'party,company_name')
    party, = Party.find([('name', '=', sCompanyName)])
    Company = proteus.Model.get('company.company')
    company, = Company.find([('party.id', '=', party.id)])

    purchase, = Purchase.find([('description', '=', uDescription),
                               ('company', '=', company.id),
                               ('party.id', '=', supplier.id)])
    if len(purchase.lines) <= 0:
        PurchaseLine = proteus.Model.get('purchase.line')

        Product = proteus.Model.get('product.product')
        for row in context.table:
            uDescription = row['description']
            # float ?!
            mKg = Decimal(row['quantity'])
            # allow 0 (<0.0001) quantity - just skip them
            if mKg < Decimal(0.0001): continue
            product = Product.find([('description', '=', uDescription)])[0]

            purchase_line = PurchaseLine()
            purchase.lines.append(purchase_line)
            purchase_line.product = product
            purchase_line.quantity = mKg
            purchase_line.description = uDescription
            if u'unit_price' in context.table.headings:
                purchase_line.unit_price = Decimal(row['unit_price'])

        purchase.save()
    return purchase

