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
                ('code', '=', uAcct),
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
                              ('company', '=', oCompany.id),]):

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
    """Add keywords to a MoveTemplate named "Test Move Template" with description "{party} - {description}" and |name|string|type|digits| following
    """
    vAssertContentTable(context, 4)

    MoveTemplate = proteus.Model.get('account.move.template')
    
    template, = MoveTemplate.find([('name', '=', uName)])
    template.description = uTDescription
    lKeywords = []
    for row in context.table:
        uKeywordName = row['name'].strip()
        dElts = dict(name=uKeywordName,
                         string=row['string'].strip(),
                         type_=row['type'].strip())
        if dElts['type_'] == 'numeric' and row['digits']:
            dElts['digits'] = int(row['digits'])
        _ = template.keywords.new(**dElts)
        lKeywords.append(uKeywordName)

    # we are going to need this
    if 'date' not in lKeywords:
        dElts = dict(name='date',
                     string='Date',
                     type_='char')
        _ = template.keywords.new(**dElts)
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

    template, = MoveTemplate.find([('name', '=', uName),
                                       ('company', '=', oCompany.id)])
    # Char('Date', help='Leave empty for today')
    if uDate == 'TODAY':
        template.date = ''
        oDate = TODAY
    else:
        template.date = 'date'
        # FixMe: derive assumes yyyy-mm-dd
        oDate = datetime.date(*map(int, uDate.split('-')))

    oPeriod, = Period.find([('company.id', '=', oCompany.id),
                                ('start_date', '<=', oDate),
                                ('end_date', '>=', oDate),])

    #  create_move has a:    move.period = self.template.period
    #? the Period on the template is required to overwrite any previous one?
    template.period = oPeriod
    template.save()
    
    # Create Move::
    create_move = proteus.Wizard('account.move.template.create')
    create_move.form.template = template
    create_move.form.period = oPeriod
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
        elif uKey == 'date':
            # this is required whether its in the lines or not
            pass
        
    keywords['date'] = oDate
        
    oMoveContext = create_move._context.copy()
    oMoveContext.update(create_move._config.context)
    # even with the template.period, this is crucial
    oMoveContext['period'] = oPeriod
    # note:: using custom call because proteus doesnt support fake model
    _ = create_move._proxy.execute(create_move.session_id, data, 'create_',
            oMoveContext)

