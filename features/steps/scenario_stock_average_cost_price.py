# -*- mode: python; py-indent-offset: 4; coding: utf-8-unix; encoding: utf-8 -*-
"""
Stock Average Cost Price Scenario
from
trytond_stock-3.2.3/tests/scenario_stock_average_cost_price.rst
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
    pass
#@step('Create product')
#def step_impl(context):

    ProductUom = proteus.Model.get('product.uom')
    ProductTemplate = proteus.Model.get('product.template')
    Product = proteus.Model.get('product.product')
    unit, = ProductUom.find([('name', '=', 'Unit')])
    product = Product()
    template = ProductTemplate()
    template.name = 'T/SACP Product Template'
    template.default_uom = unit
    template.type = 'goods'
    template.list_price = Decimal('300')
    template.cost_price = Decimal('80')
    template.cost_price_method = 'average'
    template.save()
    product.template = template
    product.save()
    product, = Product.find([('name', '=', 'T/SACP Product Template')])

    
@step('T/SACP Stock Average Cost Price Scenario')
def step_impl(context):
    config = context.oProteusConfig

    Party = proteus.Model.get('party.party')
    sCompanyName = sGetFeatureData(context, 'party,company_name')
    party, = Party.find([('name', '=', sCompanyName)])
    Company = proteus.Model.get('company.company')
    company, = Company.find([('party.id', '=', party.id)])

    ProductUom = proteus.Model.get('product.uom')
    unit, = ProductUom.find([('name', '=', 'Unit')])
    ProductTemplate = proteus.Model.get('product.template')
    Product = proteus.Model.get('product.product')
    product, = Product.find([('name', '=', 'T/SACP Product Template')])
    
#@step('Get stock locations')
#def step_impl(context):

    Location = proteus.Model.get('stock.location')
    supplier_loc, = Location.find([('code', '=', 'SUP')])
    storage_loc, = Location.find([('code', '=', 'STO')])

#@step('Make 1 unit of the product available @ 100 ')
#def step_impl(context):
    Currency = proteus.Model.get('currency.currency')
    currency, = Currency.find([('code', '=', 'USD')])


#@step('Check Cost Price is 100')
#def step_impl(context):

    product.reload()
    assert product.template.cost_price == Decimal('100.0000')

#@step('Add 1 more unit @ 200')
#def step_impl(context):

    StockMove = proteus.Model.get('stock.move')
    incoming_move = StockMove()
    incoming_move.product = product
    incoming_move.uom = unit
    incoming_move.quantity = 1
    incoming_move.from_location = supplier_loc
    incoming_move.to_location = storage_loc
    incoming_move.planned_date = TODAY
    incoming_move.effective_date = TODAY
    incoming_move.company = company
    incoming_move.unit_price = Decimal('200')
    incoming_move.currency = currency
    incoming_move.save()
    StockMove.do([incoming_move.id], config.context)

#@step('Check Cost Price Average is 150')
#def step_impl(context):

    product.reload()
    assert product.template.cost_price == Decimal('150.0000')
