# -*- mode: python; py-indent-offset: 4; coding: utf-8-unix; encoding: utf-8 -*-
"""


"""
from __future__ import print_function

import datetime
from decimal import Decimal

from behave import *
import proteus

from .support.fields import string_to_python, sGetFeatureData, vSetFeatureData
from .support import modules
from .support.tools import *
from .support.stepfuns import vAssertContentTable

TODAY = datetime.date.today()

@step('Create a Payment for an account.invoice on date "{uDate}" with description "{uDescription}" from supplier "{uSupplier}" with |name|value| fields')
def step_impl(context, uDate, uDescription, uSupplier):
    """
    Given \
    Create a Payment for an account.invoice on date with a description.

    It expects a |name|value| table; the fields typically include:
    'journal', 'invoice_date', 'amount', 'currency'
      | name              | value    |
    Idempotent.
    """
    current_config = context.oProteusConfig

    Purchase = proteus.Model.get('purchase.purchase')

    Party = proteus.Model.get('party.party')
    sCompanyName = sGetFeatureData(context, 'party,company_name')
    party, = Party.find([('name', '=', sCompanyName)])
    Company = proteus.Model.get('company.company')
    company, = Company.find([('party.id', '=', party.id)])
    supplier, = Party.find([('name', '=', uSupplier)])

    # comment currency warehouse
    if not Purchase.find([('description', '=', uDescription),
                          ('company.id',  '=', company.id),
                          ('party.id', '=', supplier.id)]):
        purchase = Purchase()
        purchase.party = supplier
        purchase.description = uDescription
        for row in context.table:
            if row['name'] == u'purchase_date':
                uDate = row['value']
                if uDate.lower() == 'today' or uDate.lower() == 'now':
                    oDate = TODAY
                else:
                    oDate = datetime.date(*map(int, uDate.split('-')))
                purchase.purchase_date = oDate
                continue
            setattr(purchase, row['name'],
                    string_to_python(row['name'], row['value'], Purchase))

        purchase.save()
    purchase, = Purchase.find([('description', '=', uDescription),
                               ('company.id',  '=', company.id),
                               ('party.id', '=', supplier.id)])

