# -*- mode: python; py-indent-offset: 4; coding: utf-8-unix; encoding: utf-8 -*-
"""

==================================
Account Stock Continental Scenario
==================================

This is a straight cut-and-paste from
trytond_account-2.8.1/tests/scenario_account_reconciliation.rst

It should be improved to be more like a Behave BDD.
"""

from behave import *
import proteus

import time
import datetime
from dateutil.relativedelta import relativedelta
from decimal import Decimal

from .support.fields import string_to_python, sGetFeatureData, vSetFeatureData
from .support.stepfuns import vAssertContentTable
from .support import modules
from .support import tools
from .support import stepfuns

# Warning - these are hardwired from the Tryton code
from .trytond_constants import *

TODAY = datetime.date.today()

# cost_price_method - one of
dCacheCostPriceMethod={}

# goods, product
@step('T/ASAS/SASAS Create products of type "{uType}" from the ProductTemplate named "{uName}" with fields')
# FixMe: actually creates 2 different Product and ProductTemplates
def step_impl(context, uType, uName):
    """
    Create two products of type "{uType}" from the ProductTemplate named
    "{uName}" with fields
	  | name                | cost_price_method | description         |
	  | product_fixed	| fixed   	    | Product Fixed       |
	  | product_average	| average	    | Product Average     |

    Idempotent.
    """
    global dCacheCostPriceMethod
    current_config = context.oProteusConfig
    Product = proteus.Model.get('product.product')
    ProductTemplate = proteus.Model.get('product.template')
    # FixMe: ('cost_price_method', '=', 'fixed'), gives a SQL Error
    # ProgrammingError: can't adapt type 'product.template'

    sCompanyName = sGetFeatureData(context, 'party,company_name')
    Party = proteus.Model.get('party.party')
    party, = Party.find([('name', '=', sCompanyName)])
    Company = proteus.Model.get('company.company')
    company, = Company.find([('party.id', '=', party.id)])

    # not ('company', '=', company.id),
    oTemplate, = ProductTemplate.find([('name', '=', uName),
                                      ('type', '=', uType)])

    for row in context.table:
        uRowName = row['name']
        uRowDescription = row['description']
        uCostPriceMethod = row['cost_price_method']

        # not ('company', '=', company.id),
        if Product.find([('description', '=', uRowDescription)]): continue

        if uCostPriceMethod == u'fixed':
            product_fixed = Product()
            product_fixed.template = oTemplate
            product_fixed.description = uRowDescription
            product_fixed.save()

        elif uCostPriceMethod == u'average':
            if 'template_average' not in dCacheCostPriceMethod:
                template_average = ProductTemplate(
                    ProductTemplate.copy([oTemplate.id],
                                         current_config.context)[0])
                template_average.cost_price_method = 'average'
                template_average.save()
                dCacheCostPriceMethod['template_average'] = template_average
            else:
                template_average = dCacheCostPriceMethod['template_average']
            # FixMe: I dont understand this logic here
            # hardcoded this would be ('description', '=', 'product_fixed')
            #?product_fixed = Product.find([])[0]
            product_average = Product(
                Product.copy([product_fixed.id], {
                    'template': template_average.id,
                    }, current_config.context)[0])
            #? why use the copy? why not just:
            #product_average = Product()
            #product_average.template = oTemplate_average
            #product_average.description = uRowDescription
            product_average.description = uRowDescription
            product_average.save()

        elif uCostPriceMethod == u'fifo':
            if 'template_fifo' not in dCacheCostPriceMethod:
                template_fifo = ProductTemplate(
                    ProductTemplate.copy([oTemplate.id],
                                         current_config.context)[0])
                template_fifo.cost_price_method = 'fifo'
                template_fifo.save()
                dCacheCostPriceMethod['template_fifo'] = template_fifo
            else:
                template_fifo = dCacheCostPriceMethod['template_fifo']
            product_fifo = Product(
                Product.copy([product_fixed.id], {
                    'template': template_fifo.id,
                    }, current_config.context)[0])
            product_fifo.description = uRowDescription
            product_fifo.save()

# 12 products, Supplier
@step('T/ASAS/SASAS Purchase products on the P. O. with description "{uDescription}" from supplier "{uSupplier}" with quantities')
def step_impl(context, uDescription, uSupplier):
    """
    Purchase products on the P. O. with description "{uDescription}"
    from supplier "{uSupplier}" with quantities
	  | description  	| quantity | unit_price |
	  | product_fixed	| 5.0	   | 4		|
	  | product_average	| 7.0	   | 6		|

    Idempotent.
    """
    current_config = context.oProteusConfig

    Purchase = proteus.Model.get('purchase.purchase')
    Product = proteus.Model.get('product.product')
    Party = proteus.Model.get('party.party')

    sCompanyName = sGetFeatureData(context, 'party,company_name')
    party, = Party.find([('name', '=', sCompanyName)])
    Company = proteus.Model.get('company.company')
    company, = Company.find([('party.id', '=', party.id)])

    supplier, = Party.find([('name', '=', uSupplier),])

    purchase, = Purchase.find([('description', '=', uDescription),
                               ('party.id', '=', supplier.id)])
    if not len(purchase.lines):

        for row in context.table:
            uPDescription = row['description']
            quantity = float(row['quantity'])
            unit_price = Decimal(row['unit_price'])
            # allow 0 (<0.0001) quantity or price lines - just skip them
            if quantity < 0.0001 or unit_price == Decimal('0.00'): continue

            product = Product.find([('description', '=', uPDescription)])[0]

            PurchaseLine = proteus.Model.get('purchase.line')
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
    """
    Idempotent.
    """
    current_config = context.oProteusConfig

    Party = proteus.Model.get('party.party')
    sCompanyName = sGetFeatureData(context, 'party,company_name')
    party, = Party.find([('name', '=', sCompanyName)])
    Company = proteus.Model.get('company.company')
    company, = Company.find([('party.id', '=', party.id)])

    supplier, = Party.find([('name', '=', uSupplier),])

    Purchase = proteus.Model.get('purchase.purchase')
    purchase, = Purchase.find([('description', '=', uDescription),
                               ('party.id', '=', supplier.id)])

    if purchase.state == u'draft':
        Purchase.quote([purchase.id], current_config.context)
        Purchase.confirm([purchase.id], current_config.context)

        # These create the moves on the purchase order

# 12 products, Supplier
@step('T/ASAS/SASAS Receive 9 products from the P. O. with description "{uDescription}" from Supplier "{uSupplier}" with quantities')
def step_impl(context, uDescription, uSupplier):
    """
    Idempotent.
    """
    current_config = context.oProteusConfig

    ShipmentIn = proteus.Model.get('stock.shipment.in')
    Party = proteus.Model.get('party.party')

    sCompanyName = sGetFeatureData(context, 'party,company_name')
    party, = Party.find([('name', '=', sCompanyName)])
    Company = proteus.Model.get('company.company')
    company, = Company.find([('party.id', '=', party.id)])

    supplier, = Party.find([('name', '=', uSupplier),])

    # FixMe: Hack alert - how do I find this Move again?
    if not ShipmentIn.find([('supplier.id', '=', supplier.id)]):
        shipment = ShipmentIn(supplier=supplier)

        Purchase = proteus.Model.get('purchase.purchase')
        purchase, = Purchase.find([('description', '=', uDescription),
                                   ('party.id', '=', supplier.id)])

        Move = proteus.Model.get('stock.move')
        Product = proteus.Model.get('product.product')
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
    """
    NOT idempotent
    """
    current_config = context.oProteusConfig

    Party = proteus.Model.get('party.party')

    sCompanyName = sGetFeatureData(context, 'party,company_name')
    party, = Party.find([('name', '=', sCompanyName)])
    Company = proteus.Model.get('company.company')
    company, = Company.find([('party.id', '=', party.id)])
    Account = proteus.Model.get('account.account')

    stock, = Account.find([
        ('kind', '=', 'stock'),
        ('company', '=', company.id),
        ('name', '=', sGetFeatureData(context, 'account.template,stock')),
        ])
    stock_supplier, = Account.find([
        ('kind', '=', 'stock'),
        ('company', '=', company.id),
        ('name', '=', sGetFeatureData(context, 'account.template,stock_supplier')),
        ])
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
        ('name', '=', sGetFeatureData(context, 'account.template,main_expense')),
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

    Purchase = proteus.Model.get('purchase.purchase')
    Party = proteus.Model.get('party.party')

    sCompanyName = sGetFeatureData(context, 'party,company_name')
    party, = Party.find([('name', '=', sCompanyName)])
    Company = proteus.Model.get('company.company')
    company, = Company.find([('party.id', '=', party.id)])

    supplier, = Party.find([('name', '=', uSupplier),])

    purchase, = Purchase.find([('description', '=', uDescription),
#?                               ('company', '=', company.id),
                               ('party.id', '=', supplier.id)])
    purchase.reload()
    assert purchase.state == u'confirmed'
    invoice, = purchase.invoices

    if invoice.state == u'draft':
        invoice.invoice_date = TODAY
        invoice.accounting_date = invoice.invoice_date
        invoice.description = "pay for what we received from the P. O. with description '%s'" % (uDescription,)

        Product = proteus.Model.get('product.product')
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

        Invoice = proteus.Model.get('account.invoice')
        Invoice.post([invoice.id], current_config.context)
        assert invoice.state == u'posted'

@step('T/ASAS/SASAS After paying for what we received assert the account credits and debits')
def step_impl(context):
    """
    NOT idempotent
    """
    current_config = context.oProteusConfig

    Party = proteus.Model.get('party.party')
    sCompanyName = sGetFeatureData(context, 'party,company_name')
    party, = Party.find([('name', '=', sCompanyName)])
    Company = proteus.Model.get('company.company')
    company, = Company.find([('party.id', '=', party.id)])

    Account = proteus.Model.get('account.account')
    payable, expense = stepfuns.gGetFeaturesPayExp(context, company)

    payable.reload()
    assert (payable.debit, payable.credit) == \
        (Decimal('0.00'), Decimal('44.00')), \
        "Expected 0.00,44.00 but got %.2f,%.2f" % (expense.debit, expense.credit,)

    expense.reload()
    assert (expense.debit, expense.credit) == \
        (Decimal('44.00'), Decimal('50.00')), \
        "Expected 44.00,50.00 but got %.2f,%.2f" % (expense.debit, expense.credit,)

    stock_supplier, = Account.find([
        ('company', '=', company.id),
        ('name', '=', sGetFeatureData(context, 'account.template,stock_supplier')),
        ])
    stock_supplier.reload()
    assert (stock_supplier.debit, stock_supplier.credit) == \
        (Decimal('46.00'), Decimal('46.00')), \
        "Expected 46.00,46.00 but got %.2f,%.2f" % (stock_supplier.debit, stock_supplier.credit,)

# Customer, Sell 5 products
@step('T/ASAS/SASAS Create a sales order with description "{uDescription}" to customer "{uCustomer}" with fields')
def step_impl(context, uDescription, uCustomer):
    """
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
#?                      ('company', '=', company.id),
                      ('party.id', '=', customer.id)]):
        sale = Sale()
        sale.party = customer
        sale.description = uDescription

        # 'payment_term', 'invoice_method'
        for row in context.table:
            setattr(sale, row['name'],
                    string_to_python(row['name'], row['value'], Sale))
        sale.save()

    assert Sale.find([('description', '=', uDescription),
#?                      ('company', '=', company.id),
                      ('party.id', '=', customer.id)])

@step('T/ASAS/SASAS Sell products on the S. O. with description "{uDescription}" to customer "{uCustomer}" with quantities')
def step_impl(context, uDescription, uCustomer):
    """
    Sell products on the S. O. with description "uDescription"
    to customer "uCustomer" with quantities
	  | description     | quantity |
	  | product_fixed   | 2.0      |
	  | product_average | 3.0      |

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
#?                       ('company', '=', company.id),
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

        sale.save()

        Sale.quote([sale.id], current_config.context)
        Sale.confirm([sale.id], current_config.context)
        Sale.process([sale.id], current_config.context)

        assert sale.state == u'processing'

@step('T/ASAS/SASAS Send 5 products on the S. O. with description "{uDescription}" to customer "{uCustomer}"')
def step_impl(context, uDescription, uCustomer):
    """
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
#?                       ('company', '=', company.id),
                       ('party.id', '=', customer.id)])

    shipment, = sale.shipments
    assert ShipmentOut.assign_try([shipment.id], current_config.context)
    # not idempotent
    assert shipment.state == u'assigned'

    shipment.reload()
    # not idempotent
    ShipmentOut.pack([shipment.id], current_config.context)
    assert shipment.state == u'packed'

    shipment.reload()
    # not idempotent
    ShipmentOut.done([shipment.id], current_config.context)
    assert shipment.state == u'done'

@step('T/ASAS/SASAS After shipping to customer assert the account credits and debits')
def step_impl(context):
    """
    T/ASAS/SASAS After shipping to customer assert the account credits and debits
    NOT idempotent.
    """

    current_config = context.oProteusConfig

    Account = proteus.Model.get('account.account')

    Party = proteus.Model.get('party.party')
    sCompanyName = sGetFeatureData(context, 'party,company_name')
    party, = Party.find([('name', '=', sCompanyName)])
    Company = proteus.Model.get('company.company')
    company, = Company.find([('party.id', '=', party.id)])

    stock, = Account.find([
        ('kind', '=', 'stock'),
        ('company', '=', company.id),
        ('name', '=', sGetFeatureData(context, 'account.template,stock')),
        ])
    stock_customer, = Account.find([
        ('kind', '=', 'stock'),
        ('company', '=', company.id),
        ('name', '=', sGetFeatureData(context, 'account.template,stock_customer')),
        ])
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
    """
    Open customer invoice for the Sales Order with description "uDescription"
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
#?                       ('company', '=', company.id),
                       ('party.id', '=', customer.id)])
    # not idempotent
    sale.reload()

    Invoice = proteus.Model.get('account.invoice')
    invoice, = sale.invoices
    # not idempotent
    Invoice.post([invoice.id], current_config.context)
    assert invoice.state == u'posted'

@step('T/ASAS/SASAS After posting the invoice to customer assert the account credits and debits')
def step_impl(context):
    # NOT idempotent?
    current_config = context.oProteusConfig

    Account = proteus.Model.get('account.account')

    Party = proteus.Model.get('party.party')
    sCompanyName = sGetFeatureData(context, 'party,company_name')
    oCompanyParty, = Party.find([('name', '=', sCompanyName)])
    Company = proteus.Model.get('company.company')
    company, = Company.find([('party.id', '=', oCompanyParty.id)])

    receivable, = Account.find([
        ('kind', '=', 'receivable'),
        ('name', '=', sGetFeatureData(context, 'account.template,main_receivable')),
        ('company', '=', company.id),
        ])
    receivable.reload()
    assert (receivable.debit, receivable.credit) == \
        (Decimal('50.00'), Decimal('0.00')), \
        "Expected 50.00,0.00 but got %.2f,%.2f" % (receivable.debit, receivable.credit,)

    revenue, = Account.find([
        ('kind', '=', 'revenue'),
        ('name', '=', sGetFeatureData(context, 'account.template,main_revenue')),
        ('company', '=', company.id),
        ])
    revenue.reload()
    assert (revenue.debit, revenue.credit) == \
        (Decimal('0.00'), Decimal('50.00')), \
        "Expected 0.00,50.00 but got %.2f,%.2f" % (revenue.debit, revenue.credit,)

    stock_customer, = Account.find([
        ('kind', '=', 'stock'),
        ('company', '=', company.id),
        ('name', '=', sGetFeatureData(context, 'account.template,stock_customer')),
        ])
    stock_customer.reload()
    assert (stock_customer.debit, stock_customer.credit) == \
        (Decimal('28.00'), Decimal('28.00')), \
        "Expected 28.00,28.00 but got %.2f,%.2f" % (stock_customer.debit, stock_customer.credit,)

    cogs, = Account.find([
        ('kind', '=', 'other'),
        ('company', '=', company.id),
        ('name', '=', sGetFeatureData(context, 'account.template,main_cogs')),
        ])
    cogs.reload()
    assert (cogs.debit, cogs.credit) == \
        (Decimal('28.00'), Decimal('0.00')), \
        "Expected 28.00,0.00 but got %.2f,%.2f" % (cogs.debit, cogs.credit,)

# Supplier, Direct
@step('T/ASAS/SASAS Create an invoice to supplier "{uSupplier}" with PaymentTerm "{uPaymentTerm}" by an accountant with quantities')
def step_impl(context, uSupplier, uPaymentTerm):
    """
    Create an invoice to supplier "uSupplier" with PaymentTerm "uPaymentTerm"
    by an accountant with quantities
	  | description     | quantity	| unit_price |
	  | product_fixed   | 5.0      	| 4.00	     |

    Idempotent.
    """
    current_config = context.oProteusConfig

    Purchase = proteus.Model.get('purchase.purchase')

    Party = proteus.Model.get('party.party')
    sCompanyName = sGetFeatureData(context, 'party,company_name')
    oCompanyParty, = Party.find([('name', '=', sCompanyName)])
    Company = proteus.Model.get('company.company')
    company, = Company.find([('party.id', '=', oCompanyParty.id)])

    supplier, = Party.find([('name', '=', uSupplier),])

    if not Purchase.find([('invoice_method', '=', 'order'),
                          ('party.id', '=', supplier.id)]):

        PaymentTerm = proteus.Model.get('account.invoice.payment_term')
        payment_term, = PaymentTerm.find([('name', '=', uPaymentTerm)])

        purchase = Purchase()
        purchase.party = supplier
        purchase.payment_term = payment_term
        purchase.invoice_method = 'order'

        Product = proteus.Model.get('product.product')
        PurchaseLine = proteus.Model.get('purchase.line')
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

        new_config = proteus.config.set_trytond(
            user=sGetFeatureData(context, 'user,accountant,login'),
            password=sGetFeatureData(context, 'user,accountant,password'),
            database_name=current_config.database_name)
        invoice_ids = [i.id for i in purchase.invoices]
        #? is this right? or does it matter?
        #? current_config.user = accountant.id
        
        Invoice = proteus.Model.get('account.invoice')
        Invoice.write(invoice_ids, {
            'invoice_date': TODAY,
        }, new_config.context)
        #? invoice.save()

        Invoice.validate_invoice([i.id for i in purchase.invoices], new_config.context)

# Supplier, Direct
@step('T/ASAS/SASAS Create an invoice to supplier "{uSupplier}" with PaymentTerm "{uPaymentTerm}" by an accountant with negative quantities')
def step_impl(context, uSupplier, uPaymentTerm):
    """
    Unfinished

    >>> invoice = Invoice()
    >>> invoice.party = customer
    >>> invoice.payment_term = payment_term
    >>> invoice_line = invoice.lines.new()
    >>> invoice_line.product = product
    >>> invoice_line.quantity = -1
    >>> invoice.save()
    >>> Invoice.post([invoice.id], config.context)
    >>> invoice.state
    u'posted'
    >>> move = invoice.move
    >>> line_cogs, = (l for l in move.lines if l.account == cogs)
    >>> line_cogs.credit
    Decimal('5.00')
    >>> line_stock, = (l for l in move.lines if l.account == stock_customer)
    >>> line_stock.debit
    Decimal('5.00')
    """
    pass
