# -*- encoding: utf-8 -*-
"""

===============================
Account Reconciliation Scenario
===============================

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

# Warning - these are hardwired from the Tryton code
from .trytond_constants import *

today = datetime.date.today()

@step('Create parties')
def step_impl(context):
    
    Party = Model.get('party.party')
    Company = Model.get('company.company')
    Account = Model.get('account.account')
    
    company, = Company.find()
    if not Party.find([('name', '=', 'Customer')]):
        payables = Account.find([
                ('kind', '=', 'payable'),
                ('company', '=', company.id),
                ])
        assert payables
        payable = payables[0]
        customer = Party(name='Customer')
        customer.account_payable = payable
        customer.save()

        assert Party.find([('name', '=', 'Customer')])
