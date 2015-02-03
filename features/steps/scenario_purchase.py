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

#@step('T/PUR Create chart of accounts')
#def step_impl(context):

@step('T/PUR Assert the Purchase lines in the P.O. with description "{uDescription}" for products from supplier "{uSupplier}"')
def step_impl(context, uDescription, uSupplier):
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
    
    assert len(purchase.moves) == 2
    assert len(purchase.shipment_returns) == 0
    assert len(purchase.invoices) == 1
    invoice, = purchase.invoices
    assert invoice.origins == purchase.rec_name

@step('T/PUR Assert the Invoice lines are linked to stock move in the P.O. with description "{uDescription}" for products from supplier "{uSupplier}"')
def step_impl(context, uDescription, uSupplier):
    config = context.oProteusConfig
    
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
    
    invoice, = purchase.invoices
    _, invoice_line1, invoice_line2 = sorted(invoice.lines,
            key=lambda l: l.quantity)
    stock_move1, stock_move2 = sorted(purchase.moves,
            key=lambda m: m.quantity)
    assert invoice_line1.stock_moves == [stock_move1]
    assert stock_move1.invoice_lines == [invoice_line1]
    assert invoice_line2.stock_moves == [stock_move2]
    assert stock_move2.invoice_lines == [invoice_line2]

@step('T/PUR Check no new invoices in the P.O. with description "{uDescription}" for products from supplier "{uSupplier}"')
def step_impl(context, uDescription, uSupplier):
    config = context.oProteusConfig
    
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

#?    purchase_user, = User.find([('name', '=', 'Purchase')])
#?    proteus.config.user = purchase_user.id
    assert len(purchase.moves) == 2
    assert len(purchase.shipment_returns) == 0
    assert len(purchase.invoices) == 1

@step('T/PUR Assert not yet linked to invoice lines P.O. with description "{uDescription}" for products from supplier "{uSupplier}"')
def step_impl(context, uDescription, uSupplier):
    config = context.oProteusConfig
    
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

    stock_move1, stock_move2 = sorted(purchase.moves,
            key=lambda m: m.quantity)
    assert len(stock_move1.invoice_lines) == 0
    assert len(stock_move2.invoice_lines) == 0

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

    AccountTemplate = proteus.Model.get('account.account.template')
    Account = proteus.Model.get('account.account')
    Journal = proteus.Model.get('account.journal')

    payable, receivable, = stepfuns.gGetFeaturesPayRec(context, company)
    revenue, expense, = stepfuns.gGetFeaturesRevExp(context, company)

    Product = proteus.Model.get('product.product')
    product, = Product.find([('name','=', 'product')])
    service, = Product.find([('name','=', 'service')])

    uSupplier = u'Supplier'
    supplier, = Party.find([('name', '=', uSupplier),])

    Purchase = proteus.Model.get('purchase.purchase')
    purchase1, = Purchase.find([('party.id',  '=', supplier.id),
                               ('company.id',  '=', company.id),
                               ('description', '=', "P. O. #1")])

    Purchase = proteus.Model.get('purchase.purchase')
    purchase2, = Purchase.find([('party.id',  '=', supplier.id),
                               ('company.id',  '=', company.id),
                               ('description', '=', "P. O. #2")])
    purchase = purchase2

#@step('T/PUR Create an open supplier invoice')
#def step_impl(context):

    Invoice = proteus.Model.get('account.invoice')
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

    stock_move1, stock_move2 = sorted(purchase.moves,
            key=lambda m: m.quantity)
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

    PurchaseLine = proteus.Model.get('purchase.line')

    PaymentTerm = proteus.Model.get('account.invoice.payment_term')
    payment_term, = PaymentTerm.find([('name', '=', 'Direct')])
    
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

    ShipmentIn = proteus.Model.get('stock.shipment.in')
    Move = proteus.Model.get('stock.move')

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
