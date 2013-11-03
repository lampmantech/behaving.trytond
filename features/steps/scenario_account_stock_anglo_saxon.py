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

import time
import datetime
from dateutil.relativedelta import relativedelta
from decimal import Decimal
from proteus import config, Model, Wizard

from .support.fields import string_to_python
from .support import modules
from .support import tools

# Warning - these are hardwired from the Tryton code
from .trytond_constants import *

today = datetime.date.today()

#unused Category
# Create a saved instance of "product.category" named "Category"
@step('T/ASAS/SASAS Create a ProductCategory named "{uName}"')
def step_impl(context, uName):
    # idempotent
    ProductCategory = Model.get('product.category')
    if not ProductCategory.find([('name', '=', uName)]):
        category = ProductCategory(name=uName)
        category.save()
        assert ProductCategory.find([('name', '=', uName)])

# product , 'fixed' or fifo
@step('T/ASAS/SASAS Create a ProductTemplate named "{uName}" having')
def step_impl(context, uName):
    # idempotent

    current_config = context.oProteusConfig
    ProductTemplate = Model.get('product.template')

    if not ProductTemplate.find([('name', '=', uName)]):
        ProductCategory = Model.get('product.category')
        category, = ProductCategory.find([('name', '=', 'Category')])

        ProductUom = Model.get('product.uom')
        unit, = ProductUom.find([('name', '=', 'Unit')])

        Party = Model.get('party.party')
        party, = Party.find([('name', '=', COMPANY_NAME)])
        Company = Model.get('company.company')
        company, = Company.find([('party.id', '=', party.id)])

        AccountJournal = Model.get('account.journal')
        stock_journal, = AccountJournal.find([('code', '=', 'STO'),
                                              ('company', '=', company.id),])

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

        # These are in by trytond_account_stock_continental/account.xml
        # which is pulled in by trytond_account_stock_anglo_saxon
        stock, = Account.find([
            ('kind', '=', 'stock'),
            ('company', '=', company.id),
            ('name', '=', 'Stock')])
        stock_customer, = Account.find([
            ('kind', '=', 'stock'),
            ('company', '=', company.id),
            ('name', '=', 'Stock Customer')])
        stock_lost_found, = Account.find([
            ('kind', '=', 'stock'),
            ('company', '=', company.id),
            ('name', '=', 'Stock Lost and Found')])
        stock_production, = Account.find([
            ('kind', '=', 'stock'),
            ('company', '=', company.id),
            ('name', '=', 'Stock Production')])
        stock_supplier, = Account.find([
            ('kind', '=', 'stock'),
            ('company', '=', company.id),
            ('name', '=', 'Stock Supplier')])

        template = ProductTemplate()
        template.name = uName
        # template_average.cost_price_method = 'fixed'
        # type, cost_price_method
        for row in context.table:
            setattr(template, row['name'],
                    string_to_python(row['name'], row['value'], ProductTemplate))

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
            modules.lInstallModules(['product_cost_fifo'], current_config)

        template.save()

# goods, product
@step('T/ASAS/SASAS Create two products of type "{sType}" from the ProductTemplate named "{uName}" with fields')
# FixMe: actually creates 2 different Product and ProductTemplates
def step_impl(context, sType, uName):
    # idempotent
    
    current_config = context.oProteusConfig
    Product = Model.get('product.product')

    ProductTemplate = Model.get('product.template')
    # FixMe: ('cost_price_method', '=', 'fixed'), gives a SQL Error
    # ProgrammingError: can't adapt type 'product.template'

    template = ProductTemplate.find([('name', '=', uName),
                                     ('type', '=', sType)])[0]

    for row in context.table:
        uRowName = row['name']
        uCostPriceMethod = row['cost_price_method']

        if uCostPriceMethod == u'fixed':
            if not Product.find([('description', '=', uRowName)]):
                product = Product()
                product.template = template
                product.description = uRowName
                product.save()


        elif uCostPriceMethod == u'average':
            if not Product.find([('description', '=', uRowName)]):
                template_average = ProductTemplate(
                    ProductTemplate.copy([template.id],
                                         current_config.context)[0])
                template_average.cost_price_method = uCostPriceMethod
                template_average.save()

                # FixMe: I dont understand this logic here
                # hardcoded this would be ('description', '=', 'product_fixed')
                product_fixed = Product.find([])[0]
                product_average = Product(
                    Product.copy([product_fixed.id], {
                        'template': template_average.id,
                        }, current_config.context)[0])
                product_average.description = uRowName
                product_average.save()

# Direct, 0
@step('T/ASAS/SASAS Create a PaymentTerm named "{uName}" with "{uNum}" days remainder')
def step_impl(context, uName, uNum):
    # idempotent
    PaymentTerm = Model.get('account.invoice.payment_term')
    iNum=int(uNum)
    assert iNum >= 0
    if not PaymentTerm.find([('name', '=', uName)]):
        PaymentTermLine = Model.get('account.invoice.payment_term.line')
        payment_term = PaymentTerm(name=uName)
        payment_term_line = PaymentTermLine(type='remainder', days=iNum)
        payment_term.lines.append(payment_term_line)
        payment_term.save()

# 12 products, Supplier
@step('T/ASAS/SASAS Create a Purchase Order with description "{uDescription}" from Supplier "{uSupplier}" with fields')
def step_impl(context, uDescription, uSupplier):
    # idempotent
    current_config = context.oProteusConfig

    Purchase = Model.get('purchase.purchase')

    Party = Model.get('party.party')
    supplier, = Party.find([('name', '=', uSupplier)])

    if not Purchase.find([('description', '=', uDescription),
                          ('party.id', '=', supplier.id)]):
        purchase = Purchase()
        purchase.party = supplier
        purchase.description = uDescription
        purchase.purchase_date = today
        
        # 'payment_term', 'invoice_method', 'purchase_date', 'currency'
        for row in context.table:
            setattr(purchase, row['name'],
                    string_to_python(row['name'], row['value'], Purchase))

        purchase.save()
        assert Purchase.find([('description', '=', uDescription),
                              ('party.id', '=', supplier.id)])

# 12 products, Supplier
@step('T/ASAS/SASAS Purchase products on the P. O. with description "{uDescription}" from Supplier "{uSupplier}" with quantities')
def step_impl(context, uDescription, uSupplier):
    # idempotent
    current_config = context.oProteusConfig

    Purchase = Model.get('purchase.purchase')
    Product = Model.get('product.product')

    Party = Model.get('party.party')
    supplier, = Party.find([('name', '=', uSupplier)])

    purchase, = Purchase.find([('description', '=', uDescription),
                               ('party.id', '=', supplier.id)])
    if not len(purchase.lines):

        for row in context.table:
            uDescription = row['description']
            quantity = float(row['quantity'])
            unit_price = Decimal(row['unit_price'])
            # allow 0 (<0.0001) quantity or price lines - just skip them
            if quantity < 0.0001 or unit_price == Decimal('0.00'): continue

            product = Product.find([('description', '=', uDescription)])[0]

            PurchaseLine = Model.get('purchase.line')
            purchase_line = PurchaseLine()
            purchase.lines.append(purchase_line)
            purchase_line.product = product
            purchase_line.quantity = quantity
            purchase_line.unit_price = unit_price

        # unneeded?
        purchase.save()

# 12 products, Supplier
@step('T/ASAS/SASAS Quote and Confirm a P. O. with description "{uDescription}" from Supplier "{uSupplier}"')
def step_impl(context, uDescription, uSupplier):
    # idempotent
    current_config = context.oProteusConfig

    Party = Model.get('party.party')
    supplier, = Party.find([('name', '=', uSupplier)])

    Purchase = Model.get('purchase.purchase')
    purchase, = Purchase.find([('description', '=', uDescription),
                               ('party.id', '=', supplier.id)])

    if purchase.state == u'draft':
        Purchase.quote([purchase.id], current_config.context)
        Purchase.confirm([purchase.id], current_config.context)

        # These create the moves on the purchase order
        
# 12 products, Supplier
@step('T/ASAS/SASAS Receive 9 products from the P. O. with description "{uDescription}" from Supplier "{uSupplier}" with quantities')
def step_impl(context, uDescription, uSupplier):
    # idempotent
    current_config = context.oProteusConfig

    ShipmentIn = Model.get('stock.shipment.in')

    Party = Model.get('party.party')
    supplier, = Party.find([('name', '=', uSupplier)])

    # FixMe: Hack alert - how do I find this Move again?
    if not ShipmentIn.find([('supplier.id', '=', supplier.id)]):
        shipment = ShipmentIn(supplier=supplier)

        Purchase = Model.get('purchase.purchase')
        purchase, = Purchase.find([('description', '=', uDescription),
                                   ('party.id', '=', supplier.id)])

        Move = Model.get('stock.move')
        Product = Model.get('product.product')
        # purchase.moves[0].product.description == u'product_fixed'
        # purchase.moves[1].product.description == u'product_average' 5.0
        for row in context.table:
            uDescription = row['description']
            fQuantity = float(row['quantity'])
            # allow 0 (<0.0001) quantity - just skip them
            if fQuantity < 0.0001: continue

            product = Product.find([('description', '=', uDescription)])[0]
            stock_move = Move.find([('product.id', '=', product.id),
                                    ('supplier.id', '=', supplier.id)])[0]
        
            move = Move(stock_move.id)
            shipment.incoming_moves.append(move)
            move.quantity = fQuantity
        shipment.save()

        ShipmentIn.receive([shipment.id], current_config.context)
        ShipmentIn.done([shipment.id], current_config.context)
        assert shipment.state == u'done'

@step('T/ASAS/SASAS After receiving 9 products assert the account credits and debits')
def step_impl(context):
    # NOT idempotent
    current_config = context.oProteusConfig

    Party = Model.get('party.party')
    party, = Party.find([('name', '=', COMPANY_NAME)])
    Company = Model.get('company.company')
    company, = Company.find([('party.id', '=', party.id)])
    Account = Model.get('account.account')

    stock, = Account.find([
                ('kind', '=', 'stock'),
                ('company', '=', company.id),
                ('name', '=', 'Stock')])
    stock_supplier, = Account.find([
                ('kind', '=', 'stock'),
                ('company', '=', company.id),
                ('name', '=', 'Stock Supplier')])
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

# 12 products, Supplier
@step('T/ASAS/SASAS Open a purchase invoice to pay for what we received from the P. O. with description "{uDescription}" to supplier "{uSupplier}" with prices')
def step_impl(context, uDescription, uSupplier):

    current_config = context.oProteusConfig

    Purchase = Model.get('purchase.purchase')

    Party = Model.get('party.party')
    supplier, = Party.find([('name', '=', uSupplier)])
    party, = Party.find([('name', '=', COMPANY_NAME)])
    Company = Model.get('company.company')
    company, = Company.find([('party.id', '=', party.id)])
    purchase, = Purchase.find([('description', '=', uDescription),
                               ('company', '=', company.id),
                               ('party.id', '=', supplier.id)])
    purchase.reload()
    assert purchase.state == u'confirmed'
    invoice, = purchase.invoices

    if invoice.state == u'draft':
        invoice.invoice_date = today
        invoice.accounting_date = invoice.invoice_date
        invoice.description = "pay for what we received from the P. O. with description '%s'" % (uDescription,)
        
        Product = Model.get('product.product')
        for row in context.table:
            uDescription = row['description']
            mUnitPrice = Decimal(row['unit_price'])
            # allow 0 (<= Decimal(0.00)) quantity - just skip them
            if mUnitPrice <= Decimal(0.00): continue
            
            product = Product.find([('description', '=', uDescription)])[0]
            for invoice_line in invoice.lines:
                if invoice_line.product == product:
                    invoice_line.unit_price = mUnitPrice
                    break

        # currency
        # currency_date
        invoice.save()

        Invoice = Model.get('account.invoice')
        Invoice.post([invoice.id], current_config.context)
        assert invoice.state == u'posted'

@step('T/ASAS/SASAS After paying for what we received assert the account credits and debits')
def step_impl(context):
    # NOT idempotent
    current_config = context.oProteusConfig

    Party = Model.get('party.party')
    party, = Party.find([('name', '=', COMPANY_NAME)])
    Company = Model.get('company.company')
    company, = Company.find([('party.id', '=', party.id)])
    
    Account = Model.get('account.account')
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

    stock_supplier, = Account.find([
        ('company', '=', company.id),
        ('name', '=', 'Stock Supplier')])
    stock_supplier.reload()
    assert (stock_supplier.debit, stock_supplier.credit) == \
        (Decimal('46.00'), Decimal('46.00')), \
        "Expected 46.00,46.00 but got %.2f,%.2f" % (stock_supplier.debit, stock_supplier.credit,)

# Customer, Sell 5 products
@step('T/ASAS/SASAS Create a sales order with description "{uDescription}" to customer "{uCustomer}" with fields')
def step_impl(context, uDescription, uCustomer):
    # idempotent
    current_config = context.oProteusConfig

    Sale = Model.get('sale.sale')

    Party = Model.get('party.party')
    customer, = Party.find([('name', '=', uCustomer)])
    party, = Party.find([('name', '=', COMPANY_NAME)])
    Company = Model.get('company.company')
    company, = Company.find([('party.id', '=', party.id)])

    if not Sale.find([('description', '=', uDescription),
                      ('company', '=', company.id),
                      ('party.id', '=', customer.id)]):
        sale = Sale()
        sale.party = customer
        sale.description = uDescription
        
        # 'payment_term', 'invoice_method'
        for row in context.table:
            setattr(sale, row['name'],
                    string_to_python(row['name'], row['value'], Sale))
        sale.save()


@step('T/ASAS/SASAS Sell products on the S. O. with description "{uDescription}" to customer "{uCustomer}" with quantities')
def step_impl(context, uDescription, uCustomer):
    # idempotent
    current_config = context.oProteusConfig

    Sale = Model.get('sale.sale')

    Party = Model.get('party.party')
    customer, = Party.find([('name', '=', uCustomer)])
    party, = Party.find([('name', '=', COMPANY_NAME)])
    Company = Model.get('company.company')
    company, = Company.find([('party.id', '=', party.id)])

    sale, = Sale.find([('description', '=', uDescription),
                       ('company', '=', company.id),
                       ('party.id', '=', customer.id)])
    if len(sale.lines) <= 0:
        SaleLine = Model.get('sale.line')
        
        Product = Model.get('product.product')
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
            
        sale.save()

        Sale.quote([sale.id], current_config.context)
        Sale.confirm([sale.id], current_config.context)
        Sale.process([sale.id], current_config.context)

        assert sale.state == u'processing'

@step('T/ASAS/SASAS Send 5 products on the S. O. with description "{uDescription}" to customer "{uCustomer}"')
def step_impl(context, uDescription, uCustomer):
    # NOT idempotent
    current_config = context.oProteusConfig

    ShipmentOut = Model.get('stock.shipment.out')

    Sale = Model.get('sale.sale')
    SaleLine = Model.get('sale.line')

    Party = Model.get('party.party')
    customer, = Party.find([('name', '=', uCustomer)])
    party, = Party.find([('name', '=', COMPANY_NAME)])
    Company = Model.get('company.company')
    company, = Company.find([('party.id', '=', party.id)])

    sale, = Sale.find([('description', '=', uDescription),
                       ('company', '=', company.id),
                       ('party.id', '=', customer.id)])

    shipment, = sale.shipments
    assert ShipmentOut.assign_try([shipment.id], current_config.context)
    assert shipment.state == u'assigned'
        
    shipment.reload()
    ShipmentOut.pack([shipment.id], current_config.context)
    assert shipment.state == u'packed'

    shipment.reload()
    ShipmentOut.done([shipment.id], current_config.context)
    assert shipment.state == u'done'

@step('T/ASAS/SASAS After shipping to customer assert the account credits and debits')
def step_impl(context):
    # NOT idempotent?
    current_config = context.oProteusConfig

    Account = Model.get('account.account')
    
    Party = Model.get('party.party')
    party, = Party.find([('name', '=', COMPANY_NAME)])
    Company = Model.get('company.company')
    company, = Company.find([('party.id', '=', party.id)])
    
    stock, = Account.find([
                ('kind', '=', 'stock'),
                ('company', '=', company.id),
                ('name', '=', 'Stock')])
    stock_customer, = Account.find([
                ('kind', '=', 'stock'),
                ('company', '=', company.id),
                ('name', '=', 'Stock Customer')])
    stock_customer.reload()
    assert (stock_customer.debit, stock_customer.credit) == \
        (Decimal('28.00'), Decimal('0.00')), \
        "Expected 28.00,0.00 but got %.2f,%.2f" % (stock_customer.debit, stock_customer.credit,)

    stock.reload()
    assert (stock.debit, stock.credit) == \
        (Decimal('50.00'), Decimal('28.00')), \
        "Expected 50.00,28.00 but got %.2f,%.2f" % (stock.debit, stock.credit,)

# Customer
@step('T/ASAS/SASAS Open customer invoice for the S. O. with description "{uDescription}" to customer "{uCustomer}"')
def step_impl(context, uDescription, uCustomer):

    current_config = context.oProteusConfig

    Sale = Model.get('sale.sale')

    Party = Model.get('party.party')
    customer, = Party.find([('name', '=', uCustomer)])
    party, = Party.find([('name', '=', COMPANY_NAME)])
    Company = Model.get('company.company')
    company, = Company.find([('party.id', '=', party.id)])
    
    sale, = Sale.find([('invoice_method', '=', 'shipment'),
                       ('company', '=', company.id),
                       ('party.id', '=', customer.id)])

    # FixMe: not idempotent
    sale.reload()

    Invoice = Model.get('account.invoice')
    invoice, = sale.invoices
    Invoice.post([invoice.id], current_config.context)    
    assert invoice.state == u'posted'

@step('T/ASAS/SASAS After posting the invoice to customer assert the account credits and debits')
def step_impl(context):
    # NOT idempotent?
    current_config = context.oProteusConfig

    Account = Model.get('account.account')
    
    Party = Model.get('party.party')
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

    stock_customer, = Account.find([
                ('kind', '=', 'stock'),
                ('company', '=', company.id),
                ('name', '=', 'Stock Customer')])
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

# Supplier
@step('T/ASAS/SASAS Now create an invoice to supplier "{uSupplier}" by an accountant with quantities')
def step_impl(context, uSupplier):

    current_config = context.oProteusConfig

    Purchase = Model.get('purchase.purchase')

    Party = Model.get('party.party')
    supplier, = Party.find([('name', '=', uSupplier)])

    if not Purchase.find([('invoice_method', '=', 'order'),
                          ('party.id', '=', supplier.id)]):

        PaymentTerm = Model.get('account.invoice.payment_term')
        payment_term, = PaymentTerm.find([('name', '=', 'Direct')])
        purchase = Purchase()
        purchase.party = supplier
        purchase.payment_term = payment_term
        purchase.invoice_method = 'order'

        Product = Model.get('product.product')
        PurchaseLine = Model.get('purchase.line')
        for row in context.table:
            uDescription = row['description']
            fQuantity = float(row['quantity'])
            mUnitPrice = Decimal(row['unit_price'])
            # allow 0 (<0.0001) quantity - just skip them
            if fQuantity < 0.0001 or mUnitPrice <= Decimal(0.0): continue
            
            product = Product.find([('description', '=', uDescription)])[0]

            purchase_line = PurchaseLine()
            purchase.lines.append(purchase_line)
            purchase_line.product = product
            purchase_line.quantity = fQuantity
            purchase_line.unit_price = mUnitPrice
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
