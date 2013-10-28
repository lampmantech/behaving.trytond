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

# Customer
@step('TS/SAR Create a party named "{sName}" with an account_payable attribute')
def step_impl(context, sName):

    Party = Model.get('party.party')
    Company = Model.get('company.company')
    Account = Model.get('account.account')

    if not Party.find([('name', '=', sName)]):
        party, = Party.find([('name', '=', COMPANY_NAME)])
        company, = Company.find([('party.id', '=', party.id)])
        payables = Account.find([
                ('kind', '=', 'payable'),
                ('company', '=', company.id),
                ])
        assert payables
        payable = payables[0]
        customer = Party(name=sName)
        customer.account_payable = payable
        customer.save()

    assert Party.find([('name', '=', sName)])

@step('TS/SAR Create Moves for direct reconciliation')
def step_impl(context):

    Move = Model.get('account.move')

    Journal = Model.get('account.journal')
    journal_revenue, = Journal.find([
                ('code', '=', 'REV'),
                ])
    journal_cash, = Journal.find([
                ('code', '=', 'CASH'),
                ])

    FiscalYear = Model.get('account.fiscalyear')
    fiscalyear, = FiscalYear.find([('name', '=', str(today.year))])
    period = fiscalyear.periods[0]

    Party = Model.get('party.party')
    party, = Party.find([('name', '=', COMPANY_NAME)])
    Company = Model.get('company.company')
    company, = Company.find([('party.id', '=', party.id)])
    Account = Model.get('account.account')
    receivable, = Account.find([
        ('kind', '=', 'receivable'),
        ('company', '=', company.id),
        ])
    revenue, = Account.find([
        ('kind', '=', 'revenue'),
        ('company', '=', company.id),
        ])
    cash, = Account.find([
        ('kind', '=', 'other'),
        ('company', '=', company.id),
        ('name', '=', 'Main Cash'),
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
    # FixMe: Hack alert - we want to avoid using context.dData
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
    # FixMe: Hack alert - we want to avoid using context.dData
    context.dData['feature']['reconcile2'] = reconcile2

@step('TS/SAR Reconcile Lines without writeoff')
def step_impl(context):

    reconcile1 = context.dData['feature']['reconcile1']
    reconcile2 = context.dData['feature']['reconcile2']

    reconcile_lines = Wizard('account.move.reconcile_lines',
            [reconcile1, reconcile2])
    assert reconcile_lines.state == 'end'

    reconcile1.reload()

    reconcile2.reload()

    assert reconcile1.reconciliation == reconcile2.reconciliation != None
    assert len(reconcile1.reconciliation.lines) == 2

@step('TS/SAR Create Moves for writeoff reconciliation')
def step_impl(context):

    Move = Model.get('account.move')

    Journal = Model.get('account.journal')
    journal_revenue, = Journal.find([
                ('code', '=', 'REV'),
                ])
    journal_cash, = Journal.find([
                ('code', '=', 'CASH'),
                ])

    FiscalYear = Model.get('account.fiscalyear')
    fiscalyear, = FiscalYear.find([('name', '=', str(today.year))])
    period = fiscalyear.periods[0]

    move = Move()
    move.period = period
    move.journal = journal_revenue
    move.date = period.start_date

    Party = Model.get('party.party')
    customer, = Party.find([('name', '=', 'Customer')])

    party, = Party.find([('name', '=', COMPANY_NAME)])
    Company = Model.get('company.company')
    company, = Company.find([('party.id', '=', party.id)])
    Account = Model.get('account.account')
    receivable, = Account.find([
        ('kind', '=', 'receivable'),
        ('company', '=', company.id),
        ])
    revenue, = Account.find([
        ('kind', '=', 'revenue'),
        ('company', '=', company.id),
        ])
    cash, = Account.find([
        ('kind', '=', 'other'),
        ('company', '=', company.id),
        ('name', '=', 'Main Cash'),
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
    # FixMe: Hack alert - we want to avoid using context.dData
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
    # FixMe: Hack alert - we want to avoid using context.dData
    context.dData['feature']['reconcile2'] = reconcile2

@step('TS/SAR Reconcile Lines with writeoff')
def step_impl(context):

    reconcile1 = context.dData['feature']['reconcile1']
    reconcile2 = context.dData['feature']['reconcile2']

    Party = Model.get('party.party')
    party, = Party.find([('name', '=', COMPANY_NAME)])
    Company = Model.get('company.company')
    company, = Company.find([('party.id', '=', party.id)])

    Account = Model.get('account.account')
    expense, = Account.find([
        ('kind', '=', 'expense'),
        ('company', '=', company.id),
        ])

    Journal = Model.get('account.journal')
    journal_expense, = Journal.find([
                ('code', '=', 'EXP'),
                ])
    reconcile_lines = Wizard('account.move.reconcile_lines',
            [reconcile1, reconcile2])
    assert reconcile_lines.form_state == 'writeoff'
    reconcile_lines.form.journal = journal_expense
    reconcile_lines.form.account = expense
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
