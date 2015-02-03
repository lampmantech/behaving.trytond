# -*- mode: python; py-indent-offset: 4; coding: utf-8-unix; encoding: utf-8 -*-
"""

===============================
Account Reconciliation Scenario
===============================

This is a straight cut-and-paste from
trytond_account-2.8.1/tests/scenario_account_reconciliation.rst

It should be improved to be more like a Behave BDD.
"""

from behave import *
import proteus

import datetime
from dateutil.relativedelta import relativedelta
from decimal import Decimal

from .support.fields import string_to_python, sGetFeatureData, vSetFeatureData

today = datetime.date.today()

@step('T/A/SAR Create Moves for direct reconciliation')
def step_impl(context):
    """
    Tryton is the only Python project that puts NO documentation in its doctests!
    """
    Move = proteus.Model.get('account.move')

    Party = proteus.Model.get('party.party')
    sCompanyName = sGetFeatureData(context, 'party,company_name')
    party, = Party.find([('name', '=', sCompanyName)])
    Company = proteus.Model.get('company.company')
    company, = Company.find([('party.id', '=', party.id)])

    Journal = proteus.Model.get('account.journal')
    journal_revenue, = Journal.find([('code', '=', 'REV'),])
    journal_cash, = Journal.find([('code', '=', 'CASH'),])

    FiscalYear = proteus.Model.get('account.fiscalyear')
    fiscalyear, = FiscalYear.find([('name', '=', str(today.year))])
    period = fiscalyear.periods[0]

    Account = proteus.Model.get('account.account')
    receivable, = Account.find([
        ('kind', '=', 'receivable'),
        ('name', '=', sGetFeatureData(context, 'account.template,main_receivable')),
        ('company', '=', company.id),
        ])
    revenue, = Account.find([
        ('kind', '=', 'revenue'),
        ('name', '=', sGetFeatureData(context, 'account.template,main_revenue')),
        ('company', '=', company.id),
        ])
    cash, = Account.find([
        ('kind', '=', 'other'),
        ('company', '=', company.id),
        ('name', '=', sGetFeatureData(context, 'account.template,main_cash')),
        ])
    customer, = Party.find([('name', '=', 'Customer')])

    move = Move()
    move.period = period
    move.journal = journal_revenue
    move.date = period.start_date

    line = move.lines.new()
    line.account = revenue
    line.credit = Decimal(42)
    line = move.lines.new()
    line.account = receivable
    line.debit = Decimal(42)
    line.party = customer
    move.save()

    reconcile1, = [l for l in move.lines if l.account == receivable]
    # FixMe: bring up - we want to avoid using context.dData in the code
    context.dData['feature']['reconcile1'] = reconcile1

    move = Move()
    move.period = period
    move.journal = journal_cash
    move.date = period.start_date

    line = move.lines.new()
    line.account = cash
    line.debit = Decimal(42)
    line.party = customer
    line = move.lines.new()
    line.account = receivable
    line.credit = Decimal(42)
    line.party = customer
    move.save()

    reconcile2, = [l for l in move.lines if l.account == receivable]
    # FixMe: bring up - we want to avoid using context.dData in the code
    context.dData['feature']['reconcile2'] = reconcile2

@step('T/A/SAR Reconcile Lines without writeoff')
def step_impl(context):
    """
    Tryton is the only Python project that puts NO documentation in its doctests!
    """

    reconcile1 = context.dData['feature']['reconcile1']
    reconcile2 = context.dData['feature']['reconcile2']

    reconcile_lines = proteus.Wizard('account.move.reconcile_lines',
            [reconcile1, reconcile2])
    assert reconcile_lines.state == 'end'

    reconcile1.reload()

    reconcile2.reload()

    assert reconcile1.reconciliation == reconcile2.reconciliation != None
    assert len(reconcile1.reconciliation.lines) == 2

@step('T/A/SAR Create Moves for writeoff reconciliation')
def step_impl(context):
    """
    Tryton is the only Python project that puts NO documentation in its doctests!
    """

    Move = proteus.Model.get('account.move')

    Journal = proteus.Model.get('account.journal')
    journal_revenue, = Journal.find([
                ('code', '=', 'REV'),
                ])
    journal_cash, = Journal.find([
                ('code', '=', 'CASH'),
                ])

    FiscalYear = proteus.Model.get('account.fiscalyear')
    fiscalyear, = FiscalYear.find([('name', '=', str(today.year))])
    period = fiscalyear.periods[0]

    move = Move()
    move.period = period
    move.journal = journal_revenue
    move.date = period.start_date

    Party = proteus.Model.get('party.party')
    customer, = Party.find([('name', '=', 'Customer')])

    sCompanyName = sGetFeatureData(context, 'party,company_name')
    party, = Party.find([('name', '=', sCompanyName)])
    Company = proteus.Model.get('company.company')
    company, = Company.find([('party.id', '=', party.id)])

    Account = proteus.Model.get('account.account')
    receivable, = Account.find([
        ('kind', '=', 'receivable'),
        ('name', '=', sGetFeatureData(context, 'account.template,main_receivable')),
        ('company', '=', company.id),
        ])
    revenue, = Account.find([
        ('kind', '=', 'revenue'),
        ('name', '=', sGetFeatureData(context, 'account.template,main_revenue')),
        ('company', '=', company.id),
        ])
    cash, = Account.find([
        ('kind', '=', 'other'),
        ('company', '=', company.id),
        ('name', '=', sGetFeatureData(context, 'account.template,main_cash')),
        ])

    line = move.lines.new()
    line.account = revenue
    line.credit = Decimal(68)
    line = move.lines.new()
    line.account = receivable
    line.debit = Decimal(68)
    line.party = customer
    move.save()

    reconcile1, = [l for l in move.lines if l.account == receivable]
    # FixMe: bring up - we want to avoid using context.dData in the code
    context.dData['feature']['reconcile1'] = reconcile1

    move = Move()
    move.period = period
    move.journal = journal_cash
    move.date = period.start_date

    line = move.lines.new()
    line.account = cash
    line.debit = Decimal(65)
    line.party = customer

    line = move.lines.new()
    line.account = receivable
    line.credit = Decimal(65)
    line.party = customer
    move.save()

    reconcile2, = [l for l in move.lines if l.account == receivable]
    # FixMe: bring up - we want to avoid using context.dData in the code
    context.dData['feature']['reconcile2'] = reconcile2

@step('T/A/SAR Reconcile Lines with writeoff')
def step_impl(context):
    """
    Tryton is the only Python project that puts NO documentation in its doctests!
    """

    reconcile1 = context.dData['feature']['reconcile1']
    assert reconcile1
    reconcile2 = context.dData['feature']['reconcile2']
    assert reconcile2

    Party = proteus.Model.get('party.party')
    sCompanyName = sGetFeatureData(context, 'party,company_name')
    party, = Party.find([('name', '=', sCompanyName)])
    Company = proteus.Model.get('company.company')
    company, = Company.find([('party.id', '=', party.id)])

    Account = proteus.Model.get('account.account')
    expense, = Account.find([
        ('kind', '=', 'expense'),
        ('name', '=', sGetFeatureData(context, 'account.template,main_expense')),
        ('company', '=', company.id),
        ])
    revenue, = Account.find([
        ('kind', '=', 'revenue'),
        ('name', '=', sGetFeatureData(context, 'account.template,main_revenue')),
        ('company', '=', company.id),
        ])

    reconcile_lines = proteus.Wizard('account.move.reconcile_lines',
            [reconcile1, reconcile2])
    assert reconcile_lines.form_state == 'writeoff'

    Journal = proteus.Model.get('account.journal')
    # Fixme: how do we know the tryton version we are talking to?
    # I'll assume it's the same as the proteus for now
    sMaj, sMin, sMic = proteus.__version__.split('.')
    if int(sMaj) < 3 or ( int(sMaj) == 3 and int(sMin) < 2):
        # This errors on 3.2 but not <= 3.0
        journal_expense, = Journal.find([
                ('code', '=', 'EXP'),
                ])
        reconcile_lines.form.journal = journal_expense
        reconcile_lines.form.account = expense
    else:
        Sequence = proteus.Model.get('ir.sequence')
#        SequenceStrict = proteus.Model.get('ir.sequence.strict')
        sequence_journal, = Sequence.find([('code', '=', 'account.journal')])
        journal_writeoff = Journal(name='Write-Off', type='write-off',
                                   sequence=sequence_journal,
                                   credit_account=revenue,
                                   debit_account=expense)
        journal_writeoff.save()

        reconcile_lines.form.journal = journal_writeoff

    reconcile_lines.execute('reconcile')

    reconcile1.reload()
    reconcile2.reload()
    assert reconcile1.reconciliation == reconcile2.reconciliation != None
    assert len(reconcile1.reconciliation.lines) == 3

    writeoff_line1, = [l for l in reconcile1.reconciliation.lines
            if l.credit == Decimal(3)]
    writeoff_line2, = [l for l in writeoff_line1.move.lines
            if l != writeoff_line1]

    assert writeoff_line2.account == expense
    assert writeoff_line2.debit == Decimal(3)
