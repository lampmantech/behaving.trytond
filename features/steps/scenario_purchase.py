# -*- mode: python; py-indent-offset: 4; coding: utf-8-unix; encoding: utf-8 -*-

"""
=================
Purchase Scenario
=================

Unfinished
"""

from behave import *
import proteus

import datetime
from dateutil.relativedelta import relativedelta
from decimal import Decimal
from operator import attrgetter

from .support.fields import string_to_python, sGetFeatureData, vSetFeatureData
from .support import stepfuns

TODAY = datetime.date.today()

@step('T/PUR Create ProductTemplate')
def step_impl(context):
    """
    Create a ProductTemplate named "product" from a ProductCategory named "Category" with |name|value| fields
	  | name              | value |
	  | type	      | goods |
	  | cost_price_method | fixed |
          | default_uom       | Unit  |
	  | purchasable       | True  |
	  | salable 	      | True  |
	  | list_price 	      | 10    |
	  | cost_price 	      | 5     |
	  | delivery_time     | 0     |
	  | default_uom	      | Unit  |
	  | account_expense   | Main Expense |
	  | account_revenue   | Main Revenue |
    """
    config = context.oProteusConfig

    Party = proteus.Model.get('party.party')
    sCompanyName = sGetFeatureData(context, 'party,company_name')
    party, = Party.find([('name', '=', sCompanyName)])
    Company = proteus.Model.get('company.company')
    company, = Company.find([('party.id', '=', party.id)])

    payable, receivable, = stepfuns.gGetFeaturesPayRec(context, company)
    revenue, expense, = stepfuns.gGetFeaturesRevExp(context, company)
    
    Account = proteus.Model.get('account.account')
    
    ProductTemplate = proteus.Model.get('product.template')
    template = ProductTemplate()
    uName = 'product'
    if not ProductTemplate.find([('name','=', uName)]):
        ProductUom = proteus.Model.get('product.uom')
        unit, = ProductUom.find([('name', '=', 'Unit')])
        
        template = ProductTemplate()
        template.name = uName
        template.default_uom = unit
        template.type = 'goods'
        template.purchasable = True
        template.salable = True
        template.list_price = Decimal('10')
        template.cost_price = Decimal('5')
        template.cost_price_method = 'fixed'
        template.account_expense = expense
        template.account_revenue = revenue
        template.save()
    template, = ProductTemplate.find([('name','=', uName)])
    

@step('T/PUR Purchase Scenario')
def step_impl(context):
    config = context.oProteusConfig

    Party = proteus.Model.get('party.party')
    sCompanyName = sGetFeatureData(context, 'party,company_name')
    party, = Party.find([('name', '=', sCompanyName)])
    Company = proteus.Model.get('company.company')
    company, = Company.find([('party.id', '=', party.id)])

    User = proteus.Model.get('res.user')
    Group = proteus.Model.get('res.group')

#@step('T/PUR Create chart of accounts')
#def step_impl(context):

    AccountTemplate = proteus.Model.get('account.account.template')
    Account = proteus.Model.get('account.account')
    Journal = proteus.Model.get('account.journal')
    

#@step('T/PUR Create product')
#def step_impl(context):
    payable, receivable, = stepfuns.gGetFeaturesPayRec(context, company)
    revenue, expense, = stepfuns.gGetFeaturesRevExp(context, company)

    ProductUom = proteus.Model.get('product.uom')
    unit, = ProductUom.find([('name', '=', 'Unit')])
    ProductTemplate = proteus.Model.get('product.template')
    Product = proteus.Model.get('product.product')
    
    product = Product()
    uName = 'product'
    template, = ProductTemplate.find([('name','=', uName)])
    product.template = template
    product.save()    

    service = Product()
    uName = 'service'
    l = ProductTemplate.find([('name','=', uName)])
    if l:
        template = l[0]
    else:
        template = ProductTemplate()
        template.name = 'service'
        template.default_uom = unit
        template.type = 'service'
        template.purchasable = True
        template.list_price = Decimal('10')
        template.cost_price = Decimal('10')
        template.cost_price_method = 'fixed'
        template.account_expense = expense
        template.account_revenue = revenue
        template.save()
    service.template = template
    service.save()

#@step('T/PUR Create payment term')
#def step_impl(context):

    PaymentTerm = proteus.Model.get('account.invoice.payment_term')
    l = PaymentTerm.find([('name', '=', 'Direct')])
    if l:
        payment_term = l[0]
    else:
        PaymentTermLine = proteus.Model.get('account.invoice.payment_term.line')
        payment_term = PaymentTerm(name='Direct')
        payment_term_line = PaymentTermLine(type='remainder', days=0)
        payment_term.lines.append(payment_term_line)
        payment_term.save()

#@step('T/PUR Create an Inventory')
#def step_impl(context):

    stock_user, = User.find([('name', '=', 'Stock')])
    proteus.config.user = stock_user.id
    Inventory = proteus.Model.get('stock.inventory')
    Location = proteus.Model.get('stock.location')
    storage, = Location.find([
                ('code', '=', 'STO'),
                ])
    inventory = Inventory()
    inventory.location = storage
    inventory.save()
    
    InventoryLine = proteus.Model.get('stock.inventory.line')
    inventory_line = InventoryLine(product=product, inventory=inventory)
    inventory_line.quantity = 100.0
    inventory_line.expected_quantity = 0.0
    inventory.save()
    inventory_line.save()
    Inventory.confirm([inventory.id], config.context)
    assert inventory.state == u'done'

#@step('T/PUR Purchase 5 products')
#def step_impl(context):
    uSupplier = u'Supplier'
    supplier, = Party.find([('name', '=', uSupplier),])

    purchase_user, = User.find([('name', '=', 'Purchase')])
    proteus.config.user = purchase_user.id
    Purchase = proteus.Model.get('purchase.purchase')
    PurchaseLine = proteus.Model.get('purchase.line')
    purchase = Purchase()
    purchase.party = supplier
    purchase.payment_term = payment_term
    purchase.invoice_method = 'order'
    purchase_line = PurchaseLine()
    purchase.lines.append(purchase_line)
    purchase_line.product = product
    purchase_line.quantity = 2.0
    purchase_line = PurchaseLine()
    purchase.lines.append(purchase_line)
    purchase_line.type = 'comment'
    purchase_line.description = 'Comment'
    purchase_line = PurchaseLine()
    purchase.lines.append(purchase_line)
    purchase_line.product = product
    purchase_line.quantity = 3.0
    purchase.save()
    Purchase.quote([purchase.id], config.context)
    Purchase.confirm([purchase.id], config.context)
    assert purchase.state == u'confirmed'
    purchase.reload()
    assert len(purchase.moves) == 2
    assert len(purchase.shipment_returns) == 0
    assert len(purchase.invoices) == 1
    invoice, = purchase.invoices
    assert invoice.origins == purchase.rec_name

#@step('T/PUR Invoice line must be linked to stock move')
#def step_impl(context):

    _, invoice_line1, invoice_line2 = sorted(invoice.lines,
            key=lambda l: l.quantity)
    stock_move1, stock_move2 = sorted(purchase.moves,
            key=lambda m: m.quantity)
    assert invoice_line1.stock_moves == [stock_move1]
    assert stock_move1.invoice_lines == [invoice_line1]
    assert invoice_line2.stock_moves == [stock_move2]
    assert stock_move2.invoice_lines == [invoice_line2]

#@step('T/PUR Post invoice and check no new invoices')
#def step_impl(context):

    account_user, = User.find([('name', '=', 'Account')])
    proteus.config.user = account_user.id
    Invoice = proteus.Model.get('account.invoice')
    invoice = Invoice(purchase.invoices[0].id)
    invoice.invoice_date = TODAY
    invoice.click('post')
    
    purchase_user, = User.find([('name', '=', 'Purchase')])
    proteus.config.user = purchase_user.id
    purchase.reload()
    assert len(purchase.moves) == 2
    assert len(purchase.shipment_returns) == 0
    assert len(purchase.invoices) == 1

#@step('T/PUR Purchase 5 products with an invoice method 'on shipment'')
#def step_impl(context):

    purchase_user, = User.find([('name', '=', 'Purchase')])
    proteus.config.user = purchase_user.id
    purchase = Purchase()
    purchase.party = supplier
    purchase.payment_term = payment_term
    purchase.invoice_method = 'shipment'
    purchase_line = PurchaseLine()
    purchase.lines.append(purchase_line)
    purchase_line.product = product
    purchase_line.quantity = 2.0
    purchase_line = PurchaseLine()
    purchase.lines.append(purchase_line)
    purchase_line.type = 'comment'
    purchase_line.description = 'Comment'
    purchase_line = PurchaseLine()
    purchase.lines.append(purchase_line)
    purchase_line.product = product
    purchase_line.quantity = 3.0
    purchase.save()
    Purchase.quote([purchase.id], config.context)
    Purchase.confirm([purchase.id], config.context)
    assert purchase.state == u'confirmed'
    purchase.reload()
    
    assert len(purchase.moves) == 2
    assert len(purchase.shipment_returns) == 0
    assert len(purchase.invoices) == 0

#@step('T/PUR Not yet linked to invoice lines')
#def step_impl(context):

    stock_move1, stock_move2 = sorted(purchase.moves,
            key=lambda m: m.quantity)
    assert len(stock_move1.invoice_lines) == 0
    assert len(stock_move2.invoice_lines) == 0

#@step('T/PUR Validate Shipments')
#def step_impl(context):

    stock_user, = User.find([('name', '=', 'Stock')])
    proteus.config.user = stock_user.id
    Move = proteus.Model.get('stock.move')
    ShipmentIn = proteus.Model.get('stock.shipment.in')
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
    assert len(purchase.shipments) == 1
    assert len(purchase.shipment_returns) == 0

#@step('T/PUR Open supplier invoice')
#def step_impl(context):

    purchase_user, = User.find([('name', '=', 'Purchase')])
    proteus.config.user = purchase_user.id
    invoice, = purchase.invoices
    account_user, = User.find([('name', '=', 'Account')])
    proteus.config.user = account_user.id
    invoice = Invoice(invoice.id)
    assert invoice.type == u'in_invoice'
    invoice_line1, invoice_line2 = sorted(invoice.lines,
                                          key=lambda l: l.quantity)
    for line in invoice.lines:
        line.quantity = 1
        line.save()
    invoice.invoice_date = TODAY
    invoice.save()
    Invoice.post([invoice.id], config.context)

#@step('T/PUR Invoice lines must be linked to each stock moves')
#def step_impl(context):

    assert invoice_line1.stock_moves == [stock_move1]
    assert invoice_line2.stock_moves == [stock_move2]

#@step('T/PUR Check second invoices')
#def step_impl(context):

    purchase_user, = User.find([('name', '=', 'Purchase')])
    proteus.config.user = purchase_user.id
    purchase.reload()
    assert len(purchase.invoices) == 2
    assert sum(l.quantity for i in purchase.invoices for l in i.lines) == 5.0

#@step('T/PUR Create a Return')
#def step_impl(context):

    purchase_user, = User.find([('name', '=', 'Purchase')])
    proteus.config.user = purchase_user.id
    return_ = Purchase()
    return_.party = supplier
    return_.payment_term = payment_term
    return_.invoice_method = 'shipment'
    return_line = PurchaseLine()
    return_.lines.append(return_line)
    return_line.product = product
    return_line.quantity = -4.
    return_line = PurchaseLine()
    return_.lines.append(return_line)
    return_line.type = 'comment'
    return_line.description = 'Comment'
    return_.save()
    Purchase.quote([return_.id], config.context)
    Purchase.confirm([return_.id], config.context)
    assert return_.state == u'confirmed'
    return_.reload()
    assert len(return_.shipments) == 0
    assert len(return_.shipment_returns) == 1
    assert len(return_.invoices) == 0

#@step('T/PUR Check Return Shipments')
#def step_impl(context):

    stock_user, = User.find([('name', '=', 'Stock')])
    proteus.config.user = stock_user.id
    ShipmentReturn = proteus.Model.get('stock.shipment.in.return')
    ship_return, = return_.shipment_returns
    assert ship_return.state == u'waiting'
    move_return, = ship_return.moves
    assert move_return.product.rec_name == u'product'
    assert move_return.quantity == 4.0
    assert ShipmentReturn.assign_try([ship_return.id], config.context)
    ShipmentReturn.done([ship_return.id], config.context)
    ship_return.reload()
    assert ship_return.state == u'done'
    return_.reload()

#@step('T/PUR Open supplier credit note')
#def step_impl(context):

    purchase_user, = User.find([('name', '=', 'Purchase')])
    proteus.config.user = purchase_user.id
    credit_note, = return_.invoices
    account_user, = User.find([('name', '=', 'Account')])
    proteus.config.user = account_user.id
    credit_note = Invoice(credit_note.id)
    assert credit_note.type == u'in_credit_note'
    assert len(credit_note.lines) == 1
    assert sum(l.quantity for l in credit_note.lines) == 4.0
    credit_note.invoice_date = TODAY
    credit_note.save()
    Invoice.post([credit_note.id], config.context)

#@step('T/PUR Mixing return and purchase')
#def step_impl(context):

    purchase_user, = User.find([('name', '=', 'Purchase')])
    proteus.config.user = purchase_user.id
    mix = Purchase()
    mix.party = supplier
    mix.payment_term = payment_term
    mix.invoice_method = 'order'
    mixline = PurchaseLine()
    mix.lines.append(mixline)
    mixline.product = product
    mixline.quantity = 7.
    mixline_comment = PurchaseLine()
    mix.lines.append(mixline_comment)
    mixline_comment.type = 'comment'
    mixline_comment.description = 'Comment'
    mixline2 = PurchaseLine()
    mix.lines.append(mixline2)
    mixline2.product = product
    mixline2.quantity = -2.
    mix.save()
    Purchase.quote([mix.id], config.context)
    Purchase.confirm([mix.id], config.context)
    assert mix.state == u'confirmed'
    mix.reload()
    assert len(mix.moves) == 2
    assert len(mix.shipment_returns) == 1
    assert len(mix.invoices) == 2

#@step('T/PUR Checking Shipments')
#def step_impl(context):

    mix_returns, = mix.shipment_returns
    stock_user, = User.find([('name', '=', 'Stock')])
    proteus.config.user = stock_user.id
    mix_shipments = ShipmentIn()
    mix_shipments.supplier = supplier
    for move in mix.moves:
        if move.id in [m.id for m in mix_returns.moves]:
            continue
        incoming_move = Move(id=move.id)
        mix_shipments.incoming_moves.append(incoming_move)
    mix_shipments.save()
    ShipmentIn.receive([mix_shipments.id], config.context)
    ShipmentIn.done([mix_shipments.id], config.context)
    mix.reload()
    assert len(mix.shipments) == 1

    ShipmentReturn.wait([mix_returns.id], config.context)
    assert ShipmentReturn.assign_try([mix_returns.id], config.context)
    ShipmentReturn.done([mix_returns.id], config.context)
    move_return, = mix_returns.moves
    assert move_return.product.rec_name == u'product'
    assert move_return.quantity == 2.0

#@step('T/PUR Checking the invoice')
#def step_impl(context):

    purchase_user, = User.find([('name', '=', 'Purchase')])
    proteus.config.user = purchase_user.id
    mix.reload()
    mix_invoice, mix_credit_note = sorted(mix.invoices,
            key=attrgetter('type'), reverse=True)
    account_user, = User.find([('name', '=', 'Account')])
    proteus.config.user = account_user.id
    mix_invoice = Invoice(mix_invoice.id)
    mix_credit_note = Invoice(mix_credit_note.id)
    assert mix_invoice.type, mix_credit_note.type == \
        (u'in_invoice', u'in_credit_note')
    assert len(mix_invoice.lines), len(mix_credit_note.lines) == \
        (1, 1)
    assert sum(l.quantity for l in mix_invoice.lines) == 7.0
    assert sum(l.quantity for l in mix_credit_note.lines) == 2.0
    
    mix_invoice.invoice_date = TODAY
    mix_invoice.save()
    Invoice.post([mix_invoice.id], config.context)
    mix_credit_note.invoice_date = TODAY
    mix_credit_note.save()
    Invoice.post([mix_credit_note.id], config.context)

#@step('T/PUR Mixing stuff with an invoice method 'on shipment'')
#def step_impl(context):

    purchase_user, = User.find([('name', '=', 'Purchase')])
    proteus.config.user = purchase_user.id
    mix = Purchase()
    mix.party = supplier
    mix.payment_term = payment_term
    mix.invoice_method = 'shipment'
    
    mixline = PurchaseLine()
    mix.lines.append(mixline)
    mixline.product = product
    mixline.quantity = 6.
    mixline_comment = PurchaseLine()
    mix.lines.append(mixline_comment)
    mixline_comment.type = 'comment'
    mixline_comment.description = 'Comment'
    mixline2 = PurchaseLine()
    mix.lines.append(mixline2)
    mixline2.product = product
    mixline2.quantity = -3.
    mix.save()
    Purchase.quote([mix.id], config.context)
    Purchase.confirm([mix.id], config.context)
    assert mix.state == u'confirmed'
    mix.reload()
    assert len(mix.moves) == 2
    assert len(mix.shipment_returns) == 1
    assert len(mix.invoices) == 0
    
#@step('T/PUR Checking Shipments')
#def step_impl(context):

    stock_user, = User.find([('name', '=', 'Stock')])
    proteus.config.user = stock_user.id
    mix_returns, = mix.shipment_returns
    mix_shipments = ShipmentIn()
    mix_shipments.supplier = supplier
    for move in mix.moves:
        if move.id in [m.id for m in mix_returns.moves]:
            continue
        incoming_move = Move(id=move.id)
        mix_shipments.incoming_moves.append(incoming_move)
    mix_shipments.save()
    ShipmentIn.receive([mix_shipments.id], config.context)
    ShipmentIn.done([mix_shipments.id], config.context)
    mix.reload()
    assert len(mix.shipments) == 1

    ShipmentReturn.wait([mix_returns.id], config.context)
    assert ShipmentReturn.assign_try([mix_returns.id], config.context)
    ShipmentReturn.done([mix_returns.id], config.context)
    move_return, = mix_returns.moves
    assert move_return.product.rec_name == u'product'
    assert move_return.quantity == 3.0

#@step('T/PUR Purchase services')
#def step_impl(context):

    purchase_user, = User.find([('name', '=', 'Purchase')])
    proteus.config.user = purchase_user.id
    service_purchase = Purchase()
    service_purchase.party = supplier
    service_purchase.payment_term = payment_term
    purchase_line = service_purchase.lines.new()
    purchase_line.product = service
    purchase_line.quantity = 1
    service_purchase.save()
    service_purchase.click('quote')
    service_purchase.click('confirm')
    assert service_purchase.state == u'confirmed'
    service_invoice, = service_purchase.invoices

#@step('T/PUR Pay the service invoice')
#def step_impl(context):
    cash_journal, = Journal.find([('type', '=', 'cash')])
    Journal = proteus.Model.get('account.journal')

    account_user, = User.find([('name', '=', 'Account')])
    proteus.config.user = account_user.id
    service_invoice.invoice_date = TODAY
    service_invoice.click('post')
    pay = proteus.Wizard('account.invoice.pay', [service_invoice])
    pay.form.journal = cash_journal
    pay.form.amount = service_invoice.total_amount
    pay.execute('choice')
    service_invoice.reload()
    assert service_invoice.state == u'paid'

#@step('T/PUR Check service purchase states')
#def step_impl(context):

    proteus.config.user = purchase_user.id
    service_purchase.reload()
    assert service_purchase.invoice_state == u'paid'
    assert service_purchase.shipment_state == u'none'
    assert service_purchase.state == u'done'
