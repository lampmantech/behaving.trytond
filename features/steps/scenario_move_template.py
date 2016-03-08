# -*- mode: python; py-indent-offset: 4; coding: utf-8-unix; encoding: utf-8 -*-
"""
Move Template Scenario
"""

from behave import *
import proteus

import datetime
from decimal import Decimal

from .support.fields import string_to_python, sGetFeatureData, vSetFeatureData
from .support import modules
from .support.stepfuns import vAssertContentTable

TODAY = datetime.date.today()

@step('Create a MoveTemplate named "{uName}" on Journal coded "{uJCode}"')
def step_impl(context, uName, uJCode):
    """
    Then Create a MoveTemplate named "Test" on Journal coded "CASH"'
    """
    current_config = context.oProteusConfig

    Party = proteus.Model.get('party.party')
    sCompanyName = sGetFeatureData(context, 'party,company_name')
    party, = Party.find([('name', '=', sCompanyName)])
    Company = proteus.Model.get('company.company')
    company, = Company.find([('party.id', '=', party.id)])

    # Create Template::

    MoveTemplate = proteus.Model.get('account.move.template')
    Journal = proteus.Model.get('account.journal')

    template = MoveTemplate()
    # date company description
    template.name = uName
    template.journal, = Journal.find([('code', '=', uJCode),])
    template.save()

@step('Add keywords to a MoveTemplate named "{uName}" with description "{uTDescription}" and |name|string|type|digits| following')
def step_impl(context, uName, uTDescription):
    """Add keywords to a MoveTemplate named "Test Move Template" with description "{party} - {description}" and|name|string|type|digits| following
    """
    vAssertContentTable(context, 4)

    MoveTemplate = proteus.Model.get('account.move.template')
    template, = MoveTemplate.find([('name', '=', uName)])
    uTDescription = '{party} - {description}'
    template.description = uTDescription
    if False:
        _ = template.keywords.new(name='party', string='Party',
                type_='party')
        _ = template.keywords.new(name='description', string='Description',
                type_='char')
        _ = template.keywords.new(name='amount', string='Amount',
                type_='numeric', digits=2)
    else:
        for row in context.table:
            dElts = dict(name=row['name'], string=row['string'], type_=row['type'])
            if dElts['type_'] == 'numeric' and row['digits']:
                dElts['digits'] = int(row['digits'])
            _ = template.keywords.new(**dElts)
    template.save()

@step('Add lines to a MoveTemplate named "{uName}" with Tax "{uTaxName}" and |amount|account|tax|party|operation| following')
def step_impl(context, uName, uTaxName):
    """Add lines to a MoveTemplate named "Test Move Template" with Tax "10% Sales Tax" and |amount|account|tax|party|operation| following
    """
    vAssertContentTable(context, 4)
    Party = proteus.Model.get('party.party')
    sCompanyName = sGetFeatureData(context, 'party,company_name')
    party, = Party.find([('name', '=', sCompanyName)])
    Company = proteus.Model.get('company.company')
    company, = Company.find([('party.id', '=', party.id)])

    MoveTemplate = proteus.Model.get('account.move.template')
    template, = MoveTemplate.find([('name', '=', uName)])

    Account = proteus.Model.get('account.account')
    payable, = Account.find([
        ('kind', '=', 'payable'),
        ('name', '=', sGetFeatureData(context, 'account.template,main_payable')),
        ('company', '=', company.id),
        ])
    expense, = Account.find([
        ('kind', '=', 'expense'),
        ('name', '=', sGetFeatureData(context, 'account.template,main_expense')),
        ('company', '=', company.id),
        ])
    account_tax, = Account.find([
        ('kind', '=', 'other'),
        ('name', '=', sGetFeatureData(context, 'account.template,main_tax')),
        ('company', '=', company.id),
        ])

    from trytond.modules.account.tests.tools import \
            get_accounts, create_tax, set_tax_code

    # Create tax with code::
    oTaxRate = Decimal('0.1')
    tax = set_tax_code(create_tax(oTaxRate))
    tax.save()

    Tax = proteus.Model.get('account.tax')
    tax, = Tax.find([('name', '=', uTaxName)])
    assert tax.type == 'percentage'
    oTaxRate = tax.rate

    if True:
        for row in context.table:
            line = template.lines.new()
            line.operation = row['operation']
            if row['account'] == 'payable':
                line.account = payable
            elif row['account'] == 'expense':
                line.account = expense
            elif row['account'] == 'invoice_account':
                line.account = tax.invoice_account
            line.party = row['party']
            line.amount = row['amount']
            if row['tax']:
                ttax = line.taxes.new()
                ttax.amount = line.amount
                if row['tax'] == 'base':
                    ttax.code = tax.invoice_base_code
                elif row['tax'] == 'tax':
                    ttax.code = tax.invoice_tax_code
                ttax.tax = tax
    else:
        line = template.lines.new()
        line.operation = 'credit'
        line.account = payable
        line.party = 'party'
        line.amount = 'amount'

        line = template.lines.new()
        line.operation = 'debit'
        line.account = expense
        line.amount = 'amount / 1.1'
        ttax = line.taxes.new()
        ttax.amount = line.amount
        ttax.code = tax.invoice_base_code
        ttax.tax = tax

        line = template.lines.new()
        line.operation = 'debit'
        line.account = tax.invoice_account
        line.amount = 'amount * (1 - 1/1.1)'
        ttax = line.taxes.new()
        ttax.amount = line.amount
        ttax.code = tax.invoice_tax_code
        ttax.tax = tax

    template.save()

@step('Create a move from a MoveTemplate named "{uName}" on date "{uDate}" with |name|value| keywords following')
def step_impl(context, uName, uDate):
    """Create a move from a MoveTemplate named "Test Move Template" on date "TODAY" with |name|value| keywords following

    Date is in yyyy-mm-dd format, or TODAY.
    """
    vAssertContentTable(context, 2)

    MoveTemplate = proteus.Model.get('account.move.template')
    Period = proteus.Model.get('account.period')
    Party = proteus.Model.get('party.party')

    sCompanyName = sGetFeatureData(context, 'party,company_name')
    party, = Party.find([('name', '=', sCompanyName)])
    Company = proteus.Model.get('company.company')
    company, = Company.find([('party.id', '=', party.id)])

    template, = MoveTemplate.find([('name', '=', uName)])
    # Create Move::
    create_move = proteus.Wizard('account.move.template.create')
    # Char('Date', help='Leave empty for today')
    if uDate == 'TODAY':
        template.date = ''
    else:
        template.date = uDate
    create_move.form.template = template
    create_move.execute('keywords')

    data = {}
    keywords = data['keywords'] = {}
    if False:
        supplier, = Party.find([('name', '=', 'Supplier'),])
        keywords['party'] = supplier.id
        uLineDescription = uName +' ' +uDate
        keywords['description'] = uLineDescription
        keywords['amount'] = Decimal('12.24')
    else:
        for row in context.table:
            uKey = row['name']
            if uKey == 'description':
                keywords[uKey] = row['value']
            elif uKey == 'party':
                oParty, = Party.find([('name', '=', row['value']),])
                keywords[uKey] = oParty.id
            elif uKey == 'amount':
                keywords[uKey] = Decimal(row['value'])

    # derive keywords['period'] from uDate for move
    if uDate == 'TODAY':
        oDate = TODAY
    else:
        # FixMe: derive assumes yyyy-mm-dd
        oDate = datetime.date(*uDate.split('-'))
    period_ids = Period.find(company.id, date=oDate)
    if len(period_ids) == 1:
        keywords['period'] = period_ids[0]

    context = create_move._context.copy()
    context.update(create_move._config.context)
    # note:: using custom call because proteus doesnt support fake model
    _ = create_move._proxy.execute(create_move.session_id, data, 'create_',
            context)

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
