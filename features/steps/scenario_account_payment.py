# -*- mode: python; py-indent-offset: 4; coding: utf-8-unix; encoding: utf-8 -*-
"""
Payment Scenario
"""

from behave import *
import proteus

import datetime
from dateutil.relativedelta import relativedelta
from decimal import Decimal

TODAY = datetime.date.today()


@step('T/AP Create a PaymentJournal named "{uName}" of type "{uType}"')
def step_impl(context, uName, uType):
    """
    T/AP Create a PaymentJournal named "Manual" of type "manual"
    """
    PaymentJournal = proteus.Model.get('account.payment.journal')
    if not PaymentJournal.find([('name', '=', uName)]):
        payment_journal = PaymentJournal(name=uName,
                                         process_method=uType)
        payment_journal.save()
    payment_journal, = PaymentJournal.find([('name', '=', uName)])

@step('T/AP Unfinished')
def step_impl(context):

    config = context.oProteusConfig

    Company = proteus.Model.get('company.company')
    FiscalYear = proteus.Model.get('account.fiscalyear')
    Party = proteus.Model.get('party.party')

    sCompanyName = sGetFeatureData(context, 'party,company_name')
    party, = Party.find([('name', '=', sCompanyName)])
    company, = Company.find([('party.id', '=', party.id)])

#@step('T/AP Create payable move')
#def step_impl(context):

    Move = proteus.Model.get('account.move')
    Journal = proteus.proteus.Model.get('account.journal')
    expense, = Journal.find([('code', '=', 'EXP')])

    move = Move()
    move.journal = expense

    Account = proteus.Model.get('account.account')
    payable, = Account.find([
                ('kind', '=', 'payable'),
                ('company', '=', company.id),
                ])
    expense, = Account.find([
                ('kind', '=', 'expense'),
                ('company', '=', company.id),
                ])

    supplier, = Party.find([('name', '=', 'Supplier'),])

    line = move.lines.new(account=payable, party=supplier,
            credit=Decimal(50))
    line = move.lines.new(account=expense, debit=Decimal(50))
    move.click('post')

#@step('T/AP Partially pay line')
#def step_impl(context):
    PaymentJournal = proteus.Model.get('account.payment.journal')
    payment_journal, = PaymentJournal.find([('name', '=', 'Manual')])

    Payment = proteus.Model.get('account.payment')
    line, = [l for l in move.lines if l.account == payable]
    pay_line = proteus.Wizard('account.move.line.pay', [line])
    pay_line.form.journal = payment_journal
    pay_line.execute('pay')
    payment, = Payment.find()
    assert payment.party == supplier
    assert payment.amount == Decimal(50)
    payment.amount = Decimal(20)
    payment.click('approve')
    assert payment.state == u'approved'
    process_payment = proteus.Wizard('account.payment.process', [payment])
    process_payment.execute('process')
    payment.reload()
    assert payment.state == u'processing'
    line.reload()
    assert line.payment_amount == Decimal(30)

#@step('T/AP Partially fail to pay the remaining')
#def step_impl(context):

    pay_line = proteus.Wizard('account.move.line.pay', [line])
    pay_line.form.journal = payment_journal
    pay_line.execute('pay')
    payment, = Payment.find([('state', '=', 'draft')])
    assert payment.amount == Decimal(30)
    payment.click('approve')
    process_payment = proteus.Wizard('account.payment.process', [payment])
    process_payment.execute('process')
    line.reload()
    assert line.payment_amount == Decimal(0)
    payment.reload()
    payment.click('fail')
    assert payment.state == u'failed'
    line.reload()
    assert line.payment_amount == Decimal(30)
