# -*- mode: python; py-indent-offset: 4; coding: utf-8-unix; encoding: utf-8 -*-
"""
Stock Shipment Out Scenario
from
trytond_stock_supply-3.2.2/tests/scenario_stock_internal_supply.rst
"""
from behave import *
import proteus

import datetime
from dateutil.relativedelta import relativedelta
from decimal import Decimal

from .support.fields import string_to_python, sGetFeatureData, vSetFeatureData
from .support import modules
from .support.tools import *
from .support import stepfuns

TODAY = datetime.date.today()

if False:
#@step('Create company')
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
        currency = Currency(name='US Dollar', symbol=u'$', code='USD',
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

#@step('Reload the context')
#def step_impl(context):

    User = proteus.Model.get('res.user')
    Group = proteus.Model.get('res.group')
    config._context = User.get_preferences(True, config.context)

#@step('Create stock user')
#def step_impl(context):

    stock_user = User()
    stock_user.name = 'Stock'
    stock_user.login = 'stock'
    stock_user.main_company = company
    stock_group, = Group.find([('name', '=', 'Stock')])
    stock_user.groups.append(stock_group)
    stock_user.save()

    ProductUom = proteus.Model.get('product.uom')
    unit, = ProductUom.find([('name', '=', 'Unit')])
    template = ProductTemplate()
    template.name = 'T/SSIS Product Template'
    template.default_uom = unit
    template.type = 'goods'
    template.list_price = Decimal('20')
    template.cost_price = Decimal('8')
    template.save()    
    template, = ProductTemplate.find([('name', '=', 'T/SSIS Product Template')])
    template, = ProductTemplate.find([('name', '=', 'T/SSIS Product Template')])
    product = Product()
    product.template = template
    product.description = 'Product Description'
    product.save()
    product, = Product.find([('description', '=', 'Product Description')])
    
@step('T/SSOS Stock Shipment Out Scenario')
def step_impl(context):
    """
    Notice: no chart of accounts or fiscal year
    """
    
    config = context.oProteusConfig

    Currency = proteus.Model.get('currency.currency')
    CurrencyRate = proteus.Model.get('currency.currency.rate')

    User = proteus.Model.get('res.user')
    Group = proteus.Model.get('res.group')
    
    Party = proteus.Model.get('party.party')
    sCompanyName = sGetFeatureData(context, 'party,company_name')
    party, = Party.find([('name', '=', sCompanyName)])
    Company = proteus.Model.get('company.company')
    company, = Company.find([('party.id', '=', party.id)])

    stock_admin_user, = User.find([('name', '=', 'Stock Admin')])

    stock_user, = User.find([('name', '=', 'Stock')])
    product_admin_user, = User.find([('name', '=', 'Product')])

#@step('Create product')
#def step_impl(context):

    config.user = product_admin_user.id
    ProductTemplate = proteus.Model.get('product.template')
    Product = proteus.Model.get('product.product')
    
    product, = Product.find([('description', '=', 'Product Description')])

#@step('Get stock locations')
#def step_impl(context):

    config.user = stock_admin_user.id
    Location = proteus.Model.get('stock.location')
    warehouse_loc, = Location.find([('code', '=', 'WH')])
    supplier_loc, = Location.find([('code', '=', 'SUP')])
    customer_loc, = Location.find([('code', '=', 'CUS')])
    output_loc, = Location.find([('code', '=', 'OUT')])
    storage_loc, = Location.find([('code', '=', 'STO')])

#@step('Create new internal location')
#def step_impl(context):

    Location = proteus.Model.get('stock.location')
    provisioning_loc = Location()
    provisioning_loc.name = 'Provisioning Location'
    provisioning_loc.type = 'storage'
    provisioning_loc.parent = warehouse_loc
    provisioning_loc.save()

#@step('Create internal order point')
#def step_impl(context):

    OrderPoint = proteus.Model.get('stock.order_point')
    order_point = OrderPoint()
    order_point.product = product
    order_point.warehouse_location = warehouse_loc
    order_point.storage_location = storage_loc
    order_point.provisioning_location = provisioning_loc
    order_point.type = 'internal'
    order_point.min_quantity = 10
    order_point.max_quantity = 15
    order_point.save()

#@step('Create inventory to add enough quantity in Provisioning Location')
#def step_impl(context):

    config.user = stock_user.id
    Inventory = proteus.Model.get('stock.inventory')
    InventoryLine = proteus.Model.get('stock.inventory.line')
    Location = proteus.Model.get('stock.location')
    inventory = Inventory()
    inventory.location = provisioning_loc
    inventory.save()
    inventory_line = InventoryLine(product=product, inventory=inventory)
    inventory_line.quantity = 100.0
    inventory_line.expected_quantity = 0.0
    inventory.save()
    inventory_line.save()
    Inventory.confirm([inventory.id], config.context)
    assert inventory.state == u'done'

#@step('Execute internal supply')
#def step_impl(context):

    ShipmentInternal = proteus.Model.get('stock.shipment.internal')
    proteus.Wizard('stock.shipment.internal.create').execute('create_')
    shipment, = ShipmentInternal.find([])
    assert shipment.state == u'waiting'
    assert len(shipment.moves) == 1
    move, = shipment.moves
    assert move.product.template.name == u'T/SSIS Product Template'
    assert move.quantity == 15.0
    assert move.from_location.name == u'Provisioning Location'
    assert move.to_location.code == u'STO'
