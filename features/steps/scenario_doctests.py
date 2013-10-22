# -*- encoding: utf-8 -*-
"""

This is a straight cut-and-paste from
trytond_*-2.8.*/tests/scenario_*.rst
to refactor the doctests to eliminate duplication.
All the steps in this file are used by all of
the feature files that implment the doctest scenarios.

The aim is to make each step idempotent, so that if
you run a step again from another feature file,
the work is not repeated, and will not error.
That's easy in th early steps, but harder farther on,
so some feature files will need to be run on their own.
Most steps are commented as either idempotent or FixMe.

It should be improved to be more like a Behave BDD.
"""

from behave import *
from proteus import Model, Wizard

import datetime
from dateutil.relativedelta import relativedelta
from decimal import Decimal
from proteus import config, Model, Wizard
from .support import modules

# Warning - these are hardwired from the Tryton code
from .trytond_constants import *

today = datetime.date.today()

@step('Create database')
def step_impl(context):
    context.dData = dict()

@step('Create database with pool.test set to True')
def step_impl(context):
    # This is cute
    context.execute_steps(u'''
    Given Create database
    ''')
    current_config = context.oProteusConfig
    current_config.pool.test = True

# account_stock_anglo_saxon
@step('Install the test module named "{sName}"')
def step_impl(context, sName):
    from trytond.tests.test_tryton import install_module
    install_module(sName)

#unused
@step('Install account')
def step_impl(context):
    context.execute_steps(u'''Given Ensure that the "account" module is loaded''')

@step('Create the Company with default COMPANY_NAME and Currency code "{sCode}"')
def step_impl(context, sCode):

    Company = Model.get('company.company')
    Party = Model.get('party.party')

    if not Party.find([('name', '=', COMPANY_NAME)]):
        company_config = Wizard('company.company.config')
        company_config.execute('company')
        company = company_config.form

        party = Party(name=COMPANY_NAME)
        party.save()
        company.party = party

        Currency = Model.get('currency.currency')
        currencies = Currency.find([('code', '=', sCode)])
        if not currencies:
            if sCode == 'EUR':
                currency = Currency(name='EUR', symbol=u'€', code='EUR',
                    rounding=Decimal('0.01'), mon_grouping='[3, 3, 0]',
                    mon_decimal_point=',')
            elif sCode == 'GBP':
                currency = Currency(name='GBP', symbol=u'£', code='GBP',
                    rounding=Decimal('0.01'), mon_grouping='[3, 3, 0]',
                    mon_decimal_point='.')
            elif sCode == 'USD':
                currency = Currency(name='USD', symbol=u'$', code='USD',
                    rounding=Decimal('0.01'), mon_grouping='[3, 3, 0]',
                    mon_decimal_point='.')
            else:
                assert code in ['EUR', 'GBP', 'USD'], \
                       "Unsupported currency code: %s" % (sCode,)
            currency.save()

            CurrencyRate = Model.get('currency.currency.rate')
            CurrencyRate(date=today + relativedelta(month=1, day=1),
                rate=Decimal('1.0'), currency=currency).save()
        else:
            currency, = currencies
        company.currency = currency
        company_config.execute('add')

    assert Company.find()

@step('Reload the default User preferences into the context')
def step_impl(context):
    config = context.oProteusConfig

    User = Model.get('res.user')
    config._context = User.get_preferences(True, config.context)

@step('Create this fiscal year')
def step_impl(context):
    config = context.oProteusConfig

    Company = Model.get('company.company')
    FiscalYear = Model.get('account.fiscalyear')
    SequenceStrict = Model.get('ir.sequence.strict')
    Party = Model.get('party.party')

    party, = Party.find([('name', '=', COMPANY_NAME)])
    company, = Company.find([('party.id', '=', party.id)])
    if not FiscalYear.find([('name', '=', str(today.year))]):
        fiscalyear = FiscalYear(name='%s' % today.year)
        fiscalyear.start_date = today + relativedelta(month=1, day=1)
        fiscalyear.end_date = today + relativedelta(month=12, day=31)
        fiscalyear.company = company

        Sequence = Model.get('ir.sequence')
        post_move_sequence = Sequence(name='%s' % today.year,
            code='account.move', company=company)
        post_move_sequence.save()
        fiscalyear.post_move_sequence = post_move_sequence
        fiscalyear.save()

        FiscalYear.create_period([fiscalyear.id], config.context)
        assert len(fiscalyear.periods) == 12

    assert FiscalYear.find([('name', '=', str(today.year))])

@step('Create this fiscal year with Invoicing')
def step_impl(context):
    config = context.oProteusConfig

    Company = Model.get('company.company')
    FiscalYear = Model.get('account.fiscalyear')
    Sequence = Model.get('ir.sequence')
    Party = Model.get('party.party')

    party, = Party.find([('name', '=', COMPANY_NAME)])
    company, = Company.find([('party.id', '=', party.id)])
    if not FiscalYear.find([('name', '=', str(today.year))]):
        fiscalyear = FiscalYear(name='%s' % today.year)
        fiscalyear.start_date = today + relativedelta(month=1, day=1)
        fiscalyear.end_date = today + relativedelta(month=12, day=31)
        fiscalyear.company = company

        Sequence = Model.get('ir.sequence')
        post_move_sequence = Sequence(name='%s' % today.year,
            code='account.move', company=company)
        post_move_sequence.save()
        fiscalyear.post_move_sequence = post_move_sequence

        SequenceStrict = Model.get('ir.sequence.strict')
        invoice_sequence = SequenceStrict(name='%s' % today.year,
                                          code='account.invoice',
                                          company=company)
        invoice_sequence.save()
        fiscalyear.out_invoice_sequence = invoice_sequence
        fiscalyear.in_invoice_sequence = invoice_sequence
        fiscalyear.out_credit_note_sequence = invoice_sequence
        fiscalyear.in_credit_note_sequence = invoice_sequence
        fiscalyear.save()

        FiscalYear.create_period([fiscalyear.id], config.context)
        assert len(fiscalyear.periods) == 12

    assert FiscalYear.find([('name', '=', str(today.year))])

@step('Create a chart of accounts from the MINIMAL_ACCOUNT_PARENT')
def step_impl(context):

    Company = Model.get('company.company')
    AccountTemplate = Model.get('account.account.template')
    Account = Model.get('account.account')
    Journal = Model.get('account.journal')
    FiscalYear = Model.get('account.fiscalyear')
    Party = Model.get('party.party')

    party, = Party.find([('name', '=', COMPANY_NAME)])
    company, = Company.find([('party.id', '=', party.id)])
    fiscalyear, = FiscalYear.find([('name', '=', str(today.year))])
    account_template, = AccountTemplate.find([('parent', '=', MINIMAL_ACCOUNT_PARENT)])

    # FixMe: Is there a better test of telling if the
    # 'Minimal A' chart of accounts has been created?
    if not Account.find([('name', '=', MINIMAL_ACCOUNT_ROOT)]):

        create_chart = Wizard('account.create_chart')
        create_chart.execute('account')

        create_chart.form.account_template = account_template
        create_chart.form.company = company
        create_chart.execute('create_account')

        receivable = Account.find([
                ('kind', '=', 'receivable'),
                ('company', '=', company.id),
                ])[0]
        payable, = Account.find([
                ('kind', '=', 'payable'),
                ('company', '=', company.id),
                ])
        revenue, = Account.find([
                ('kind', '=', 'revenue'),
                ('company', '=', company.id),
                ])
        expense, = Account.find([
                ('kind', '=', 'expense'),
                ('company', '=', company.id),
                ])
        cash, = Account.find([
                ('kind', '=', 'other'),
                ('company', '=', company.id),
                ('name', '=', 'Main Cash'),
                ])
        create_chart.form.account_receivable = receivable
        create_chart.form.account_payable = payable
        create_chart.execute('create_properties')

    assert Account.find([('name', '=', MINIMAL_ACCOUNT_ROOT)])
    if 'account_stock_anglo_saxon' in modules.lInstalledModules():
        # in account_stock_anglo_saxon/account.xml
        assert Account.find([
            ('kind', '=', 'other'),
            ('company', '=', company.id),
            ('name', '=', 'COGS'),
            ])
# party.party Supplier
@step('Create a saved instance of "{sKlass}" named "{sName}"')
def step_impl(context, sKlass, sName):

    Party = Model.get(sKlass)
    if not Party.find([('name', '=', sName)]):
        supplier = Party(name=sName)
        supplier.save()

@step('Create parties')
def step_impl(context):

    Party = Model.get('party.party')
    if not Party.find([('name', '=', 'Supplier')]):
        supplier = Party(name='Supplier')
        supplier.save()
    if not Party.find([('name', '=', 'Customer')]):
        customer = Party(name='Customer')
        customer.save()

