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

@step('T/AIMT Add lines to a MoveTemplate named "{uName}" with Tax "{uTaxName}" and |amount|account|tax|party|operation| following')
def step_impl(context, uName, uTaxName):
    """T/AIMT Add lines to a MoveTemplate named "Test Move Template" with Tax "10% Sales Tax" and |amount|account|tax|party|operation| following
    """
    vAssertContentTable(context, 4)

    MoveTemplate = proteus.Model.get('account.move.template')
    
    Party = proteus.Model.get('party.party')
    sCompanyName = sGetFeatureData(context, 'party,company_name')
    party, = Party.find([('name', '=', sCompanyName)])
    Company = proteus.Model.get('company.company')
    oCompany, = Company.find([('party.id', '=', party.id)])

    template, = MoveTemplate.find([('name', '=', uName)])

    Account = proteus.Model.get('account.account')
    payable, = Account.find([
        ('kind', '=', 'payable'),
        ('name', '=', sGetFeatureData(context, 'account.template,main_payable')),
        ('company', '=', oCompany.id),
        ])
    expense, = Account.find([
        ('kind', '=', 'expense'),
        ('name', '=', sGetFeatureData(context, 'account.template,main_expense')),
        ('company', '=', oCompany.id),
        ])
    account_tax, = Account.find([
        ('kind', '=', 'other'),
        # Purchase Tax Control Account
        ('name', '=', sGetFeatureData(context, 'account.template,main_input_tax')),
        ('company', '=', oCompany.id),
        ])

    if uTaxName == '0% Sales Tax':
        oTax = None
    else:
        Tax = proteus.Model.get('account.tax')
        oTax, = Tax.find([('name', '=', uTaxName)])
        assert oTax.type == 'percentage'
        oTaxRate = oTax.rate

    for row in context.table:
        line = template.lines.new()
        line.operation = row['operation']
        if row['account'] == 'payable':
            line.account = payable
        elif row['account'] == 'expense':
            line.account = expense
        elif row['account'] == 'invoice_account':
            line.account = oTax.invoice_account
        else:
            assert line.account, "Account not in: payable expense invoice_account"
        line.party = row['party']
        line.amount = row['amount']
        
        if oTax and row['tax']:
            ttax = line.taxes.new()
            ttax.amount = line.amount
            if row['tax'] == 'base':
                ttax.code = oTax.invoice_base_code
            elif row['tax'] == 'tax':
                ttax.code = oTax.invoice_tax_code
            ttax.tax = oTax
            
    template.save()

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
