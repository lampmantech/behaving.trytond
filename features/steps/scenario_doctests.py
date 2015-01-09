# -*- encoding: utf-8 -*-
"""

This is a straight cut-and-paste from
trytond_*-2.8.*/tests/scenario_*.rst
to refactor the doctests to eliminate duplication.
All the steps in this file are used by all of
the feature files that impelment the doctest scenari.

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
    """
    You can use this step to define a set of default feature data
    that will be available using the vSetFeatureData and vSetFeatureData
    functions to pass data between steps. The default data is pulled
    from the Tryton code, but you can override this for your own
    production Chart of Accounts, users...
    """
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
    """
    You can use this step to define a set of default feature data
    that will be available using the vSetFeatureData and vSetFeatureData
    functions to pass data between steps. It expects a |name|value| table.
    """
    assert type(context.dData['feature']) == dict
    for row in context.table:
        vSetFeatureData(context, row['name'], row['value'])

@step('Create database with pool.test set to True')
def step_impl(context):
    # FixMe: what does this do?
    """
    Sets pool.test set to True
    """
    # This is cute
    current_config = context.oProteusConfig
    current_config.pool.test = True

# account_stock_anglo_saxon
@step('Install the test module named "{uName}"')
def step_impl(context, uName):
    # FixMe: what does this do?
    """
    Installs a module using trytond.tests.test_tryton.install_module
    in case thats different to installing a module.
    """
    from trytond.tests.test_tryton import install_module
    install_module(uName)

#unused
@step('Install account')
def step_impl(context):
    context.execute_steps(u'''Given Ensure that the "account" module is loaded''')

@step('Create the Company with default COMPANY_NAME and Currency code "{uCode}"')
def step_impl(context, uCode):

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
        currencies = Currency.find([('code', '=', uCode)])
        if not currencies:
            if uCode == 'EUR':
                currency = Currency(name='EUR', symbol=u'€', code='EUR',
                                    digits=2,
                                    rounding=Decimal('0.01'),
                                    mon_grouping='[3, 3, 0]',
                                    mon_decimal_point='.')
            elif uCode == 'GBP':
                currency = Currency(name='GBP', symbol=u'£', code='GBP',
                                    digits=2,
                                    rounding=Decimal('0.01'),
                                    mon_grouping='[3, 3, 0]',
                                    mon_decimal_point='.')
            elif uCode == 'USD':
                currency = Currency(name='USD', symbol=u'$', code='USD',
                                    digits=2,
                                    rounding=Decimal('0.01'),
                                    mon_grouping='[3, 3, 0]',
                                    mon_decimal_point='.')
            elif uCode == 'CAD':
                currency = Currency(name='CAD', symbol=u'$', code='CAD',
                                    digits=2,
                                    rounding=Decimal('0.01'),
                                    mon_grouping='[3, 3, 0]',
                                    mon_decimal_point='.')
            else:
                assert code in ['EUR', 'GBP', 'USD', 'CAD'], \
                       "Unsupported currency code: %s" % (uCode,)
            currency.save()

            CurrencyRate = Model.get('currency.currency.rate')
            # the beginning of computer time
            CurrencyRate(date=datetime.date(year=1970, month=1, day=1),
                         rate=Decimal('1.0'),
                         currency=currency).save()
        else:
            currency, = currencies
        company.currency = currency
        company_config.execute('add')

    assert Company.find()

@step('Create the currency with Currency code "{uCode}"')
def step_impl(context, uCode):
    """
    Create the currency with the given Currency code.
    You'll need to do this before you use any other currencies
    than the company's base currency.
    """
    Company = Model.get('company.company')
    Party = Model.get('party.party')

    sCompanyName = sGetFeatureData(context, 'party,company_name')
    party, = Party.find([('name', '=', sCompanyName)])
    company, = Company.find([('party.id', '=', party.id)])
    
    Currency = Model.get('currency.currency')
    currencies = Currency.find([('code', '=', uCode)])
    if not currencies:
        if uCode == 'EUR':
            currency = Currency(name='EUR', symbol=u'€', code='EUR',
                rounding=Decimal('0.01'), mon_grouping='[3, 3, 0]',
                mon_decimal_point=',')
        elif uCode == 'GBP':
            currency = Currency(name='GBP', symbol=u'£', code='GBP',
                rounding=Decimal('0.01'), mon_grouping='[3, 3, 0]',
                mon_decimal_point='.')
        elif uCode == 'USD':
            currency = Currency(name='USD', symbol=u'$', code='USD',
                rounding=Decimal('0.01'), mon_grouping='[3, 3, 0]',
                mon_decimal_point='.')
        elif uCode == 'CAD':
            currency = Currency(name='CAD', symbol=u'$', code='CAD',
                rounding=Decimal('0.01'), mon_grouping='[3, 3, 0]',
                mon_decimal_point='.')
        else:
            assert code in ['EUR', 'GBP', 'USD', 'CAD'], \
                   "Unsupported currency code: %s" % (uCode,)
        currency.save()


    assert Currency.find([('code', '=', uCode)])

@step('Reload the default User preferences into the context')
def step_impl(context):
    # FixMe: what does this do?
    """
    Reload the default User get_preferences.
    """
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
    """
    Creates a fiscal year 'uYear' with a non-Strict move_sequence.
    Create the company first before creating fiscal years.
    """
    
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
    """
    Creates a fiscal year 'uYear' with a non-Strict move_sequence
    and a Strict invoice_sequence for Invoices.
    Create the company first.
    """
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
    """
    Create a chart of accounts from template "{uTem}" 
    with root account "{uRoot}".
    Before you do this, set the feature data for:
    * account.template,main_receivable
    * account.template,main_payable
    * account.template,main_revenue
    * account.template,main_expense
    * account.template,main_cash
    """
    
    Account = Model.get('account.account')

    sCompanyName = sGetFeatureData(context, 'party,company_name')
    Party = Model.get('party.party')
    party, = Party.find([('name', '=', sCompanyName)])
    Company = Model.get('company.company')
    company, = Company.find([('party.id', '=', party.id)])

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
    """
    Create an instance of a Model, like Model.get('party.party')
    with the name attribute of 'uName'.
    Idempotent.
    """
    Party = Model.get(uKlass)
    if not Party.find([('name', '=', uName)]):
        instance = Party(name=uName)
        instance.save()

@step('Create a party named "{uName}"')
def step_impl(context, uName):
# boken in 3.2
#    context.execute_steps(u'''
#    Given Create a saved instance of "party.party" named "%s"
#    ''' % (uName,))
    Party = Model.get('party.party')
    if not Party.find([('name', '=', uName)]):
        instance = Party(name=uName)
        instance.save()

@step('Create an instance of "{uKlass}" named "{uName}" with fields')
def step_impl(context, uKlass, uName):
    """
    Create an instance of a Model, like Model.get('party.party')
    with the name attribute of 'uName'. It expects a |name|value| table.
    Idempotent.
    """

    assert context.table, "Please supply a table of field name and values"
    if hasattr(context.table, 'headings'):
        # if we have a real table, ensure it has 2 columns
        # otherwise, we will just fail during iteration
        assert_equal(len(context.table.headings), 2)

    Klass = Model.get(uKlass)
    if not Klass.find([('name', '=', uName)]):
        oInstance = Klass(name=uName)
        for row in context.table:
            gValue = string_to_python(row['name'], row['value'], Klass)
            setattr(oInstance, row['name'], gValue )
        oInstance.save()

@step('Set the slots of the instance named "{uName}" of model "{uKlass}" to the values')
def step_impl(context, uName, uKlass):
    """
    Guven an instance of a Model, like Model.get('party.party')
    with the name attribute of 'uName', set the attributes to the values.
    It expects a |name|value| table.
    Idempotent.
    """

    assert context.table, "Please supply a table of field name and values"
    if hasattr(context.table, 'headings'):
        # if we have a real table, ensure it has 2 columns
        # otherwise, we will just fail during iteration
        assert_equal(len(context.table.headings), 2)

    Klass = Model.get(uKlass)
    oInstance, = Klass.find([('name', '=', uName)])
    for row in context.table:
        setattr(oInstance, row['name'],
                string_to_python(row['name'], row['value'], Klass))
    oInstance.save()

@step('Create parties')
def step_impl(context):
    context.execute_steps(u'''Given Create a party named "Supplier"''')
    context.execute_steps(u'''Given Create a party named "Customer"''')

# Customer
@step('Create a party named "{uName}" with an account_payable attribute')
def step_impl(context, uName):
    """
    Create a party named 'uName' with an account_payable attribute.
    The account_payable Account is taken from the
    'account.template,main_payable' entry of the feature data
    (use 'Set the feature data with values' to override)
    Idempotent.
    """
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

# Direct, 0
@step('Create a PaymentTerm named "{uTermName}" with "{uNum}" days remainder')
def step_impl(context, uTermName, uNum):
    """
    Create a account.invoice.payment_term with name 'uTermName'
    with a account.invoice.payment_term.line of type 'remainder',
    and days=uNum.
    Idempotent.
    """
    PaymentTerm = Model.get('account.invoice.payment_term')
    iNum=int(uNum)
    assert iNum >= 0
    if not PaymentTerm.find([('name', '=', uTermName)]):
        PaymentTermLine = Model.get('account.invoice.payment_term.line')
        payment_term = PaymentTerm(name=uTermName)
        payment_term_line = PaymentTermLine(type='remainder', days=iNum)
        payment_term.lines.append(payment_term_line)
        payment_term.save()

# Accountant, Account
@step('Create a user named "{uName}" with the fields')
def step_impl(context, uName):
    """
    Create a res.user named 'uName' and the given field values.
    It expects a |name|value| table.
    If one of the field names is 'group', it will add the User to that group.
    Idempotent.
    """
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

# 12 products, Supplier
@step('Create a Purchase Order with description "{uDescription}" from supplier "{uSupplier}" with fields')
def step_impl(context, uDescription, uSupplier):
    """
    Create a Purchase Order from a supplier with a description.
    It expects a |name|value| table; the fields typically include:
    'payment_term', 'invoice_method', 'purchase_date', 'currency'
    Idempotent.
    """
    current_config = context.oProteusConfig

    Purchase = Model.get('purchase.purchase')

    Party = Model.get('party.party')
    supplier, = Party.find([('name', '=', uSupplier)])

    if not Purchase.find([('description', '=', uDescription),
                          ('party.id', '=', supplier.id)]):
        purchase = Purchase()
        purchase.party = supplier
        purchase.description = uDescription
        purchase.purchase_date = today
        
        for row in context.table:
            setattr(purchase, row['name'],
                    string_to_python(row['name'], row['value'], Purchase))

        purchase.save()
        assert Purchase.find([('description', '=', uDescription),
                              ('party.id', '=', supplier.id)])


@step('Create a calendar named "{uCalName}" owned by the user "{uUserName}"')
def step_impl(context, uCalName, uUserName):
    """
    WIP.
    Idempotent.
    """
    current_config = context.oProteusConfig

    Calendar = Model.get('calendar.calendar')

    uUserName=sGetFeatureData(context, 'user,accountant,name')
    uUserLogin=sGetFeatureData(context, 'user,accountant,login')
    uUserPassword=sGetFeatureData(context, 'user,accountant,password')
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
    """
    WIP.
    It expects a |name|value| table.
    Idempotent.
    """
    Calendar = Model.get('calendar.calendar')

    uUserName=sGetFeatureData(context, 'user,accountant,name')
    uUserLogin=sGetFeatureData(context, 'user,accountant,login')
    uUserPassword=sGetFeatureData(context, 'user,accountant,password')
    User = Model.get('res.user')
    oUser, = User.find([('name', '=', uUserName)])

    calendar, = Calendar.find([('name', '=', uCalName)])

    Rdate = pool.get('calendar.event.rdate')
    
    # FixMe: unfinished
    for row in context.table:
        pass

# unfinished
@step('Create holidays in the calendar named "{uCalName}" owned by the user named "{uUserName}" with fields')
def step_impl(context, uCalName, uUserName):
    """
    WIP.
    It expects a |name|value| table.
    Idempotent.
    """
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
