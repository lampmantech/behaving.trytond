"""
Account Asset Scenario
"""

import datetime
from dateutil.relativedelta import relativedelta
from decimal import Decimal
from proteus import config, Model, Wizard

from .support.fields import string_to_python, sGetFeatureData, vSetFeatureData
from .support import modules
from .support.stepfuns import vAssertContentTable

from behave import *
import proteus

TODAY = datetime.date.today()

def done(context):

    from trytond.modules.company.tests.tools import create_company, \
            get_company
    from trytond.modules.account.tests.tools import create_fiscalyear, \
            create_chart, get_accounts
    from.trytond.modules.account_invoice.tests.tools import \
            set_fiscalyear_invoice_sequences, create_payment_term
    from trytond.modules.account_asset.tests.tools \
            import add_asset_accounts

#step('Create database')

    config = config.set_trytond()
    config.pool.test = True

#step('Install account_asset')

    Module = Model.get('ir.module.module')
    module, = Module.find([
            ('name', '=', 'account_asset'),
            ])
    module.click('install')
    Wizard('ir.module.module.install_upgrade').execute('upgrade')

#@step('Create company')

    _ = create_company()
    company = get_company()

#@step('Reload the context')

    User = Model.get('res.user')
    config._context = User.get_preferences(True, config.context)

#@step('Create fiscal year')

    fiscalyear = set_fiscalyear_invoice_sequences(
            create_fiscalyear(company))
    fiscalyear.click('create_period')

#@step('Create chart of accounts')

    _ = create_chart(company)
    accounts = add_asset_accounts(get_accounts(company), company)
    revenue = accounts['revenue']
    asset_account = accounts['asset']
    expense = accounts['expense']
    depreciation_account = accounts['depreciation']

@step('Account Asset Scenario')
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
    # Tangible assets depn
    depreciation, = Account.find([
                ('kind', '=', 'payable'),
                ('company', '=', company.id),
                ('name', '=', sGetFeatureData(context, 'account.template,main_depreciation')),
                ])
    expense, = Account.find([
        ('kind', '=', 'expense'),
        ('name', '=', sGetFeatureData(context, 'account.template,main_expense')),
        ('company', '=', company.id),
        ])
    
    ProductUom = Model.get('product.uom')
    unit, = ProductUom.find([('name', '=', 'Unit')])
    ProductTemplate = Model.get('product.template')
    Product = Model.get('product.product')
    asset_product = Product()
    asset_template = ProductTemplate()
    asset_template.name = 'Asset'
    asset_template.type = 'assets'
    asset_template.default_uom = unit
    asset_template.list_price = Decimal('1000')
    asset_template.cost_price = Decimal('1000')
    asset_template.depreciable = True
    asset_template.account_expense = expense
    asset_template.account_revenue = revenue
    asset_template.account_asset = asset_account
    asset_template.account_depreciation = depreciation_account
    asset_template.depreciation_duration = Decimal(24)
    asset_template.save()
    asset_product.template = asset_template
    asset_product.save()

#@step('Create supplier')
#def step_impl(context):

    Party = Model.get('party.party')
    supplier = Party(name='Supplier')
    supplier.save()
    customer = Party(name='Customer')
    customer.save()

#@step('Create payment term')
#def step_impl(context):

    payment_term = create_payment_term()
    payment_term.save()

#@step('Buy an asset')
#def step_impl(context):

    Invoice = Model.get('account.invoice')
    InvoiceLine = Model.get('account.invoice.line')
    supplier_invoice = Invoice(type='in_invoice')
    supplier_invoice.party = supplier
    invoice_line = InvoiceLine()
    supplier_invoice.lines.append(invoice_line)
    invoice_line.product = asset_product
    invoice_line.quantity = 1
    assert invoice_line.account == asset_account
    supplier_invoice.invoice_date = TODAY + relativedelta(day=1, month=1)
    
    supplier_invoice.click('post')
    assert supplier_invoice.state == u'posted'
    invoice_line, = supplier_invoice.lines
    assert (asset_account.debit, asset_account.credit) == \
            (Decimal('1000'), Decimal('0'))

#@step('Depreciate the asset')
#def step_impl(context):

    Asset = Model.get('account.asset')
    asset = Asset()
    asset.product = asset_product
    asset.supplier_invoice_line = invoice_line
    assert asset.value == Decimal('1000.00')
    assert asset.start_date == supplier_invoice.invoice_date
    assert asset.end_date == (supplier_invoice.invoice_date +
            relativedelta(years=2, days=-1))
    assert asset.quantity == 1.0
	assert asset.unit == unit
    asset.residual_value = Decimal('100')
    assert asset.click('create_lines')
    assert len(asset.lines) == 24
    assert [l.depreciation for l in asset.lines] == [Decimal('37.5')] * 24
    assert asset.lines[0].actual_value == Decimal('962.50')
    assert asset.lines[0].accumulated_depreciation == Decimal('37.50')
    assert asset.lines[11].actual_value == Decimal('550.00')
    assert asset.lines[11].accumulated_depreciation == Decimal('450.00')
    assert asset.lines[-1].actual_value == Decimal('100.00')
    assert asset.lines[-1].accumulated_depreciation == Decimal('900.00')
    asset.click('run')

#@step('Create Moves for 3 months')
#def step_impl(context):

    create_moves = Wizard('account.asset.create_moves')
    create_moves.form.date = (supplier_invoice.invoice_date
            + relativedelta(months=3))
    create_moves.execute('create_moves')
    assert depreciation_account.debit == Decimal('0.00')
    assert depreciation_account.credit == Decimal('112.50')
    assert expense.debit == Decimal('112.50')
    assert expense.credit == Decimal('0.00')

#@step('Update the asset')
#def step_impl(context):

    update = Wizard('account.asset.update', [asset])
    update.form.value = Decimal('1100')
    update.execute('update_asset')
    assert update.form.amount == Decimal('100.00')
    update.form.date = (supplier_invoice.invoice_date
            + relativedelta(months=2))
    assert update.form.latest_move_date == (supplier_invoice.invoice_date
                + relativedelta(months=3, days=-1))
    assert update.form.next_depreciation_date == (supplier_invoice.invoice_date
                + relativedelta(months=4, days=-1))
    try:
        update.execute('create_move')  # doctest: +IGNORE_EXCEPTION_DETAIL
    except ValueError:
        pass
    else:
        raise RuntimeError('A ValueError should have been raised')

    update.form.date = (supplier_invoice.invoice_date
            + relativedelta(months=3))
    update.execute('create_move')
    asset.reload()
    assert asset.value == Decimal('1100')
    
    assert [l.depreciation for l in asset.lines[:3]] == \
      [Decimal('37.50'), Decimal('37.50'), Decimal('37.50')]
    assert [l.depreciation for l in asset.lines[3:-1]] == \
      [Decimal('42.26')] * 20
    assert asset.lines[-1].depreciation == Decimal('42.30')
    
    depreciation_account.reload()
    assert depreciation_account.debit == Decimal('100.00')
    assert depreciation_account.credit == Decimal('112.50')
    
    expense.reload()
    assert expense.debit == Decimal('112.50')
    assert expense.credit == Decimal('100.00')

#@step('Create Moves for 3 other months')
#def step_impl(context):

    create_moves = Wizard('account.asset.create_moves')
    create_moves.form.date = (supplier_invoice.invoice_date
            + relativedelta(months=6))
    create_moves.execute('create_moves')
    
    depreciation_account.reload()
    assert depreciation_account.debit == Decimal('100.00')
    assert depreciation_account.credit == Decimal('239.28')
    
    expense.reload()
    assert expense.debit == Decimal('239.28')
    assert expense.credit == Decimal('100.00')

#@step('Sale the asset')
#def step_impl(context):

    customer_invoice = Invoice(type='out_invoice')
    customer_invoice.party = customer
    invoice_line = InvoiceLine()
    customer_invoice.lines.append(invoice_line)
    invoice_line.product = asset_product
    invoice_line.asset = asset
    invoice_line.quantity = 1
    invoice_line.unit_price = Decimal('600')
    assert invoice_line.account == revenue
    customer_invoice.click('post')
    
    assert customer_invoice.state == u'posted'
    
    asset.reload()
    assert asset.customer_invoice_line == customer_invoice.lines[0]
    assert revenue.debit == Decimal('860.72')
    assert revenue.credit == Decimal('600.00')
    
    asset_account.reload()
    assert asset_account.debit == Decimal('1000.00')
    assert asset_account.credit == Decimal('1100.00')
    
    depreciation_account.reload()
    assert depreciation_account.debit == Decimal('339.28')
    assert depreciation_account.credit == Decimal('239.28')

#@step('Generate the asset report')
#def step_impl(context):

#    print_depreciation_table = Wizard(
#            'account.asset.print_depreciation_table')
#    print_depreciation_table.execute('print_')
