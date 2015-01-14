# -*- encoding: utf-8 -*-
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


today = datetime.date.today()

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
        
    Company = proteus.Model.get('company.company')
    FiscalYear = proteus.Model.get('account.fiscalyear')
    Party = proteus.Model.get('party.party')

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

        Sequence = proteus.Model.get('ir.sequence')
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
            code='account.move', company=company)
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

# 'Minimal Account Chart', 'Minimal Account Chart'
@step('Create a chart of accounts from template "{uTem}" with root "{uRoot}"')
def step_impl(context, uTem, uRoot):
    """
    Create a chart of accounts from template "{uTem}" 
    with root account "{uRoot}".
    Before you do this, with the step 'Set the feature data with values:'
    set the feature data as a |name|value| table for:
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

        # MINIMAL_ACCOUNT_TEMPLATE
        AccountTemplate = proteus.Model.get('account.account.template')
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

# Direct, 0
@step('Create a PaymentTerm named "{uTermName}" with "{uNum}" days remainder')
def step_impl(context, uTermName, uNum):
    """
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
        payment_term = PaymentTerm(name=uTermName)
        payment_term_line = PaymentTermLine(type='remainder', days=iNum)
        payment_term.lines.append(payment_term_line)
        payment_term.save()

# 10% Sales Tax
@step('Create a tax named "{uTaxName}" with fields')
def step_impl(context, uTaxName):
    """Create a tax:
	and Create a tax named "10% Sales Tax" with fields
	    | name                  | value            |
	    | description           | 10% Sales Tax    |
	    | type 	            | percentage       |
	    | rate 	            | .10	       |
	    | invoice_base_code     | invoice base     |
	    | invoice_tax_code      | invoice tax      |
	    | credit_note_base_code | credit note base |
	    | credit_note_tax_code  | credit note tax  |
    """
    Party = Model.get('party.party')
    sCompanyName = sGetFeatureData(context, 'party,company_name')
    party, = Party.find([('name', '=', sCompanyName)])
    Company = Model.get('company.company')
    company, = Company.find([('party.id', '=', party.id)])

    Account = Model.get('account.account')
    account_tax, = Account.find([
        ('kind', '=', 'other'),
        ('name', '=', sGetFeatureData(context, 'account.template,main_tax')),
        ('company', '=', company.id),
        ])

    Tax = Model.get('account.tax')
    if not Tax.find([('name', '=', uTaxName)]):
        
        TaxCode = Model.get('account.tax.code')
        
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

