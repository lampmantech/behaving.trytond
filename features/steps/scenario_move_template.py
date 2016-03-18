# -*- mode: python; py-indent-offset: 4; coding: utf-8-unix; encoding: utf-8 -*-
"""
Move Template Scenario
"""

import datetime
from decimal import Decimal

from .support.fields import string_to_python, sGetFeatureData, vSetFeatureData
from .support import modules
from .support.stepfuns import vAssertContentTable

from behave import *
import proteus

TODAY = datetime.date.today()

@step('T/AIMT Check the moves with the description "{uMoveDescription}" and Tax named "{uTaxName}"')
def step_impl(context, uMoveDescription, uTaxName):
    """T/AIMT Check the moves with the description "{uMoveDescription}" and Tax named "{uTaxName}"
    """
    # uLineDescription = uName +' ' +uDate
    # uMoveDescription = 'Supplier' +' - ' +uLineDescription

    # Check the Move::
    Move = proteus.Model.get('account.move')
    move = Move.find([('description', '=', uMoveDescription)])[0]

    assert len(move.lines) == 3
    assert sorted((l.debit, l.credit) for l in move.lines) == \
      [(Decimal('0'), Decimal('12.24')),
       (Decimal('1.11'),  Decimal('0')),
       (Decimal('11.13'), Decimal('0'))]

    Tax = proteus.Model.get('account.tax')
    tax, = Tax.find([('name', '=', uTaxName)])
    assert tax.invoice_base_code.sum == Decimal('11.13')
    assert tax.invoice_tax_code.sum ==  Decimal('1.11')
