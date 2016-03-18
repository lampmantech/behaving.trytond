# -*- mode: python; py-indent-offset: 4; coding: utf-8-unix; encoding: utf-8 -*-
"""
Move Template
"""

import datetime
from decimal import Decimal

from .support.fields import string_to_python, sGetFeatureData, vSetFeatureData
from .support.stepfuns import vAssertContentTable

from behave import *
import proteus

TODAY = datetime.date.today()

@step('Create a MoveTemplate named "{uName}" on a cash Journal with Account "{uAcct}"')
def step_impl(context, uName, uAcct):
    """
    Then Create a MoveTemplate named "CashJV Template" on a cash Journal with Account "1230"')
    """
    Journal = proteus.Model.get('account.journal')
    Account = proteus.Model.get('account.account')
    
    Party = proteus.Model.get('party.party')
    sCompanyName = sGetFeatureData(context, 'party,company_name')
    party, = Party.find([('name', '=', sCompanyName)])
    Company = proteus.Model.get('company.company')
    oCompany, = Company.find([('party.id', '=', party.id)])

    oCashJournal = Journal.find([('type', '=', 'cash')])[0]
    if not oCashJournal.debit_account or not oCashJournal.credit_account:
            oAccount, = Account.find([
                ('kind', '=', 'other'),
                ('name', '=', uAcct),
                ('company', '=', oCompany.id),
                ])
        oCashJournal.debit_account = oAccount
        oCashJournal.credit_account = oAccount
        oCashJournal.save()
    
    vCreateMoveTemplate(context, uName, oCashJournal)

@step('Create a MoveTemplate named "{uName}" on Journal typed "{uJType}"')
def step_impl(context, uName, uJType):
    """
    Then Create a MoveTemplate named "Test" on Journal typed "cash"'
    """
    Journal = proteus.Model.get('account.journal')
    oJournal, = Journal.find([('type', '=', uJType),])
    
    vCreateMoveTemplate(context, uName, oJournal)

@step('Create a MoveTemplate named "{uName}" on Journal coded "{uJCode}"')
def step_impl(context, uName, uJCode):
    """
    Then Create a MoveTemplate named "Test" on Journal coded "CASH"'
    """
    Journal = proteus.Model.get('account.journal')
    oJournal, = Journal.find([('code', '=', uJCode),])
    
    vCreateMoveTemplate(context, uName, oJournal)

def vCreateMoveTemplate(context, uName, oJournal):
    
    MoveTemplate = proteus.Model.get('account.move.template')
    
    Party = proteus.Model.get('party.party')
    sCompanyName = sGetFeatureData(context, 'party,company_name')
    party, = Party.find([('name', '=', sCompanyName)])
    Company = proteus.Model.get('company.company')
    oCompany, = Company.find([('party.id', '=', party.id)])

    # Create Template::
    if not MoveTemplate.find([('name', '=', uName),
                              ('oCompany', '=', oCompany.id),]):

        template = MoveTemplate()
        # date company description
        template.name = uName
        template.company = oCompany
        template.journal = oJournal
        template.save()

    assert MoveTemplate.find([('name', '=', uName),
                              ('company', '=', oCompany.id),])
    
@step('Add keywords to a MoveTemplate named "{uName}" with description "{uTDescription}" and |name|string|type|digits| following')
def step_impl(context, uName, uTDescription):
    """Add keywords to a MoveTemplate named "Test Move Template" with description "{party} - {description}" and|name|string|type|digits| following
    """
    vAssertContentTable(context, 4)

    MoveTemplate = proteus.Model.get('account.move.template')
    
    template, = MoveTemplate.find([('name', '=', uName)])
    uTDescription = '{party} - {description}'
    template.description = uTDescription
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
        ('name', '=', sGetFeatureData(context, 'account.template,main_tax')),
        ('company', '=', oCompany.id),
        ])

    if uTaxName = '0% Sales Tax':
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
            oAccount, = Account.find([
                # ('kind', '=', 'expense'),
                ('name', '=', row['account']),
                ('company', '=', oCompany.id),
                ])
            line.account = oAccount
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
    oCompany, = Company.find([('party.id', '=', party.id)])

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

    period_ids = Period.find([('code', '=', '%d-%d' % (oDate.year, oDate.month)),
                              ('company', '=', oCompany.id)])
    if len(period_ids) == 1:
        keywords['period'] = period_ids[0]

    context = create_move._context.copy()
    context.update(create_move._config.context)
    # note:: using custom call because proteus doesnt support fake model
    _ = create_move._proxy.execute(create_move.session_id, data, 'create_',
            context)

