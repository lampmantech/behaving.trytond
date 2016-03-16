# -*- mode: python; py-indent-offset: 4; coding: utf-8-unix; encoding: utf-8 -*-
"""


"""
from behave import *
import proteus

import datetime
from dateutil.relativedelta import relativedelta
from decimal import Decimal

from .support.fields import string_to_python, sGetFeatureData, vSetFeatureData
from .support import modules
from .support.tools import *
from .support.stepfuns import gGetFeaturesRevExp, gGetFeaturesPayRec
from .support import stepfuns

TODAY = datetime.date.today()

@step('Create this fiscal year')
@step('Create this fiscal year without Invoicing')
def step_impl(context):
    """
    Given \
    Create the fiscal year "TODAY" without Invoicing
    """
    context.execute_steps(u'''
    Given Create the fiscal year "TODAY" without Invoicing
    ''')

@step('Create the fiscal year "{uYear}" without Invoicing')
def step_impl(context, uYear):
    """
    Given \
    Creates a fiscal year 'uYear' with a non-Strict post_move_seq.
    Create the company first before creating fiscal years.
    """
    config = context.oProteusConfig

    Company = proteus.Model.get('company.company')
    FiscalYear = proteus.Model.get('account.fiscalyear')
    Party = proteus.Model.get('party.party')

    sCompanyName = sGetFeatureData(context, 'party,company_name')
    party, = Party.find([('name', '=', sCompanyName)])
    company, = Company.find([('party.id', '=', party.id)])

    if uYear.lower() == "now" or uYear.upper() == "TODAY":
        uYear=str(TODAY.year)
    if not FiscalYear.find([('name', '=', uYear),
                            ('company', '=', company.id),]):
        oDate = datetime.date(int(uYear), 1, 1)

        fiscalyear = FiscalYear(name=uYear)
        fiscalyear.start_date = oDate + relativedelta(month=1, day=1)
        fiscalyear.end_date = oDate + relativedelta(month=12, day=31)
        fiscalyear.company = company

        Sequence = proteus.Model.get('ir.sequence')
        post_move_sequence = Sequence(name='post_move_seq %s' % (uYear,),
                                      code='account.move',
                                      company=company)
        post_move_sequence.save()
        fiscalyear.post_move_sequence = post_move_sequence
        fiscalyear.save()

        FiscalYear.create_period([fiscalyear.id], config.context)
        assert len(fiscalyear.periods) == 12

    assert FiscalYear.find([('name', '=', str(uYear))])

@step('Create this fiscal year with Invoicing')
def step_impl(context):
    """
    Given \
    Create the fiscal year "TODAY" with Invoicing
    """
    context.execute_steps(u'''
    Given Create the fiscal year "TODAY" with Invoicing
    ''')

@step('Create the fiscal year "{uYear}" with Invoicing')
def step_impl(context, uYear):
    """
    Given \
    Creates a fiscal year 'uYear' with a non-Strict move_sequence
    and a Strict invoice_sequence for account.invoice.
    Create the company first.
    """
    config = context.oProteusConfig

    if uYear == u'TODAY': uYear = str(TODAY.year)

    FiscalYear = proteus.Model.get('account.fiscalyear')
    Party = proteus.Model.get('party.party')

    sCompanyName = sGetFeatureData(context, 'party,company_name')
    party, = Party.find([('name', '=', sCompanyName)])
    Company = proteus.Model.get('company.company')
    company, = Company.find([('party.id', '=', party.id)])

    if not FiscalYear.find([('name', '=', str(uYear)),
                            ('company', '=', company.id),]):
        oDate = datetime.date(int(uYear), 1, 1)

        fiscalyear = FiscalYear(name='%s' % (uYear,))
        fiscalyear.start_date = oDate + relativedelta(month=1, day=1)
        fiscalyear.end_date = oDate + relativedelta(month=12, day=31)
        fiscalyear.company = company

        Sequence = proteus.Model.get('ir.sequence')
        post_move_sequence = Sequence(name='%s' % uYear,
                                      code='account.move',
                                      company=company)
        post_move_sequence.save()
        fiscalyear.post_move_sequence = post_move_sequence

        SequenceStrict = proteus.Model.get('ir.sequence.strict')
        invoice_sequence = SequenceStrict(name='%s' % uYear,
                                          code='account.invoice',
                                          company=company)
        invoice_sequence.save()
        fiscalyear.out_invoice_sequence = invoice_sequence
        fiscalyear.in_invoice_sequence = invoice_sequence
        fiscalyear.out_credit_note_sequence = invoice_sequence
        fiscalyear.in_credit_note_sequence = invoice_sequence
        fiscalyear.save()

        FiscalYear.create_period([fiscalyear.id], context.oProteusConfig.context)
        assert len(fiscalyear.periods) == 12

    assert FiscalYear.find([('name', '=', str(uYear))])

@step('Create this fiscal year with a non-strict post_move_seq')
def step_impl(context):
    """
    Given \
    Create the fiscal year "TODAY.year" with a non-Strict post_move_seq
    """
    uYear=str(TODAY.year)
    context.execute_steps(u'''
    Given Create the fiscal year "%s" with a non-Strict post_move_seq
    '''  % (uYear,))

# same as
# @step('Create the fiscal year "{uYear}" without Invoicing')
@step('Create the fiscal year "{uYear}" with a non-Strict post_move_seq')
def step_impl(context, uYear):
    """
    Given \
    Creates a fiscal year 'uYear' with a non-Strict post_move_seq.
    Create the company first.
    """
    current_config = context.oProteusConfig

    Party = proteus.Model.get('party.party')
    sCompanyName = sGetFeatureData(context, 'party,company_name')
    party, = Party.find([('name', '=', sCompanyName)])
    Company = proteus.Model.get('company.company')
    company, = Company.find([('party.id', '=', party.id)])

    FiscalYear = proteus.Model.get('account.fiscalyear')

    if uYear.lower() == "now" or uYear.upper() == "TODAY":
        uYear=str(TODAY.year)
    oDate=datetime.date(int(uYear), TODAY.month, TODAY.day)
    if not FiscalYear.find([('name', '=', uYear),
                            ('company', '=', company.id),]):
        fiscalyear = FiscalYear(name=uYear)
        fiscalyear.start_date = oDate + relativedelta(month=1, day=1)
        fiscalyear.end_date = oDate + relativedelta(month=12, day=31)
        fiscalyear.company = company

        Sequence = proteus.Model.get('ir.sequence')
        post_move_seq = Sequence(name="post_move_seq %s" %(uYear,),
                                 code='account.move',
                                 company=company)
        post_move_seq.save()

        fiscalyear.post_move_sequence = post_move_seq
        fiscalyear.save()

        FiscalYear.create_period([fiscalyear.id], current_config.context)

    assert FiscalYear.find([('name', '=', uYear)])

@step('Create a default Minimal Account Chart')
def step_impl(context):
    """
    Given \
    Create a default chart of accounts from template
    "Minimal Account Chart" with root "Minimal Account Chart"

    """
    context.execute_steps(u'''
    Given Create a chart of accounts from template "%s" with root "%s"
    ''' % ( 'Minimal Account Chart', 'Minimal Account Chart'))

# 'Minimal Account Chart', 'Minimal Account Chart'
@step('Create a chart of accounts from template "{uTem}" with root "{uRoot}"')
def step_impl(context, uTem, uRoot):
    """
    Given \
    Create a chart of accounts from template "{uTem}"
    with root account "{uRoot}".
    Before you do this, with the step 'Set the feature data with values:'
    set the feature data as a |name|value| table for:
    * party,company_name
    * account.template,main_receivable
    * account.template,main_payable
    * account.template,main_revenue
    * account.template,main_expense
    * account.template,main_cash
    """
    Account = proteus.Model.get('account.account')

    sCompanyName = sGetFeatureData(context, 'party,company_name')
    Party = proteus.Model.get('party.party')
    party, = Party.find([('name', '=', sCompanyName)])
    Company = proteus.Model.get('company.company')
    company, = Company.find([('party.id', '=', party.id)])

    # MINIMAL_ACCOUNT_ROOT
    if not Account.find([('name', '=', uRoot),
                         ('company', '=', company.id),]):

        create_chart = proteus.Wizard('account.create_chart')
        create_chart.execute('account')

        AccountTemplate = proteus.Model.get('account.account.template')
        account_template, = AccountTemplate.find([('name', '=', uTem)])
        create_chart.form.account_template = account_template
        create_chart.form.company = company
        create_chart.execute('create_account')

        iLen = len( Account.find([
                ('company', '=', company.id),
                ]))
        assert iLen >= 6

        payable, receivable, = gGetFeaturesPayRec(context, company)
        create_chart.form.account_receivable = receivable
        create_chart.form.account_payable = payable
        create_chart.execute('create_properties')

        cash, = Account.find([
                #? cash or other
                ('kind', '=', 'other'),
                ('company', '=', company.id),
                ('name', '=', sGetFeatureData(context, 'account.template,main_cash')),
                ])
        # This is only used if the bank module is loaded
        #? check its an attribute first?
        if hasattr(Account, 'bank_reconcile'):
            cash.bank_reconcile = True
        cash.save()

    assert Account.find([('name', '=', uRoot)])

@step('Set the default credit and debit accounts on the cash Journal')
def step_impl(context):
    """
    """
    Account = proteus.Model.get('account.account')
    Journal = proteus.Model.get('account.journal')

    sCompanyName = sGetFeatureData(context, 'party,company_name')
    Party = proteus.Model.get('party.party')
    party, = Party.find([('name', '=', sCompanyName)])
    Company = proteus.Model.get('company.company')
    company, = Company.find([('party.id', '=', party.id)])

    cash, = Account.find([
            #? cash or other
            ('kind', '=', 'other'),
            ('company', '=', company.id),
            ('name', '=', sGetFeatureData(context, 'account.template,main_cash')),
            ])
    #? where is the cash Journal defined?
    #? Im assuming everyone wants this, but
    #? maybe this should be its own step
    #? its in scenario_purchase.rst
    cash_journal, = Journal.find([('type', '=', 'cash')])
    cash_journal.credit_account = cash
    cash_journal.debit_account = cash
    cash_journal.save()


# Direct, 0
@step('Create a PaymentTerm named "{uTermName}" with "{uNum}" days remainder')
def step_impl(context, uTermName, uNum):
    """
    Given \
    Create a account.invoice.payment_term with name 'uTermName'
    with a account.invoice.payment_term.line of type 'remainder',
    and days=uNum.
    Idempotent.
    """
    PaymentTerm = proteus.Model.get('account.invoice.payment_term')
    iNum=int(uNum)
    assert iNum >= 0
    if not PaymentTerm.find([('name', '=', uTermName)]):
        PaymentTermLine = proteus.Model.get('account.invoice.payment_term.line')
        PaymentTermLineRelativeDelta = proteus.Model.get('account.invoice.payment_term.line.relativedelta')
        payment_term = PaymentTerm(name=uTermName)
        payment_term_line = PaymentTermLine(type='remainder')
        # FixMe: was3.4 days=iNum now3.6 relativedeltas=
        #? , relativedeltas=[PaymentTermLineRelativeDelta(days=30)]
        payment_term.lines.append(payment_term_line)
        payment_term.save()

    assert PaymentTerm.find([('name', '=', uTermName)])

# 10% Sales Tax
@step('Create a tax named "{uTaxName}" with fields')
def step_impl(context, uTaxName):
    """
    Given \
        Create a tax named "10% Sales Tax" with fields
	    | name                  | value            |
	    | description           | 10% Sales Tax    |
	    | type 	                | percentage       |
	    | rate 	                | .10	           |
	    | invoice_base_code     | invoice base     |
	    | invoice_tax_code      | invoice tax      |
	    | credit_note_base_code | credit note base |
	    | credit_note_tax_code  | credit note tax  |
    """
    Party = proteus.Model.get('party.party')
    sCompanyName = sGetFeatureData(context, 'party,company_name')
    party, = Party.find([('name', '=', sCompanyName)])
    Company = proteus.Model.get('company.company')
    company, = Company.find([('party.id', '=', party.id)])

    Account = proteus.Model.get('account.account')
    account_tax, = Account.find([
        ('kind', '=', 'other'),
        ('name', '=', sGetFeatureData(context, 'account.template,main_tax')),
        ('company', '=', company.id),
        ])

    Tax = proteus.Model.get('account.tax')
    if not Tax.find([('name', '=', uTaxName)]):

        TaxCode = proteus.Model.get('account.tax.code')

        tax = Tax()
        tax.name = uTaxName
        tax.invoice_account = account_tax
        tax.credit_note_account = account_tax
        for row in context.table:
            if row['name'] == 'invoice_base_code' or \
                   row['name'] == 'invoice_tax_code' or \
                   row['name'] == 'credit_note_base_code' or \
                   row['name'] == 'credit_note_tax_code':
                # create these if they dont exist
                l = TaxCode.find([('name', '=', row['value'])])
                if l:
                    tax_code = l[0]
                else:
                    tax_code = TaxCode(name=row['value'])
                    tax_code.save()
                setattr(tax, row['name'], tax_code)
            else:
                setattr(tax, row['name'],
                    string_to_python(row['name'], row['value'], Tax))

        tax.save()
    assert Tax.find([('name', '=', uTaxName)])

