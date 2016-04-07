# -*- mode: python; py-indent-offset: 4; coding: utf-8-unix; encoding: utf-8 -*-
"""
This is a straight cut-and-paste from
trytond_account_statement-3.6.0/tests/scenario_account_statement.rst

Unfinished.
"""

from behave import *
import proteus

import datetime
from dateutil.relativedelta import relativedelta
from decimal import Decimal

from proteus import config, Model, Report
from trytond.exceptions import UserError, UserWarning

TODAY = datetime.date.today()

    
@step('T/SASt Scenario Account Statement')
def step_impl(context):
    config = context.oProteusConfig
    
    Party = proteus.Model.get('party.party')
    Company = proteus.Model.get('company.company')

    sCompanyName = sGetFeatureData(context, 'party,company_name')
    party, = Party.find([('name', '=', sCompanyName)])
    company, = Company.find([('party.id', '=', party.id)])

    FiscalYear = proteus.Model.get('account.fiscalyear')
    fiscalyear, = FiscalYear.find([('name', '=', str(TODAY.year))])
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
    payable, = Account.find([
                ('kind', '=', 'payable'),
                ('company', '=', company.id),
                ('name', '=', sGetFeatureData(context, 'account.template,main_payable')),
                ])
    expense, = Account.find([
        ('kind', '=', 'expense'),
        ('name', '=', sGetFeatureData(context, 'account.template,main_expense')),
        ('company', '=', company.id),
        ])
    cash, = Account.find([
        #? cash or other?
        ('kind', '=', 'other'),
        ('company', '=', company.id),
        ('name', '=', sGetFeatureData(context, 'account.template,main_cash')),
        ])
    
    PaymentTerm = proteus.Model.get('account.invoice.payment_term')
    payment_term, = PaymentTerm.find([('name', '=', "Term")])

# Create 2 customer invoices::

    customer, = Party.find([('name', '=', 'Customer')])

    Invoice = Model.get('account.invoice')
    customer_invoice1 = Invoice(type='out_invoice')
    customer_invoice1.party = customer
    customer_invoice1.payment_term = payment_term
    
    invoice_line = customer_invoice1.lines.new()
    invoice_line.quantity = 1
    invoice_line.unit_price = Decimal('100')
    invoice_line.account = revenue
    invoice_line.description = 'Test'
    
    customer_invoice1.click('post')
    assert customer_invoice1.state == u'posted'

    customer_invoice2 = Invoice(type='out_invoice')
    customer_invoice2.party = customer
    customer_invoice2.payment_term = payment_term
    invoice_line = customer_invoice2.lines.new()
    invoice_line.quantity = 1
    invoice_line.unit_price = Decimal('150')
    invoice_line.account = revenue
    invoice_line.description = 'Test'
    customer_invoice2.click('post')
    assert customer_invoice2.state == u'posted'

# Create 1 customer credit note::

    customer_credit_note = Invoice(type='out_credit_note')
    customer_credit_note.party = customer
    customer_credit_note.payment_term = payment_term
    invoice_line = customer_credit_note.lines.new()
    invoice_line.quantity = 1
    invoice_line.unit_price = Decimal('50')
    invoice_line.account = revenue
    invoice_line.description = 'Test'
    customer_credit_note.click('post')
    assert customer_credit_note.state == u'posted'

# Create 1 supplier invoices::

    supplier, = Party.find([('name', '=', 'Supplier')])
    
    supplier_invoice = Invoice(type='in_invoice')
    supplier_invoice.party = supplier
    supplier_invoice.payment_term = payment_term
    invoice_line = supplier_invoice.lines.new()
    invoice_line.quantity = 1
    invoice_line.unit_price = Decimal('50')
    invoice_line.account = expense
    invoice_line.description = 'Test'
    supplier_invoice.invoice_date = TODAY
    supplier_invoice.click('post')
    assert supplier_invoice.state == u'posted'

# Create statement::

    StatementJournal = Model.get('account.statement.journal')
    Statement = Model.get('account.statement')
    StatementLine = Model.get('account.statement.line')
    Sequence = Model.get('ir.sequence')

    sequence = Sequence(name='Statement Sequence',
            code='account.journal',
            company=company,
        )
    sequence.save()
    
    AccountJournal = Model.get('account.journal')
    account_journal = AccountJournal(name='Statement Journal',
            type='statement',
            credit_account=cash,
            debit_account=cash,
            sequence=sequence,
        )
    account_journal.save()

    statement_journal = StatementJournal(name='Test',
            journal=account_journal,
            validation='balance',
        )
    statement_journal.save()

    statement = Statement(name='Test Statement',
            journal=statement_journal,
            start_balance=Decimal('0'),
            end_balance=Decimal('80'),
        )

# Received 180 from customer::

    statement_line = StatementLine()
    statement.lines.append(statement_line)
    statement_line.date = TODAY
    statement_line.amount = Decimal('180')
    statement_line.party = customer
    assert statement_line.account == receivable
    
    statement_line.invoice = customer_invoice1
    assert statement_line.amount == Decimal('100.00')
    statement_line = statement.lines[-1]
    assert statement_line.amount == Decimal('80.00')
    assert statement_line.party == customer
    assert statement_line.account == receivable
    statement_line.invoice = customer_invoice2
    assert statement_line.amount ==  Decimal('80.00')

# Paid 50 to customer::

    statement_line = StatementLine()
    statement.lines.append(statement_line)
    statement_line.date = TODAY
    statement_line.amount = Decimal('-50')
    statement_line.party = customer
    statement_line.account = receivable
    statement_line.invoice = customer_credit_note

# Paid 50 to supplier::

    statement_line = StatementLine()
    statement.lines.append(statement_line)
    statement_line.date = TODAY
    statement_line.amount = Decimal('-60')
    statement_line.party = supplier
    assert statement_line.account == payable
    statement_line.invoice = supplier_invoice
    assert statement_line.amount == Decimal('-50.00')
    statement_line = statement.lines.pop()
    assert statement_line.amount == Decimal('-10.00')

    statement.save()

# Validate statement::

    statement.click('validate_statement')
    assert statement.state == u'validated'

# Test invoice state::

    customer_invoice1.reload()
    assert customer_invoice1.state == u'paid'
    customer_invoice2.reload()
    assert customer_invoice2.state == u'posted'
    assert customer_invoice2.amount_to_pay == Decimal('70.00')
    customer_credit_note.reload()
    assert customer_credit_note.state == u'paid'
    supplier_invoice.reload()
    assert supplier_invoice.state == u'paid'

# Test statement report::

    report = Report('account.statement')
    _ = report.execute([statement], {})

# Let's test the negative amount version of the supplier/customer invoices::

    customer_invoice3 = Invoice(type='out_invoice')
    customer_invoice3.party = customer
    customer_invoice3.payment_term = payment_term
    invoice_line = customer_invoice3.lines.new()
    invoice_line.quantity = 1
    invoice_line.unit_price = Decimal('-120')
    invoice_line.account = revenue
    invoice_line.description = 'Test'
    customer_invoice3.click('post')
    assert customer_invoice3.state == u'posted'

    supplier_invoice2 = Invoice(type='in_invoice')
    supplier_invoice2.party = supplier
    supplier_invoice2.payment_term = payment_term
    invoice_line = supplier_invoice2.lines.new()
    invoice_line.quantity = 1
    invoice_line.unit_price = Decimal('-40')
    invoice_line.account = expense
    invoice_line.description = 'Test'
    supplier_invoice2.invoice_date = TODAY
    supplier_invoice2.click('post')
    assert supplier_invoice2.state == u'posted'

    statement = Statement(name='test negative',
            journal=statement_journal,
            end_balance=Decimal('0'),
        )

    statement_line = StatementLine()
    statement.lines.append(statement_line)
    statement_line.date = TODAY
    statement_line.party = customer
    statement_line.account = receivable
    statement_line.amount = Decimal(-120)
    statement_line.invoice = customer_invoice3
    assert statement_line.invoice.id == customer_invoice3.id

    statement_line = StatementLine()
    statement.lines.append(statement_line)
    statement_line.date = TODAY
    statement_line.party = supplier
    statement_line.account = payable
    statement_line.amount = Decimal(50)
    statement_line.invoice = supplier_invoice2
    assert statement_line.amount == Decimal('40.00')
    assert len(statement.lines) == 3
    assert statement.lines[-1].amount == Decimal('10.00')

# Testing the use of an invoice in multiple statements::

    customer_invoice4 = Invoice(type='out_invoice')
    customer_invoice4.party = customer
    customer_invoice4.payment_term = payment_term
    invoice_line = customer_invoice4.lines.new()
    invoice_line.quantity = 1
    invoice_line.unit_price = Decimal('300')
    invoice_line.account = revenue
    invoice_line.description = 'Test'
    customer_invoice4.click('post')
    assert customer_invoice4.state == u'posted'

    statement1 = Statement(name='1', journal=statement_journal)
    statement1.end_balance = Decimal(380)
    statement_line = statement1.lines.new()
    statement_line.date = TODAY
    statement_line.party = customer
    statement_line.account = receivable
    statement_line.amount = Decimal(300)
    statement_line.invoice = customer_invoice4
    statement1.save()

    statement2 = Statement(name='2', journal=statement_journal)
    statement2.end_balance = Decimal(680)
    statement_line = statement2.lines.new()
    statement_line.date = TODAY
    statement_line.party = customer
    statement_line.account = receivable
    statement_line.amount = Decimal(300)
    statement_line.invoice = customer_invoice4
    try:
        # in the doctest, this is not expecting a UserWarning,
        # but one is being raised
        statement2.save()
    except UserWarning:
        pass
    try:
        statement1.click('validate_statement')
    except UserWarning:
        pass
    statement2.reload()
    
    Model.get('res.user.warning')(user=config.user,
            name=str(statement2.lines[0].id), always=True).save()
    try:
        statement1.click('validate_statement')
    except UserWarning:
        pass
    assert statement1.state ==  u'validated'

    statement1.reload()
    assert bool(statement1.lines[0].invoice)
    statement2.reload()
    assert bool(statement2.lines[0].invoice) == False

#@step('T/SASt Testing balance validation')
#def step_impl(context):

    Statement = Model.get('account.statement')
    StatementJournal = Model.get('account.statement.journal')
    journal_balance = StatementJournal(name='Balance',
            journal=account_journal,
            validation='balance',
            )
    journal_balance.save()

    statement = Statement(name='balance')
    statement.journal = journal_balance
    statement.start_balance = Decimal('50.00')
    statement.end_balance = Decimal('150.00')
    line = statement.lines.new()
    line.date = TODAY
    line.amount = Decimal('60.00')
    line.account = receivable
    line.party = customer
    try:
        statement.click('validate_statement')
    except UserError:
        pass

    second_line = statement.lines.new()
    second_line.date = TODAY
    second_line.amount = Decimal('40.00')
    second_line.account = receivable
    second_line.party = customer
    statement.click('validate_statement')

#@step('T/SASt Testing amount validation')
#def step_impl(context):

    Statement = Model.get('account.statement')
    StatementJournal = Model.get('account.statement.journal')
    journal_amount = StatementJournal(name='Amount',
            journal=account_journal,
            validation='amount',
            )
    journal_amount.save()

    statement = Statement(name='amount')
    statement.journal = journal_amount
    statement.total_amount = Decimal('80.00')
    line = statement.lines.new()
    line.date = TODAY
    line.amount = Decimal('50.00')
    line.account = receivable
    line.party = customer
    try:
       statement.click('validate_statement')  # doctest: +IGNORE_EXCEPTION_DETAIL
    except UserError:
        pass

    second_line = statement.lines.new()
    second_line.date = TODAY
    second_line.amount = Decimal('30.00')
    second_line.account = receivable
    second_line.party = customer
    statement.click('validate_statement')

#@step('T/SASt Test number of lines validation')
#def step_impl(context):

    Statement = Model.get('account.statement')
    StatementJournal = Model.get('account.statement.journal')
    journal_number = StatementJournal(name='Number',
            journal=account_journal,
            validation='number_of_lines',
            )
    journal_number.save()

    statement = Statement(name='number')
    statement.journal = journal_number
    statement.number_of_lines = 2
    line = statement.lines.new()
    line.date = TODAY
    line.amount = Decimal('50.00')
    line.account = receivable
    line.party = customer
    try:
        statement.click('validate_statement')
    except UserError:
        pass

    second_line = statement.lines.new()
    second_line.date = TODAY
    second_line.amount = Decimal('10.00')
    second_line.account = receivable
    second_line.party = customer
    statement.click('validate_statement')
