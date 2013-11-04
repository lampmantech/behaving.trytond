# -*- encoding: utf-8 -*-
"""

This is a straight cut-and-paste from
trytond_*-2.8.*/tests/scenario_*.rst
to refactor the doctests to eliminate duplication.
All the steps in this file are used by all of
the feature files that implment the doctest scenari.

The aim is to make each step idempotent, so that if
you run a step again from another feature file,
the work is not repeated, and will not error.
That's easy in the early steps, but harder farther on,
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

from .support.fields import string_to_python, sGetFeatureData, vSetFeatureData
from .support import modules
from .support.tools import *

today = datetime.date.today()

@step('Create database')
def step_impl(context):
    pass

# Warning - these are hardwired from the Tryton code
from .trytond_constants import *
@step('Set the default feature data')
def step_impl(context):
    
    assert type(context.dData['feature']) == dict
    uDefaults = u'''
    Given Set the feature data with values
     | name                                      | value                      |
     | party,company_name                        | {company_name}             |
     | account.account,minimal_account_root      | {minimal_account_root}     |
     | account.template,minimal_account_template | {minimal_account_template} |
     | user,accountant,name                      | {accountant_name}          |
     | user,accountant,login                     | {accountant_login}         |
     | user,accountant,password                  | {accountant_password}      |
     | account.template,main_receivable          | {main_receivable}          |
     | account.template,main_payable             | {main_payable}             |
     | account.template,main_revenue             | {main_revenue}             |
     | account.template,main_expense             | {main_expense}             |
     | account.template,main_cash                | {main_cash}                |
     | account.template,main_tax                 | {main_tax}                 |
'''
    uDefaults = uDefaults.format(
        company_name=COMPANY_NAME, # "B2CK"
        minimal_account_root=MINIMAL_ACCOUNT_ROOT,
        minimal_account_template=MINIMAL_ACCOUNT_TEMPLATE,
        accountant_name=ACCOUNTANT_NAME, # 'Accountant'
        accountant_login=ACCOUNTANT_USER, # 'accountant'
        accountant_password=ACCOUNTANT_PASSWORD, # 'accountant'
        # from trytond_account-3.0.0/account.xml
        main_receivable='Main Receivable',
        main_payable='Main Payable',
        main_revenue='Main Revenue',
        main_expense='Main Expense',
        main_cash='Main Cash',
        main_tax='Main Tax',
        )
    context.execute_steps(uDefaults)

@step('Set the feature data with values')
def step_impl(context):
    assert type(context.dData['feature']) == dict
    for row in context.table:
        vSetFeatureData(context, row['name'], row['value'])

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

    sCompanyName = sGetFeatureData(context, 'party,company_name')
    if not Party.find([('name', '=', sCompanyName)]):
        company_config = Wizard('company.company.config')
        company_config.execute('company')
        company = company_config.form

        party = Party(name=sCompanyName)
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
@step('Create this fiscal year without Invoicing')
def step_impl(context):
    context.execute_steps(u'''
    Given Create the fiscal year "TODAY" without Invoicing
    ''')
    
@step('Create the fiscal year "{uYear}" without Invoicing')
def step_impl(context, uYear):
    config = context.oProteusConfig

    if uYear == u'TODAY': uYear = str(today.year)
        
    Company = Model.get('company.company')
    FiscalYear = Model.get('account.fiscalyear')
    Party = Model.get('party.party')

    sCompanyName = sGetFeatureData(context, 'party,company_name')
    party, = Party.find([('name', '=', sCompanyName)])
    company, = Company.find([('party.id', '=', party.id)])
    if not FiscalYear.find([('name', '=', uYear),
                            ('company', '=', company.id),]):
        oDate = datetime.date(int(uYear), 1, 1)
        
        fiscalyear = FiscalYear(name='%s' % (uYear,))
        fiscalyear.start_date = oDate + relativedelta(month=1, day=1)
        fiscalyear.end_date = oDate + relativedelta(month=12, day=31)
        fiscalyear.company = company

        Sequence = Model.get('ir.sequence')
        post_move_sequence = Sequence(name='%s' % (uYear,),
            code='account.move', company=company)
        post_move_sequence.save()
        fiscalyear.post_move_sequence = post_move_sequence
        fiscalyear.save()

        FiscalYear.create_period([fiscalyear.id], config.context)
        assert len(fiscalyear.periods) == 12

    assert FiscalYear.find([('name', '=', str(uYear))])

@step('Create this fiscal year with Invoicing')
def step_impl(context):
    context.execute_steps(u'''
    Given Create the fiscal year "TODAY" with Invoicing
    ''')
    
@step('Create the fiscal year "{uYear}" with Invoicing')
def step_impl(context, uYear):
    config = context.oProteusConfig

    if uYear == u'TODAY': uYear = str(today.year)

    FiscalYear = Model.get('account.fiscalyear')
    Party = Model.get('party.party')

    sCompanyName = sGetFeatureData(context, 'party,company_name')
    party, = Party.find([('name', '=', sCompanyName)])
    Company = Model.get('company.company')
    company, = Company.find([('party.id', '=', party.id)])
    if not FiscalYear.find([('name', '=', str(uYear)),
                            ('company', '=', company.id),]):
        oDate = datetime.date(int(uYear), 1, 1)

        fiscalyear = FiscalYear(name='%s' % (uYear,))
        fiscalyear.start_date = oDate + relativedelta(month=1, day=1)
        fiscalyear.end_date = oDate + relativedelta(month=12, day=31)
        fiscalyear.company = company

        Sequence = Model.get('ir.sequence')
        post_move_sequence = Sequence(name='%s' % uYear,
            code='account.move', company=company)
        post_move_sequence.save()
        fiscalyear.post_move_sequence = post_move_sequence

        SequenceStrict = Model.get('ir.sequence.strict')
        invoice_sequence = SequenceStrict(name='%s' % uYear,
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

    assert FiscalYear.find([('name', '=', str(uYear))])

# 'Minimal Account Chart', 'Minimal Account Chart'
@step('Create a chart of accounts from template "{uTem}" with root "{uRoot}"')
def step_impl(context, uTem, uRoot):

    Account = Model.get('account.account')

    sCompanyName = sGetFeatureData(context, 'party,company_name')
    Party = Model.get('party.party')
    party, = Party.find([('name', '=', sCompanyName)])
    Company = Model.get('company.company')
    company, = Company.find([('party.id', '=', party.id)])

    # FixMe: Is there a better test of telling if the
    # 'Minimal A' chart of accounts has been created?
    # MINIMAL_ACCOUNT_ROOT
    if not Account.find([('name', '=', uRoot),
                         ('company', '=', company.id),]):

        create_chart = Wizard('account.create_chart')
        create_chart.execute('account')

        # MINIMAL_ACCOUNT_TEMPLATE
        AccountTemplate = Model.get('account.account.template')
        account_template, = AccountTemplate.find([('name', '=', uTem)])
        create_chart.form.account_template = account_template
        create_chart.form.company = company
        create_chart.execute('create_account')

        receivable = Account.find([
                ('kind', '=', 'receivable'),
                ('name', '=', sGetFeatureData(context, 'account.template,main_receivable')),
                ('company', '=', company.id),
                ])[0]
        payable, = Account.find([
                ('kind', '=', 'payable'),
                ('name', '=', sGetFeatureData(context, 'account.template,main_payable')),
                ('company', '=', company.id),
                ])
        revenue, = Account.find([
                ('kind', '=', 'revenue'),
                ('name', '=', sGetFeatureData(context, 'account.template,main_revenue')),
                ('company', '=', company.id),
                ])
        expense, = Account.find([
                ('kind', '=', 'expense'),
                ('name', '=', sGetFeatureData(context, 'account.template,main_expense')),
                ('company', '=', company.id),
                ])
        cash, = Account.find([
                ('kind', '=', 'other'),
                ('company', '=', company.id),
                ('name', '=', sGetFeatureData(context, 'account.template,main_cash')),
                ])
        create_chart.form.account_receivable = receivable
        create_chart.form.account_payable = payable
        create_chart.execute('create_properties')

    assert Account.find([('name', '=', uRoot)])

# party.party Supplier
@step('Create a saved instance of "{uKlass}" named "{uName}"')
def step_impl(context, uKlass, uName):
    # idempotent

    Party = Model.get(uKlass)
    if not Party.find([('name', '=', uName)]):
        instance = Party(name=uName)
        instance.save()

@step('Create an instance of "{uKlass}" named "{uName}" with fields')
def step_impl(context, uKlass, uName):
    # idempotent

    assert context.table, "please supply a table of field name and values"
    if hasattr(context.table, 'headings'):
        # if we have a real table, ensure it has 2 columns
        # otherwise, we will just fail during iteration
        assert_equal(len(context.table.headings), 2)

    Party = Model.get(uKlass)
    if not Party.find([('name', '=', uName)]):
        oInstance = Party(name=uName)
        for row in context.table:
            setattr(oInstance, row['name'],
                    string_to_python(row['name'], row['value'], Party))
        oInstance.save()

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
        sCompanyName = sGetFeatureData(context, 'party,company_name')
        party, = Party.find([('name', '=', sCompanyName)])
        company, = Company.find([('party.id', '=', party.id)])
        payables = Account.find([
                ('kind', '=', 'payable'),
                ('name', '=', sGetFeatureData(context, 'account.template,main_payable')),
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
                    string_to_python(row['name'], row['value'], User))
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
        
# accountant_calendar = proteus.Model.get('calendar.calendar', proteus.config.TrytondConfig('test30', 'accountant', 'postgresql', config_file='/etc/trytond.conf'))(2)

    Rdate = Model.get('calendar.event.rdate')
