# -*- encoding: utf-8 -*-
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


today = datetime.date.today()

# 'Stock Admin', 'stock_admin', 'Stock Administration'
@step('Create a stock admin user named "{uName}" with login "{uLogin}" in group "{uGroup}"')
def step_impl(context, uName, uLogin, uGroup):
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
