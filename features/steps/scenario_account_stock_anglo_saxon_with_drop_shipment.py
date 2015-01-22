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

TODAY = datetime.date.today()

@step('Account Stock Anglo-Saxon with Drop Shipment Scenario')
def step_impl(context):

#@step('T/ASASDS Create database')
#def step_impl(context):
## replaced by Create database with pool.test set to True
#    config = proteus.config.set_trytond()
#    config.pool.test = True
    config = context.oProteusConfig
    
#@step('T/ASASDS Install sale_supply_drop_shipment, sale, purchase')
#def step_impl(context):

    Module = proteus.Model.get('ir.module.module')
    modules = Module.find([
                ('name', 'in', ('account_stock_anglo_saxon',
                    'sale_supply_drop_shipment', 'sale', 'purchase')),
                ])
    Module.install([x.id for x in modules], config.context)
    proteus.Wizard('ir.module.module.install_upgrade').execute('upgrade')

#@step('T/ASASDS Create company')
#def step_impl(context):

    Currency = proteus.Model.get('currency.currency')
    CurrencyRate = proteus.Model.get('currency.currency.rate')
    Company = proteus.Model.get('company.company')
    Party = proteus.Model.get('party.party')
    company_config = proteus.Wizard('company.company.config')
    company_config.execute('company')
    company = company_config.form
    party = Party(name='Dunder Mifflin')
    party.save()
    company.party = party
    currencies = Currency.find([('code', '=', 'USD')])
    if not currencies:
        currency = Currency(name='USD', symbol=u'$', code='USD',
                            rounding=Decimal('0.01'), mon_grouping='[3, 3, 0]',
                            mon_decimal_point='.')
        currency.save()
        CurrencyRate(date=TODAY + relativedelta(month=1, day=1),
                     rate=Decimal('1.0'), currency=currency).save()
    else:
        currency, = currencies
    company.currency = currency
    company_config.execute('add')
    company, = Company.find()

#@step('T/ASASDS Reload the context')
#def step_impl(context):

    User = proteus.Model.get('res.user')
    Group = proteus.Model.get('res.group')
    config._context = User.get_preferences(True, config.context)

#@step('T/ASASDS Create sale user')
#def step_impl(context):

    sale_user = User()
    sale_user.name = 'Sale'
    sale_user.login = 'sale'
    sale_user.main_company = company
    sale_group, = Group.find([('name', '=', 'Sales')])
    sale_user.groups.append(sale_group)
    sale_user.save()
    sale_user, = User.find([('name', '=', 'Sale')])

#@step('T/ASASDS Create purchase user')
#def step_impl(context):

    purchase_user = User()
    purchase_user.name = 'Purchase'
    purchase_user.login = 'purchase'
    purchase_user.main_company = company
    purchase_group, = Group.find([('name', '=', 'Purchase')])
    purchase_user.groups.append(purchase_group)
    purchase_request_group, = Group.find(
            [('name', '=', 'Purchase Request')])
    purchase_user.groups.append(purchase_request_group)
    purchase_user.save()

#@step('T/ASASDS Create stock user')
#def step_impl(context):

    stock_user = User()
    stock_user.name = 'Stock'
    stock_user.login = 'stock'
    stock_user.main_company = company
    stock_group, = Group.find([('name', '=', 'Stock')])
    stock_user.groups.append(stock_group)
    stock_user.save()

#@step('T/ASASDS Create account user')
#def step_impl(context):

    account_user = User()
    account_user.name = 'Account'
    account_user.login = 'account'
    account_user.main_company = company
    account_group, = Group.find([('name', '=', 'Account')])
    account_user.groups.append(account_group)
    account_user.save()

#@step('T/ASASDS Create fiscal year')
#def step_impl(context):

    FiscalYear = proteus.Model.get('account.fiscalyear')
    Sequence = proteus.Model.get('ir.sequence')
    SequenceStrict = proteus.Model.get('ir.sequence.strict')
    fiscalyear = FiscalYear(name='%s' % TODAY.year)
    fiscalyear.start_date = TODAY + relativedelta(month=1, day=1)
    fiscalyear.end_date = TODAY + relativedelta(month=12, day=31)
    fiscalyear.company = company
    post_move_sequence = Sequence(name='%s' % TODAY.year,
            code='account.move',
            company=company)
    post_move_sequence.save()
    fiscalyear.post_move_sequence = post_move_sequence
    invoice_sequence = SequenceStrict(name='%s' % TODAY.year,
                                      code='account.invoice',
                                      company=company)
    invoice_sequence.save()
    fiscalyear.out_invoice_sequence = invoice_sequence
    fiscalyear.in_invoice_sequence = invoice_sequence
    fiscalyear.out_credit_note_sequence = invoice_sequence
    fiscalyear.in_credit_note_sequence = invoice_sequence
    fiscalyear.save()
    FiscalYear.create_period([fiscalyear.id], config.context)

#@step('T/ASASDS Create chart of accounts')
#def step_impl(context):

    AccountTemplate = proteus.Model.get('account.account.template')
    Account = proteus.Model.get('account.account')
    AccountJournal = proteus.Model.get('account.journal')
    account_template, = AccountTemplate.find([('parent', '=', None)])
    create_chart = proteus.Wizard('account.create_chart')
    create_chart.execute('account')
    create_chart.form.account_template = account_template
    create_chart.form.company = company
    create_chart.execute('create_account')
    receivable, = Account.find([
                ('kind', '=', 'receivable'),
                ('company', '=', company.id),
                ])
    payable, = Account.find([
                ('kind', '=', 'payable'),
                ('company', '=', company.id),
                ])
    revenue, = Account.find([
                ('kind', '=', 'revenue'),
                ('company', '=', company.id),
                ])
    expense, = Account.find([
                ('kind', '=', 'expense'),
                ('company', '=', company.id),
                ])
    (stock, stock_customer, stock_lost_found, stock_production,
            stock_supplier) = Account.find([
                ('kind', '=', 'stock'),
                ('company', '=', company.id),
                ('name', 'like', 'Stock%'),
                ], order=[('name', 'ASC')])
    cogs, = Account.find([
                ('kind', '=', 'other'),
                ('company', '=', company.id),
                ('name', '=', 'COGS'),
                ])
    create_chart.form.account_receivable = receivable
    create_chart.form.account_payable = payable
    create_chart.execute('create_properties')
    stock_journal, = AccountJournal.find([('code', '=', 'STO')])

#@step('T/ASASDS Create parties')
#def step_impl(context):

    Party = proteus.Model.get('party.party')
    supplier = Party(name='Supplier')
    supplier.save()
    customer = Party(name='Customer')
    customer.save()

#@step('T/ASASDS Create product')
#def step_impl(context):

    ProductUom = proteus.Model.get('product.uom')
    ProductSupplier = proteus.Model.get('purchase.product_supplier')
    unit, = ProductUom.find([('name', '=', 'Unit')])
    ProductTemplate = proteus.Model.get('product.template')
    Product = proteus.Model.get('product.product')
    product = Product()
    template = ProductTemplate()
    template.name = 'product'
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
    template.account_stock = stock
    template.account_cogs = cogs
    template.account_stock_supplier = stock_supplier
    template.account_stock_customer = stock_customer
    template.account_stock_production = stock_production
    template.account_stock_lost_found = stock_lost_found
    template.account_journal_stock_supplier = stock_journal
    template.account_journal_stock_customer = stock_journal
    template.account_journal_stock_lost_found = stock_journal
    template.supply_on_sale = True
    template.save()
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

    Invoice = proteus.Model.get('account.invoice')
    config.user = purchase_user.id
    purchase.reload()
    invoice, = purchase.invoices
    
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

    config.user = sale_user.id
    sale.reload()
    invoice, = sale.invoices
    
#?    account_user = User.find([('name', '=', 'Account')])
    config.user = account_user.id
    Invoice.post([invoice.id], config.context)
    assert invoice.state == u'posted'
    
    receivable, = Account.find([
                ('kind', '=', 'receivable'),
                ('company', '=', company.id),
                ])
    receivable.reload()
    assert receivable.debit == Decimal('500.00')
    assert receivable.credit == Decimal('0.00')
    
    revenue, = Account.find([
                ('kind', '=', 'revenue'),
                ('company', '=', company.id),
                ])
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
