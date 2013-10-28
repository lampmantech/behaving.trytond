# -*- encoding: utf-8 -*-
"""

==================================
Account Stock Continental Scenario
==================================

This is a straight cut-and-paste from
trytond_account-2.8.1/tests/scenario_account_reconciliation.rst

It should be improved to be more like a Behave BDD.
"""

from behave import *
from proteus import Model, Wizard

import datetime
from dateutil.relativedelta import relativedelta
from decimal import Decimal
from proteus import config, Model, Wizard
from .support.fields import string_to_python

# Warning - these are hardwired from the Tryton code
from .trytond_constants import *

today = datetime.date.today()

# Account
@step('TS/SASAS Create an ACCOUNTANT_USER user with the "{sGroup}" group')
def step_impl(context, sGroup):
    # idempotent
    User = Model.get('res.user')
    Group = Model.get('res.group')

    if not User.find([('name', '=', ACCOUNTANT_NAME)]):
        accountant = User()
        accountant.name = ACCOUNTANT_NAME
        accountant.login = ACCOUNTANT_USER
        accountant.password = ACCOUNTANT_PASSWORD
        account_group, = Group.find([('name', '=', sGroup)])
        accountant.groups.append(account_group)
        accountant.save()

    assert User.find([('name', '=', 'Accountant')])

#unused Category
# Create a saved instance of "product.category" named "Category"
@step('TS/SASAS Create a ProductCategory named "{sName}"')
def step_impl(context, sName):
    # idempotent
    ProductCategory = Model.get('product.category')
    if not ProductCategory.find([('name', '=', sName)]):
        category = ProductCategory(name=sName)
        category.save()
        assert ProductCategory.find([('name', '=', sName)])

# product , 'fixed' or fifo
@step('TS/SASAS Create a ProductTemplate named "{sName}" having')
def step_impl(context, sName):
    # idempotent

    ProductTemplate = Model.get('product.template')

    if not ProductTemplate.find([('name', '=', sName)]):
        ProductCategory = Model.get('product.category')
        category, = ProductCategory.find([('name', '=', 'Category')])

        ProductUom = Model.get('product.uom')
        unit, = ProductUom.find([('name', '=', 'Unit')])

        Party = Model.get('party.party')
        party, = Party.find([('name', '=', COMPANY_NAME)])
        Company = Model.get('company.company')
        company, = Company.find([('party.id', '=', party.id)])

        AccountJournal = Model.get('account.journal')
        stock_journal, = AccountJournal.find([('code', '=', 'STO')])

        Account = Model.get('account.account')
        revenue, = Account.find([
            ('kind', '=', 'revenue'),
            ('company', '=', company.id),
            ])
        expense, = Account.find([
            ('kind', '=', 'expense'),
            ('company', '=', company.id),
            ])
        cogs, = Account.find([
                    ('kind', '=', 'other'),
                    ('company', '=', company.id),
                    ('name', '=', 'COGS'),
                    ])

        # FixMe: where are these defined? Theyre not in Minimal A
        (stock, stock_customer, stock_lost_found, stock_production,
                stock_supplier) = Account.find([
                    ('kind', '=', 'stock'),
                    ('company', '=', company.id),
                    ('name', 'like', 'Stock%'),
                    ], order=[('name', 'ASC')])
        template = ProductTemplate()
        template.name = sName
        # type, cost_price_method
        for row in context.table:
            setattr(template, row['name'],
                    string_to_python(row['name'], row['value']))

        template.category = category
        template.default_uom = unit
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

        if template.cost_price_method == 'fifo':
            # FixMe: assert product_cost_fifo is loaded
            pass

        template.save()

# product, average or fifo
@step('TS/SASAS Create a product from the ProductTemplate named "{sName}"')
# FixMe: actually creates 2 different Product and ProductTemplates
def step_impl(context, sName):

    current_config = context.oProteusConfig
    Product = Model.get('product.product')

    ProductTemplate = Model.get('product.template')
    # FixMe: ('cost_price_method', '=', 'fixed'), gives a SQL Error
    # ProgrammingError: can't adapt type 'product.template'

    template = ProductTemplate.find([('name', '=', sName),
                                     ('type', '=', 'goods')])[0]

    # FixMe: Hack alert - how do I find this Product again?
    if not 'product' in context.dData['feature']:
        product = Product()
        product.template = template
        product.description = 'test product'
        product.save()

        # FixMe: Hack alert - we want to avoid using context.dData
        context.dData['feature']['product'] = product
        
    # FixMe: Hack alert - how do I find this Product again?
    if not 'product_average' in context.dData['feature']:
        template_average = ProductTemplate(
            ProductTemplate.copy([template.id],
                                 current_config.context)[0])
        template_average.cost_price_method = 'average'
        template_average.save()
        
        product = context.dData['feature']['product']
        product_average = Product(
            Product.copy([product.id], {
                'template': template_average.id,
                }, current_config.context)[0])
        # FixMe: Hack alert - we want to avoid using context.dData
        context.dData['feature']['product_average'] = product_average

# Direct, 0
@step('TS/SASAS Create a PaymentTerm named "{sName}" with "{iNum}" days remainder')
def step_impl(context, sName, iNum):
    # idempotent
    PaymentTerm = Model.get('account.invoice.payment_term')
    iNum=int(iNum)
    assert iNum >= 0
    if not PaymentTerm.find([('name', '=', sName)]):
        PaymentTermLine = Model.get('account.invoice.payment_term.line')
        payment_term = PaymentTerm(name=sName)
        payment_term_line = PaymentTermLine(type='remainder', days=iNum)
        payment_term.lines.append(payment_term_line)
        payment_term.save()

@step('TS/SASAS Purchase 12 products from Supplier "{sSupplier}"')
def step_impl(context, sSupplier):
    # idempotent
    current_config = context.oProteusConfig

    Purchase = Model.get('purchase.purchase')

    Party = Model.get('party.party')
    supplier, = Party.find([('name', '=', sSupplier)])

    if not Purchase.find([('invoice_method', '=', 'shipment'),
                          ('party.id', '=', supplier.id)]):
        purchase = Purchase()

        PaymentTerm = Model.get('account.invoice.payment_term')
        payment_term, = PaymentTerm.find([('name', '=', 'Direct')])

        purchase.party = supplier
        purchase.payment_term = payment_term
        purchase.invoice_method = 'shipment'

        # FixMe: Hack alert - we want to avoid using context.dData
        product = context.dData['feature']['product']
        # FixMe: Hack alert - we want to avoid using context.dData
        product_average = context.dData['feature']['product_average']

        PurchaseLine = Model.get('purchase.line')
        purchase_line = PurchaseLine()
        purchase.lines.append(purchase_line)
        purchase_line.product = product
        purchase_line.quantity = 5.0
        purchase_line.unit_price = Decimal(4)
        
        purchase_line = PurchaseLine()
        purchase.lines.append(purchase_line)
        purchase_line.product = product_average
        purchase_line.quantity = 7.0
        purchase_line.unit_price = Decimal(6)
        purchase.save()
        # FixMe: Hack alert - we want to avoid using context.dData
        context.dData['feature']['purchase'] = purchase

        Purchase.quote([purchase.id], current_config.context)
        Purchase.confirm([purchase.id], current_config.context)
        assert purchase.state == u'confirmed'

@step('TS/SASAS Receive 9 products from Supplier "{sSupplier}"')
def step_impl(context, sSupplier):
    # idempotent
    current_config = context.oProteusConfig

    ShipmentIn = Model.get('stock.shipment.in')

    Party = Model.get('party.party')
    supplier, = Party.find([('name', '=', sSupplier)])

    # FixMe: Hack alert - how do I find this Move again?
    if not ShipmentIn.find([('supplier.id', '=', supplier.id)]):
        shipment = ShipmentIn(supplier=supplier)

        Purchase = Model.get('purchase.purchase')
        purchase, = Purchase.find([('invoice_method', '=', 'shipment'),
                                   ('party.id', '=', supplier.id)])

        Move = Model.get('stock.move')
        move = Move(purchase.moves[0].id)
        shipment.incoming_moves.append(move)
        move.quantity = 4.0

        move = Move(purchase.moves[1].id)
        shipment.incoming_moves.append(move)
        move.quantity = 5.0
        shipment.save()

        ShipmentIn.receive([shipment.id], current_config.context)
        ShipmentIn.done([shipment.id], current_config.context)
        assert shipment.state == u'done'

        party, = Party.find([('name', '=', COMPANY_NAME)])
        Company = Model.get('company.company')
        company, = Company.find([('party.id', '=', party.id)])
        Account = Model.get('account.account')
        (stock, stock_customer, stock_lost_found, stock_production,
                stock_supplier) = Account.find([
                    ('kind', '=', 'stock'),
                    ('company', '=', company.id),
                    ('name', 'like', 'Stock%'),
                    ], order=[('name', 'ASC')])
        stock_supplier.reload()

        stock.reload()
        assert (stock_supplier.debit, stock_supplier.credit) == \
            (Decimal('0.00'), Decimal('46.00')), \
            "Expected 0.00,46.00 but got %.2f,%.2f" % (stock_supplier.debit, stock_supplier.credit,)

        stock.reload()
        assert (stock.debit, stock.credit) == \
            (Decimal('50.00'), Decimal('0.00')), \
            "Expected 50.00,0.00 but got %.2f,%.2f" % (stock.debit, stock.credit,)
        expense, = Account.find([
            ('kind', '=', 'expense'),
            ('company', '=', company.id),
            ])
        expense.reload()
        assert (expense.debit, expense.credit) == \
            (Decimal('0.00'), Decimal('4.00')), \
            "Expected 0.00,4.00 but got %.2f,%.2f" % (expense.debit, expense.credit,)

@step('TS/SASAS Open purchase invoice to Supplier "{sSupplier}"')
def step_impl(context, sSupplier):

    current_config = context.oProteusConfig

    Invoice = Model.get('account.invoice')
    Account = Model.get('account.account')

    Party = Model.get('party.party')
    supplier, = Party.find([('name', '=', sSupplier)])
    Purchase = Model.get('purchase.purchase')
    purchase, = Purchase.find([('invoice_method', '=', 'shipment'),
                               ('party.id', '=', supplier.id)])
    purchase.reload()

    # FixMe: not idempotent
    invoice, = purchase.invoices
    invoice_line = invoice.lines[0]
    invoice_line.unit_price = Decimal('6')
    invoice_line = invoice.lines[1]
    invoice_line.unit_price = Decimal('4')
    invoice.invoice_date = today
    invoice.save()

    Invoice.post([invoice.id], current_config.context)
    assert invoice.state == u'posted'

    party, = Party.find([('name', '=', COMPANY_NAME)])
    Company = Model.get('company.company')
    company, = Company.find([('party.id', '=', party.id)])
    payable, = Account.find([
        ('kind', '=', 'payable'),
        ('company', '=', company.id),
        ])
    payable.reload()
    assert (payable.debit, payable.credit) == \
        (Decimal('0.00'), Decimal('44.00')), \
        "Expected 0.00,44.00 but got %.2f,%.2f" % (expense.debit, expense.credit,)

    expense, = Account.find([
        ('kind', '=', 'expense'),
        ('company', '=', company.id),
        ])
    expense.reload()
    assert (expense.debit, expense.credit) == \
        (Decimal('44.00'), Decimal('50.00')), \
        "Expected 44.00,50.00 but got %.2f,%.2f" % (expense.debit, expense.credit,)

    (stock, stock_customer, stock_lost_found, stock_production,
     stock_supplier) = Account.find([
        ('kind', '=', 'stock'),
        ('company', '=', company.id),
        ('name', 'like', 'Stock%'),
        ], order=[('name', 'ASC')])
    stock_supplier.reload()
    assert (stock_supplier.debit, stock_supplier.credit) == \
        (Decimal('46.00'), Decimal('46.00')), \
        "Expected 46.00,46.00 but got %.2f,%.2f" % (stock_supplier.debit, stock_supplier.credit,)

@step('TS/SASAS Sell 5 products to customer "{sCustomer}"')
def step_impl(context, sCustomer):
    # idempotent
    current_config = context.oProteusConfig

    Sale = Model.get('sale.sale')

    Party = Model.get('party.party')
    customer, = Party.find([('name', '=', sCustomer)])

    if not Sale.find([('invoice_method', '=', 'shipment'),
                      ('party.id', '=', customer.id)]):
        sale = Sale()
        sale.party = customer
        PaymentTerm = Model.get('account.invoice.payment_term')
        payment_term, = PaymentTerm.find([('name', '=', 'Direct')])
        sale.payment_term = payment_term
        sale.invoice_method = 'shipment'

        # FixMe: Hack alert - we want to avoid using context.dData
        product = context.dData['feature']['product']
        # FixMe: Hack alert - we want to avoid using context.dData
        product_average = context.dData['feature']['product_average']

        SaleLine = Model.get('sale.line')
        sale_line = SaleLine()
        sale.lines.append(sale_line)
        sale_line.product = product
        sale_line.quantity = 2.0

        sale_line = SaleLine()
        sale.lines.append(sale_line)
        sale_line.product = product_average
        sale_line.quantity = 3.0
        sale.save()

        Sale.quote([sale.id], current_config.context)
        Sale.confirm([sale.id], current_config.context)
        Sale.process([sale.id], current_config.context)

        assert sale.state == u'processing'

@step('TS/SASAS Send 5 products to customer "{sCustomer}"')
def step_impl(context, sCustomer):
    current_config = context.oProteusConfig

    ShipmentOut = Model.get('stock.shipment.out')

    Sale = Model.get('sale.sale')
    SaleLine = Model.get('sale.line')

    Party = Model.get('party.party')
    customer, = Party.find([('name', '=', sCustomer)])

    sale, = Sale.find([('invoice_method', '=', 'shipment'),
                       ('party.id', '=', customer.id)])

    # FixMe: not idempotent
    shipment, = sale.shipments
    assert ShipmentOut.assign_try([shipment.id], current_config.context)
    assert shipment.state == u'assigned'

    shipment.reload()
    ShipmentOut.pack([shipment.id], current_config.context)
    assert shipment.state == u'packed'

    shipment.reload()
    ShipmentOut.done([shipment.id], current_config.context)
    assert shipment.state == u'done'

    party, = Party.find([('name', '=', COMPANY_NAME)])
    Company = Model.get('company.company')
    company, = Company.find([('party.id', '=', party.id)])
    Account = Model.get('account.account')
    (stock, stock_customer, stock_lost_found, stock_production,
     stock_supplier) = Account.find([
        ('kind', '=', 'stock'),
        ('company', '=', company.id),
        ('name', 'like', 'Stock%'),
        ], order=[('name', 'ASC')])
    stock_customer.reload()
    assert (stock_customer.debit, stock_customer.credit) == \
        (Decimal('28.00'), Decimal('0.00')), \
        "Expected 28.00,0.00 but got %.2f,%.2f" % (stock_customer.debit, stock_customer.credit,)

    stock.reload()
    assert (stock.debit, stock.credit) == \
        (Decimal('50.00'), Decimal('28.00')), \
        "Expected 50.00,28.00 but got %.2f,%.2f" % (stock.debit, stock.credit,)

@step('TS/SASAS Open customer invoice')
def step_impl(context):

    current_config = context.oProteusConfig

    Account = Model.get('account.account')
    Invoice = Model.get('account.invoice')

    Party = Model.get('party.party')
    customer, = Party.find([('name', '=', 'Customer')])
    Sale = Model.get('sale.sale')
    sale, = Sale.find([('invoice_method', '=', 'shipment'),
                      ('party.id', '=', customer.id)])

    # FixMe: not idempotent
    sale.reload()

    invoice, = sale.invoices
    Invoice.post([invoice.id], current_config.context)
    assert invoice.state == u'posted'

    party, = Party.find([('name', '=', COMPANY_NAME)])
    Company = Model.get('company.company')
    company, = Company.find([('party.id', '=', party.id)])
    receivable, = Account.find([
        ('kind', '=', 'receivable'),
        ('company', '=', company.id),
        ])
    receivable.reload()
    assert (receivable.debit, receivable.credit) == \
        (Decimal('50.00'), Decimal('0.00')), \
        "Expected 50.00,0.00 but got %.2f,%.2f" % (receivable.debit, receivable.credit,)

    revenue, = Account.find([
        ('kind', '=', 'revenue'),
        ('company', '=', company.id),
        ])
    revenue.reload()
    assert (revenue.debit, revenue.credit) == \
        (Decimal('0.00'), Decimal('50.00')), \
        "Expected 0.00,50.00 but got %.2f,%.2f" % (revenue.debit, revenue.credit,)

    (stock, stock_customer, stock_lost_found, stock_production,
     stock_supplier) = Account.find([
        ('kind', '=', 'stock'),
        ('company', '=', company.id),
        ('name', 'like', 'Stock%'),
        ], order=[('name', 'ASC')])
    stock_customer.reload()
    assert (stock_customer.debit, stock_customer.credit) == \
        (Decimal('28.00'), Decimal('28.00')), \
        "Expected 28.00,28.00 but got %.2f,%.2f" % (stock_customer.debit, stock_customer.credit,)

    cogs, = Account.find([
        ('kind', '=', 'other'),
        ('company', '=', company.id),
        ('name', '=', 'COGS'),
        ])
    cogs.reload()
    assert (cogs.debit, cogs.credit) == \
        (Decimal('28.00'), Decimal('0.00')), \
        "Expected 28.00,0.00 but got %.2f,%.2f" % (cogs.debit, cogs.credit,)

@step('TS/SASAS Now create a supplier invoice with an accountant')
def step_impl(context):

    current_config = context.oProteusConfig

    Purchase = Model.get('purchase.purchase')

    Party = Model.get('party.party')
    supplier, = Party.find([('name', '=', 'Supplier')])
    PaymentTerm = Model.get('account.invoice.payment_term')
    payment_term, = PaymentTerm.find([('name', '=', 'Direct')])

    supplier, = Party.find([('name', '=', 'Supplier')])
    if not Purchase.find([('invoice_method', '=', 'order'),
                          ('party.id', '=', supplier.id)]):

        purchase = Purchase()
        purchase.party = supplier
        purchase.payment_term = payment_term
        purchase.invoice_method = 'order'

        # FixMe: Hack alert - we want to avoid using context.dData
        product = context.dData['feature']['product']

        PurchaseLine = Model.get('purchase.line')
        purchase_line = PurchaseLine()
        purchase.lines.append(purchase_line)
        purchase_line.product = product
        purchase_line.quantity = 5.0
        purchase_line.unit_price = Decimal(4)
        purchase.save()

        Purchase.quote([purchase.id], current_config.context)
        Purchase.confirm([purchase.id], current_config.context)
        assert purchase.state == u'confirmed'

        import proteus
        new_config = proteus.config.set_trytond(
            user=ACCOUNTANT_USER,
            password=ACCOUNTANT_PASSWORD,
            database_name=current_config.database_name)
        for invoice in purchase.invoices:
                invoice.invoice_date = today
                invoice.save()
                Invoice = Model.get('account.invoice')
        Invoice.validate_invoice([i.id for i in purchase.invoices], new_config.context)