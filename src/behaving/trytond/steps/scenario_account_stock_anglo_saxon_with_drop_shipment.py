# -*- mode: python; py-indent-offset: 4; coding: utf-8-unix; encoding: utf-8 -*-

"""
=====================================================
Account Stock Anglo-Saxon with Drop Shipment Scenario
=====================================================

Unfinished
"""

from behave import *
import proteus

import datetime
from dateutil.relativedelta import relativedelta
from decimal import Decimal

from .support.fields import string_to_python, sGetFeatureData, vSetFeatureData
from .support import stepfuns

TODAY = datetime.date.today()

# unused
# product, Supplier
@step('Create a ProductSupplier with description "{uDescription}" from a ProductTemplate named "{uTemplateName}" with supplier named "{uSupplier}" with |name|value| fields')
def step_impl(context, uDescription, uTemplateName, uSupplier):
    """
    Given \
    Create a ProductSupplier from a Template named "product" \
    with a supplier named "Supplier" \
    with |name|value| fields such as:
      drop_shipment
    E. g.
	  | name              | value   |
	  | drop_shipment     | True    |
          | delivery_time     | 0       |
    Idempotent.
    """
    ProductSupplier = proteus.Model.get('purchase.product_supplier')

    Party = proteus.Model.get('party.party')
    supplier, = Party.find([('name', '=', uSupplier),])

    ProductTemplate = proteus.Model.get('product.template')
    template, = ProductTemplate.find([('name', '=', uTemplateName)])
    if not ProductSupplier.find([('product.name', '=', uTemplateName),
                                 ('party.id', '=', supplier.id)]):
        product_supplier = ProductSupplier()
        product_supplier.product = template
        product_supplier.party = supplier
        for row in context.table:
            setattr(template, row['name'],
                    string_to_python(row['name'], row['value'],
                                     ProductSupplier))
        product_supplier.save()

    assert ProductSupplier.find([('product.name', '=', uTemplateName),
                                     ('party.id', '=', supplier.id)])


def product_supplier():
    if True:
        product_supplier, = ProductSupplier.find([('product.name', '=', uName),
                                                  ('party.id', '=', supplier.id)])
    else:
        product_supplier = ProductSupplier()
        product_supplier.product = template
        product_supplier.party = supplier
        product_supplier.drop_shipment = True
        product_supplier.delivery_time = 0
        product_supplier.save()

@step('T/ASASDS Account Stock Anglo-Saxon with Drop Shipment Scenario')
def step_impl(context):

    config = context.oProteusConfig
    Party = proteus.Model.get('party.party')
    sCompanyName = sGetFeatureData(context, 'party,company_name')
    party, = Party.find([('name', '=', sCompanyName)])
    Company = proteus.Model.get('company.company')
    company, = Company.find([('party.id', '=', party.id)])

    User = proteus.Model.get('res.user')
    Group = proteus.Model.get('res.group')

    Account = proteus.Model.get('account.account')
    AccountJournal = proteus.Model.get('account.journal')

    # ProductSupplier = proteus.Model.get('purchase.product_supplier')

    payable, receivable, = stepfuns.gGetFeaturesPayRec(context, company)
    revenue, expense, = stepfuns.gGetFeaturesRevExp(context, company)

    # These are in by trytond_account_stock_continental/account.xml
    # which is pulled in by trytond_account_stock_anglo_saxon
    stock, stock_customer, stock_lost_found, stock_production, \
        stock_supplier, = stepfuns.gGetFeaturesStockAccs(context, company)

    uSupplier = u'Supplier'
    supplier, = Party.find([('name', '=', uSupplier),])

    ProductTemplate = proteus.Model.get('product.template')
    uName = 'Product Template'
    template, = ProductTemplate.find([('name','=', uName)])
    Product = proteus.Model.get('product.product')
    if True:
        product, = Product.find([('template.name','=', uName),
                                 ('description', '=', "T/ASASDS Product Description")])
    else:
        product = Product()
        product.template = template
        product.description = "T/ASASDS Product Description"
        product.save()

# Wierd: unused product_supplier but the code breaks if its not here
    ProductSupplier = proteus.Model.get('purchase.product_supplier')
    if True:
        product_supplier = ProductSupplier()
        product_supplier.product = template
        product_supplier.party = supplier
        product_supplier.drop_shipment = True
        product_supplier.delivery_time = 0
        product_supplier.save()

#@step('T/ASASDS Create payment term')
#def step_impl(context):


    PaymentTerm = proteus.Model.get('account.invoice.payment_term')
    if True:
        payment_term, = PaymentTerm.find([('name', '=', 'Direct')])
    else:
        payment_term = PaymentTerm(name='Direct')
        PaymentTermLine = proteus.Model.get('account.invoice.payment_term.line')
        payment_term = PaymentTerm(name='Direct')
        payment_term_line = PaymentTermLine(type='remainder', days=0)
        payment_term.lines.append(payment_term_line)
        payment_term.save()

#@step('T/ASASDS Sale 50 products')
#def step_impl(context):

    customer, = Party.find([('name', '=', 'Customer')])

    User = proteus.Model.get('res.user')
    sale_user, = User.find([('name', '=', 'Sale')])
    config.user = sale_user.id

    Sale = proteus.Model.get('sale.sale')
    SaleLine = proteus.Model.get('sale.line')
    sale = Sale()
    sale.description = 'T/ASASDS Sale 50 products'
    sale.party = customer
    sale.sale_date = TODAY
    sale.payment_term = payment_term
    sale_line = sale.lines.new()
    sale_line.product = product
    sale_line.quantity = 50
    sale.save()

    Sale.quote([sale.id], config.context)
    Sale.confirm([sale.id], config.context)
    Sale.process([sale.id], config.context)
    assert sale.state == u'processing'

#@step('T/ASASDS Create Purchase from Request')
#def step_impl(context):

    User = proteus.Model.get('res.user')
    sale_user, = User.find([('name', '=', 'Sale')])
    purchase_user, = User.find([('name', '=', 'Purchase')])

    config.user = purchase_user.id
    Purchase = proteus.Model.get('purchase.purchase')
    PurchaseRequest = proteus.Model.get('purchase.request')
    purchase_request, = PurchaseRequest.find()
    create_purchase = proteus.Wizard('purchase.request.create_purchase',
            [purchase_request])
    if hasattr(create_purchase.form, 'payment_term'):
        # gone in 3.6?
        create_purchase.form.payment_term = payment_term
    
    create_purchase.execute('start')

    purchase, = Purchase.find()
    purchase_line, = purchase.lines
    purchase_line.unit_price = Decimal('3')
    purchase.save()
    Purchase.quote([purchase.id], config.context)
    Purchase.confirm([purchase.id], config.context)
    purchase.reload()
    # Fixme: should be just == u'processing'
    assert purchase.state in [u'confirmed', u'processing']

    config.user = sale_user.id
    sale.reload()
    assert sale.shipments == []
    shipment, = sale.drop_shipments

#@step('T/ASASDS Receive 50 products')
#def step_impl(context):

    User = proteus.Model.get('res.user')
    stock_user, = User.find([('name', '=', 'Stock')])

    config.user = stock_user.id
    ShipmentDrop = proteus.Model.get('stock.shipment.drop')
    ShipmentDrop.done([shipment.id], config.context)
    assert shipment.state == u'done'

    stock_supplier.reload()
    assert stock_supplier.debit == Decimal('0.00')
    assert stock_supplier.credit == Decimal('150.00')

    stock_customer.reload()
    assert stock_customer.debit == Decimal('150.00')
    assert stock_customer.credit == Decimal('0.00')

    stock.reload()
    assert stock.debit == Decimal('0.00')
    assert stock.credit == Decimal('0.00')

#@step('T/ASASDS Open supplier invoice')
#def step_impl(context):

    User = proteus.Model.get('res.user')
    Invoice = proteus.Model.get('account.invoice')
    purchase_user, = User.find([('name', '=', 'Purchase')])

    payable, receivable, = stepfuns.gGetFeaturesPayRec(context, company)
    revenue, expense, = stepfuns.gGetFeaturesRevExp(context, company)

    config.user = purchase_user.id
    purchase.reload()
    invoice, = purchase.invoices

    account_user, = User.find([('name', '=', 'Account')])
    config.user = account_user.id
    invoice.invoice_date = TODAY
    #? this was missing
    invoice.accounting_date = invoice.invoice_date
    invoice.save()
    Invoice.post([invoice.id], config.context)
    assert invoice.state == u'posted'

    payable.reload()
    assert payable.debit == Decimal('0.00')
    assert payable.credit == Decimal('150.00')

    expense.reload()
    assert expense.debit == Decimal('150.00')
    assert expense.credit == Decimal('150.00')

    stock_supplier.reload()
    assert stock_supplier.debit == Decimal('150.00')
    assert stock_supplier.credit == Decimal('150.00')

#@step('T/ASASDS Post customer Invoice')
#def step_impl(context):

    User = proteus.Model.get('res.user')
    sale_user, = User.find([('name', '=', 'Sale')])
    config.user = sale_user.id
    sale.reload()
    invoice, = sale.invoices

    account_user, = User.find([('name', '=', 'Account')])
    config.user = account_user.id
    Invoice.post([invoice.id], config.context)
    assert invoice.state == u'posted'

    payable, receivable, = stepfuns.gGetFeaturesPayRec(context, company)
    receivable.reload()
    assert receivable.debit == Decimal('500.00')
    assert receivable.credit == Decimal('0.00')

    revenue, expense, = stepfuns.gGetFeaturesRevExp(context, company)
    revenue.reload()
    assert revenue.debit == Decimal('0.00')
    assert revenue.credit == Decimal('500.00')

    (stock, stock_customer, stock_lost_found, stock_production,
            stock_supplier) = Account.find([
                ('kind', '=', 'stock'),
                ('company', '=', company.id),
                ('name', 'like', 'Stock%'),
                ], order=[('name', 'ASC')])
    stock_customer.reload()
    assert stock_customer.debit == Decimal('150.00')
    assert stock_customer.credit == Decimal('150.00')

    Account = proteus.Model.get('account.account')
    cogs, = Account.find([
                ('kind', '=', 'other'),
                ('company', '=', company.id),
                ('name', '=', 'COGS'),
                ])
    cogs.reload()
    assert cogs.debit == Decimal('150.00')
    assert cogs.credit == Decimal('0.00')
