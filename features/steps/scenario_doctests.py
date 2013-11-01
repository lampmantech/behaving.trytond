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

from .support.fields import string_to_python
from .support import modules
from .support import tools

# Warning - these are hardwired from the Tryton code
from .trytond_constants import *

today = datetime.date.today()

@step('Create database')
def step_impl(context):
    context.dData = dict()

@step('Create database with pool.test set to True')
def step_impl(context):
    # This is cute
    context.execute_steps(u'''Given Create database''')
    current_config = context.oProteusConfig
    current_config.pool.test = True

# account_stock_anglo_saxon
@step('Install the test module named "{uName}"')
def step_impl(context, uName):
    from trytond.tests.test_tryton import install_module
    install_module(uName)

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

# 'Minimal Account Chart', 'Minimal Account Chart'
@step('Create a chart of accounts from template "{sTem}" with root "{sRoot}"')
def step_impl(context, sTem, sRoot):

    Company = Model.get('company.company')
    AccountTemplate = Model.get('account.account.template')
    Account = Model.get('account.account')
    Journal = Model.get('account.journal')
    FiscalYear = Model.get('account.fiscalyear')
    Party = Model.get('party.party')

    party, = Party.find([('name', '=', COMPANY_NAME)])
    company, = Company.find([('party.id', '=', party.id)])
    fiscalyear, = FiscalYear.find([('name', '=', str(today.year))])

    # FixMe: Is there a better test of telling if the
    # 'Minimal A' chart of accounts has been created?
    # MINIMAL_ACCOUNT_ROOT
    if not Account.find([('name', '=', sRoot)]):

        create_chart = Wizard('account.create_chart')
        create_chart.execute('account')

        # MINIMAL_ACCOUNT_TEMPLATE
        account_template, = AccountTemplate.find([('name', '=', sTem)])
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
@step('Create a saved instance of "{sKlass}" named "{uName}"')
def step_impl(context, sKlass, uName):

    Party = Model.get(sKlass)
    if not Party.find([('name', '=', uName)]):
        supplier = Party(name=uName)
        supplier.save()

@step('Create parties')
def step_impl(context):
    context.execute_steps(u'''Create a party named "Supplier"''')
    context.execute_steps(u'''Create a party named "Customer"''')

@step('Create a party named "{uName}"')
def step_impl(context, uName):

    Party = Model.get('party.party')
    if not Party.find([('name', '=', uName)]):
        supplier = Party(name=uName)
        supplier.save()
    assert Party.find([('name', '=', uName)])

# Customer
@step('Create a party named "{uName}" with an account_payable attribute')
def step_impl(context, uName):

    Party = Model.get('party.party')
    Company = Model.get('company.company')
    Account = Model.get('account.account')

    if not Party.find([('name', '=', uName)]):
        party, = Party.find([('name', '=', COMPANY_NAME)])
        company, = Company.find([('party.id', '=', party.id)])
        payables = Account.find([
                ('kind', '=', 'payable'),
                ('company', '=', company.id),
                ])
        assert payables
        payable = payables[0]
        customer = Party(name=uName)
        customer.account_payable = payable
        customer.save()

    assert Party.find([('name', '=', uName)])

# Accountant, Account
@step('Create a user named "{uName}" with the fields')
def step_impl(context, uName):
    # idempotent
    User = Model.get('res.user')

    if not User.find([('name', '=', uName)]):
        Group = Model.get('res.group')
        
        user = User()
        user.name = uName
        # login password
        for row in context.table:
            if row['name'] == u'group':
                # multiple allowed?
                group, = Group.find([('name', '=', row['value'])])
                user.groups.append(group)
                continue
            setattr(user, row['name'],
                    string_to_python(row['name'], row['value']))
        user.save()

        assert User.find([('name', '=', uName)])

@step('Create a calendar named "{uCalName}" owned by the user "{uUserName}"')
def step_impl(context, uCalName, uUserName):
    # idempotent
    current_config = context.oProteusConfig

    Calendar = Model.get('calendar.calendar')

    uUserName='Accountant'
    uUserLogin='accountant'
    uUserPassword='accountant'
    User = Model.get('res.user')
    oUser, = User.find([('name', '=', uUserName)])
    oAdminUser, = User.find([('name', '=', 'Administrator')])
    # calendar names must be unique
    if not Calendar.find([('name', '=', uCalName)]):

        current_config = config.set_trytond(user=uUserLogin,
                                            password=uUserPassword,
                                            config_file=current_config.config_file,
                                            database_name=current_config.database_name)
        calendar = Calendar(name=uCalName, owner=oUser)
        WriteUser = Model.get('calendar.calendar-write-res.user')
        # oAdminWriteUser = WriteUser(calendar=calendar, user=oAdminUser)
        # calendar.write_users.append(oAdminUser)
        calendar.save()

@step('Add an annual event to a calendar named "{uCalName}" owned by the user "{uUserName}" with dates')
def step_impl(context, uCalName, uUserName):
    # idempotent
    Calendar = Model.get('calendar.calendar')

    uUserName='Accountant'
    uUserLogin='accountant'
    uUserPassword='accountant'
    User = Model.get('res.user')
    oUser, = User.find([('name', '=', uUserName)])

    calendar, = Calendar.find([('name', '=', uCalName)])

    Rdate = pool.get('calendar.event.rdate')
    
    # FixMe: unfinished
    for row in context.table:
        pass

@step('Create holidays in the calendar named "{uCalName}" owned by the user named "{uUserName}" with fields')
def step_impl(context, uCalName, uUserName):
    # idempotent
    current_config = context.oProteusConfig

    Calendar = Model.get('calendar.calendar')
    # I think Calendar names are unique across all users
    calendar, = Calendar.find([('name', '=', uCalName)])
    
    uUserName='Accountant'
    uUserLogin='accountant'
    uUserPassword='accountant'
    User = Model.get('res.user')
    oUser, = User.find([('name', '=', uUserName)])
    owner_email = oUser.email

    current_config = config.set_trytond(user=uUserLogin,
                                        password=uUserPassword,
                                        config_file=current_config.config_file,
                                        database_name=current_config.database_name)


    Event = Model.get('calendar.event')
    # name date
    for row in context.table:
        uName = row['name']
        uDate = row['date']
        summary = "%s Holiday" % (uName,)
        oDate=datetime.datetime(*map(int,uDate.split('-')))
        if not Event.find([
            ('calendar.owner.email', '=', owner_email),
            ('summary', '=', summary),
            ]):
            event = Event(calendar=calendar,
                          summary=summary,
                          all_day=True,
                          classification='public',
                          transp='transparent',
                          dtstart=oDate)
            # FixMe: UserError: ('UserError', (u'You try to bypass an access rule.\n(Document type: calendar.event)', ''))
            event.save()
        assert Event.find([
            ('calendar.owner.email', '=', owner_email),
            ('summary', '=', summary),
            ])
        
# lampman_calendar = proteus.Model.get('calendar.calendar', proteus.config.TrytondConfig('test30', 'lampman', 'postgresql', config_file='/etc/trytond.conf'))(2)

    Rdate = Model.get('calendar.event.rdate')
    
