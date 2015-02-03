# -*- mode: python; py-indent-offset: 4; coding: utf-8-unix; encoding: utf-8 -*-
"""


"""
from behave import *
import proteus

import datetime
from dateutil.relativedelta import relativedelta
from decimal import Decimal

from .support.fields import string_to_python, sGetFeatureData, vSetFeatureData
from .support import modules
from .support.tools import *

TODAY = datetime.date.today()

# 'Stock Admin', 'stock_admin', 'Stock Administration'
@step('Create a stock admin user named "{uName}" with login "{uLogin}" in group "{uGroup}"')
def step_impl(context, uName, uLogin, uGroup):
    """
    Create a stock admin user named "{uName}" with login "{uLogin}" in group "{uGroup}"
    """
    current_config = context.oProteusConfig

    User = proteus.Model.get('res.user')
    Company = proteus.Model.get('company.company')

    sCompanyName = sGetFeatureData(context, 'party,company_name')
    party, = Party.find([('name', '=', sCompanyName)])
    company, = Company.find([('party.id', '=', party.id)])

    if not User.find([('name', '=', uName)]):
        stock_admin_user = User()
        stock_admin_user.name = uName
        stock_admin_user.login = uLogin
        stock_admin_user.main_company = company

        Group = proteus.Model.get('res.group')
        stock_admin_group, = Group.find([('name', '=', uGroup)])
        stock_admin_user.groups.append(stock_admin_group)
        stock_admin_user.save()
    assert User.find([('name', '=', uName)])

# 'Provisioning Location', 'storage', 'WH'
@step('Create a new stock.location named "{uName}" of type "{uType}" of parent with code "{uParent}"')
def step_impl(context, uName, uType, uParent):
    """
    Create a new stock.location named "{uName}" of type "{uType}" of parent with code "{uParent}"
    """
    current_config = context.oProteusConfig

# these can take a lot of fields including address

    # FixMe:
    #  config.user = stock_admin_user.id
    Location = proteus.Model.get('stock.location')
    if not Location.find([('name', '=', uName)]):
        # WH only?
        storage_loc, = Location.find([('code', '=', uParent)])

        provisioning_loc = Location()
        provisioning_loc.name = uName
        provisioning_loc.type = uType
        provisioning_loc.parent = storage_loc
        provisioning_loc.save()

    assert Location.find([('name', '=', uName)])

@step('Add to inventory as user named "{uUser}" with storage at the location coded "{uCode}" with |product|quantity|expected_quantity| fields')
def step_impl(context, uUser, uCode):
    """
    Create an Inventory as user named "{uUser}"
    with storage at the location with code "{uCode}"
    The following fields are the name of the product and the
    quantity and expected_quantity as floats.
    | product | quantity | expected_quantity |
    | product | 100.0    | 0.0               |
    """
    config = context.oProteusConfig

    User = proteus.Model.get('res.user')
    Inventory = proteus.Model.get('stock.inventory')
    Location = proteus.Model.get('stock.location')
    Product = proteus.Model.get('product.product')

    stock_user, = User.find([('name', '=', uUser)])
    proteus.config.user = stock_user.id
    inventory, = Inventory.find([('location.code', '=', uCode)])

    InventoryLine = proteus.Model.get('stock.inventory.line')
    for row in context.table:
        product, = Product.find([('name','=', row['product'])])
        inventory_line = InventoryLine(product=product, inventory=inventory)
        inventory_line.quantity = float(row['quantity'])
        inventory_line.expected_quantity = float(row['expected_quantity'])
        inventory.save()
        inventory_line.save()

    Inventory.confirm([inventory.id], config.context)
    assert inventory.state == u'done'
    admin_user = User(0)
    proteus.config.user = admin_user.id

@step('Create an Inventory as user named "{uUser}" with storage at the location coded "{uCode}"')
def step_impl(context, uUser, uCode):
    """
    Create an Inventory as user named "{uUser}"
    with storage at the location with code "{uCode}"
    """
    config = context.oProteusConfig

    User = proteus.Model.get('res.user')
    Inventory = proteus.Model.get('stock.inventory')
    Location = proteus.Model.get('stock.location')

    stock_user, = User.find([('name', '=', uUser)])
    proteus.config.user = stock_user.id
    if not Inventory.find([('location.code', '=', uCode)]):
        storage, = Location.find([
                    ('code', '=', uCode),
                    ])
        inventory = Inventory()
        inventory.location = storage
        inventory.save()
    inventory, = Inventory.find([('location.code', '=', uCode)])
    admin_user = User(0)
    proteus.config.user = admin_user.id

