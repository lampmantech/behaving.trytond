# -*- encoding: utf-8 -*-
"""

This is a straight cut-and-paste from
trytond_*-2.8.*/tests/scenario_*.rst
to refactor the doctests to eliminate duplication.
All the steps in this file are used by all of
the feature files that implment the doctest scenarios.

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

@step('Create database')
def step_impl(context):
    config = context.oProteusConfig

@step('Install account')
def step_impl(context):
    config = context.oProteusConfig
    Module = Model.get('ir.module.module')
    modules = Module.find([
        ('name', '=', 'account'),
        ('state', '!=', 'installed'),
        ])
    if len(modules):
        Module.install([x.id for x in modules], config.context)
    modules = [x.name for x in Module.find([('state', '=', 'to install')])]
    if len(modules):
        Wizard('ir.module.module.install_upgrade').execute('upgrade')

@step('Create company')
def step_impl(context):
    
    Currency = Model.get('currency.currency')
    CurrencyRate = Model.get('currency.currency.rate')
    Company = Model.get('company.company')
    Party = Model.get('party.party')

    if not Company.find():
        company_config = Wizard('company.company.config')
        company_config.execute('company')
        company = company_config.form

        party = Party(name=COMPANY_NAME)
        party.save()
        company.party = party
        currencies = Currency.find([('code', '=', 'EUR')])
        if not currencies:
            currency = Currency(name='Euro', symbol=u'€', code='EUR',
                rounding=Decimal('0.01'), mon_grouping='[3, 3, 0]',
                mon_decimal_point=',')
            currency.save()
            CurrencyRate(date=today + relativedelta(month=1, day=1),
                rate=Decimal('1.0'), currency=currency).save()
        else:
            currency, = currencies
        company.currency = currency
        company_config.execute('add')
        
    assert Company.find()

@step('Reload the context')
def step_impl(context):
    config = context.oProteusConfig
    
    User = Model.get('res.user')
    config._context = User.get_preferences(True, config.context)

@step('Create fiscal year')
def step_impl(context):
    config = context.oProteusConfig
    
    Company = Model.get('company.company')
    FiscalYear = Model.get('account.fiscalyear')
    Sequence = Model.get('ir.sequence')
    SequenceStrict = Model.get('ir.sequence.strict')

    company, = Company.find()
    if not FiscalYear.find([('name', '=', str(today.year))]):
        fiscalyear = FiscalYear(name='%s' % today.year)
        fiscalyear.start_date = today + relativedelta(month=1, day=1)
        fiscalyear.end_date = today + relativedelta(month=12, day=31)
        fiscalyear.company = company
        post_move_sequence = Sequence(name='%s' % today.year,
            code='account.move', company=company)
        post_move_sequence.save()
        fiscalyear.post_move_sequence = post_move_sequence
        fiscalyear.save()
        FiscalYear.create_period([fiscalyear.id], config.context)

        assert FiscalYear.find([('name', '=', str(today.year))])
        assert len(fiscalyear.periods) == 12
        
@step('Create chart of accounts')
def step_impl(context):

    Company = Model.get('company.company')
    AccountTemplate = Model.get('account.account.template')
    Account = Model.get('account.account')
    Journal = Model.get('account.journal')
    FiscalYear = Model.get('account.fiscalyear')

    company, = Company.find()
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

