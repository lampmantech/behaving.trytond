# -*- mode: python; py-indent-offset: 4; coding: utf-8-unix; encoding: utf-8 -*-
"""

=========================
Invoice Supplier Scenario
=========================

This is a straight cut-and-paste from
trytond_account_invoice-3.0.0/tests/scenario_invoice_supplier.rst

It should be improved to be more like a Behave BDD.
"""

from behave import *
import proteus

import time
import datetime
from decimal import Decimal
from operator import attrgetter

from .support.fields import string_to_python, sGetFeatureData, vSetFeatureData
from .support import modules

TODAY = datetime.date.today()

# Buy the Services Bought, 10% Sales Tax
@step('TS/AIS Post the invoice with description "{uDescription}" and assert the taxes named "{uTaxName}" are right')
def step_impl(context, uDescription, uTaxName):
    current_config = context.oProteusConfig

    Party = proteus.Model.get('party.party')
    sCompanyName = sGetFeatureData(context, 'party,company_name')
    party, = Party.find([('name', '=', sCompanyName)])
    Company = proteus.Model.get('company.company')
    company, = Company.find([('party.id', '=', party.id)])

    Invoice = proteus.Model.get('account.invoice')
    invoice, = Invoice.find(['description', '=', uDescription])

    assert invoice.untaxed_amount == Decimal(110)
    assert invoice.tax_amount == Decimal(10)
    assert invoice.total_amount == Decimal(120)
    Invoice.post([invoice.id], current_config.context)

    invoice.reload()
    assert invoice.state ==u'posted'
    assert invoice.untaxed_amount == Decimal(110)
    assert invoice.tax_amount == Decimal(10)
    assert invoice.total_amount == Decimal(120)

    Account = proteus.Model.get('account.account')
    payable, = Account.find([
        ('kind', '=', 'payable'),
        ('name', '=', sGetFeatureData(context, 'account.template,main_payable')),
        ('company', '=', company.id),
        ])
    payable.reload()
    assert (payable.debit, payable.credit) == \
        (Decimal(0), Decimal(120))

    expense, = Account.find([
        ('kind', '=', 'expense'),
        ('name', '=', sGetFeatureData(context, 'account.template,main_expense')),
        ('company', '=', company.id),
        ])
    expense.reload()
    assert (expense.debit, expense.credit) == \
        (Decimal(110), Decimal(0))
    # failing here expense.debit, expense.credit
    account_tax, = Account.find([
        ('kind', '=', 'other'),
        ('name', '=', sGetFeatureData(context, 'account.template,main_tax')),
        ('company', '=', company.id),
        ])
    account_tax.reload()
    assert (account_tax.debit, account_tax.credit) == \
           (Decimal(10), Decimal(0))

    Tax = proteus.Model.get('account.tax')
    tax, = Tax.find([('name', '=', uTaxName)])
    invoice_base_code = tax.invoice_base_code
    invoice_base_code.reload()
    assert invoice_base_code.sum == Decimal(100)

    invoice_tax_code = tax.invoice_tax_code
    invoice_tax_code.reload()
    assert invoice_tax_code.sum == Decimal(10)

    credit_note_base_code = tax.credit_note_base_code
    credit_note_base_code.reload()
    assert credit_note_base_code.sum == Decimal(0)

    credit_note_tax_code = tax.credit_note_tax_code
    credit_note_tax_code.reload()
    assert credit_note_tax_code.sum == Decimal(0)

# Buy the Services Bought
@step('TS/AIS Create a credit note for the invoice with description "{uDescription}" and assert the amounts')
def step_impl(context, uDescription):
    """
    Create a credit note for the invoice with description "{uDescription}"
    and assert the amounts for the credit note equal the invoice amounts.
    Not idempotent.
    """
    current_config = context.oProteusConfig

    Invoice = proteus.Model.get('account.invoice')
    # company.id?
    invoice, = Invoice.find(['description', '=', uDescription])

    credit = proteus.Wizard('account.invoice.credit', [invoice])
    credit.form.with_refund = False
    credit.execute('credit')

    credit_note, = Invoice.find([('type', '=', 'in_credit_note')])
    assert credit_note.state == u'draft'
    assert credit_note.untaxed_amount == invoice.untaxed_amount
    assert credit_note.tax_amount == invoice.tax_amount
    assert credit_note.total_amount == invoice.total_amount
