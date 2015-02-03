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

# FixMe: merge
@step('T/ASASDS Create ProductTemplate')
def step_impl(context):
    """
    Create a ProductTemplate named "{uName}" with stock accounts from features from a ProductCategory named "{uCatName}" with |name|value| fields
	  | name              | value |
	  | type	      | goods |
	  | cost_price_method | fixed  |
	  | purchasable       | True  |
	  | salable 	      | True  |
	  | list_price 	      | 10    |
	  | cost_price 	      | 5     |
	  | delivery_time     | 0     |
	  | default_uom	      | Unit  |
	  | account_expense   | Main Expense |
	  | account_revenue   | Main Revenue |
	  | account_cogs      | COGS |
          | supply_on_sale    | True |
    """

    config = context.oProteusConfig

    Party = proteus.Model.get('party.party')
    sCompanyName = sGetFeatureData(context, 'party,company_name')
    party, = Party.find([('name', '=', sCompanyName)])
    Company = proteus.Model.get('company.company')
    company, = Company.find([('party.id', '=', party.id)])

    Account = proteus.Model.get('account.account')

    payable, receivable, = stepfuns.gGetFeaturesPayRec(context, company)
    revenue, expense, = stepfuns.gGetFeaturesRevExp(context, company)

    # These are in by trytond_account_stock_continental/account.xml
    # which is pulled in by trytond_account_stock_anglo_saxon
    stock, stock_customer, stock_lost_found, stock_production, \
        stock_supplier, = stepfuns.gGetFeaturesStockAccs(context, company)
    cogs, = Account.find([
        # what kind is cogs and why is it not in the default accounts?
        ('kind', '=', 'other'),
        ('name', '=', sGetFeatureData(context, 'account.template,main_cogs')),
        ('company', '=', company.id),
    ])

    ProductTemplate = proteus.Model.get('product.template')
    template = ProductTemplate()
    uName = 'product'
    if not ProductTemplate.find([('name','=', uName)]):
        ProductUom = proteus.Model.get('product.uom')
        unit, = ProductUom.find([('name', '=', 'Unit')])
        template.name = uName
        template.default_uom = unit
        template.type = 'goods'
        template.purchasable = True
        template.salable = True
        template.list_price = Decimal('10')
        template.cost_price = Decimal('5')
        template.cost_price_method = 'fixed'
        template.delivery_time = 0
        template.account_expense = expense
        template.account_revenue = revenue
        template.account_cogs = cogs
        template.supply_on_sale = True

        template.account_stock = stock
        template.account_stock_supplier = stock_supplier
        template.account_stock_customer = stock_customer
        template.account_stock_production = stock_production
        template.account_stock_lost_found = stock_lost_found

        AccountJournal = proteus.Model.get('account.journal')
        stock_journal, = AccountJournal.find([('code', '=', 'STO')])
        template.account_journal_stock_supplier = stock_journal
        template.account_journal_stock_customer = stock_journal
        template.account_journal_stock_lost_found = stock_journal
        template.save()
    template, = ProductTemplate.find([('name','=', uName)])

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

    ProductSupplier = proteus.Model.get('purchase.product_supplier')
    Product = proteus.Model.get('product.product')

    payable, receivable, = stepfuns.gGetFeaturesPayRec(context, company)
    revenue, expense, = stepfuns.gGetFeaturesRevExp(context, company)

    # These are in by trytond_account_stock_continental/account.xml
    # which is pulled in by trytond_account_stock_anglo_saxon
    stock, stock_customer, stock_lost_found, stock_production, \
        stock_supplier, = stepfuns.gGetFeaturesStockAccs(context, company)
    cogs, = Account.find([
        # what kind is cogs and why is it not in the default accounts?
        ('kind', '=', 'other'),
        ('name', '=', sGetFeatureData(context, 'account.template,main_cogs')),
        ('company', '=', company.id),
    ])

    uSupplier = u'Supplier'
    supplier, = Party.find([('name', '=', uSupplier),])

    ProductTemplate = proteus.Model.get('product.template')
    uName = 'product'
    product = Product()
    template, = ProductTemplate.find([('name','=', uName)])
    product.template = template
    product.save()

    product_supplier = ProductSupplier()
    product_supplier.product = template
    product_supplier.party = supplier
    product_supplier.drop_shipment = True
    product_supplier.delivery_time = 0
    product_supplier.save()

#@step('T/ASASDS Create payment term')
#def step_impl(context):

    PaymentTerm = proteus.Model.get('account.invoice.payment_term')
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
    sale.party = customer
    sale.payment_term = payment_term
    sale_line = SaleLine()
    sale.lines.append(sale_line)
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
    create_purchase.form.payment_term = payment_term
    create_purchase.execute('start')

    purchase, = Purchase.find()
    purchase_line, = purchase.lines
    purchase_line.unit_price = Decimal('3')
    purchase.save()
    Purchase.quote([purchase.id], config.context)
    Purchase.confirm([purchase.id], config.context)
    purchase.reload()
    assert purchase.state == u'confirmed'

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

#@step('T/ASASDS Open customer invoice')
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

    cogs, = Account.find([
                ('kind', '=', 'other'),
                ('company', '=', company.id),
                ('name', '=', 'COGS'),
                ])
    cogs.reload()
    assert cogs.debit == Decimal('150.00')
    assert cogs.credit == Decimal('0.00')
