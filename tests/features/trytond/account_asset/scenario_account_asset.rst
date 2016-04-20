======================
Account Asset Scenario
======================

Imports::

    >>> import datetime
    >>> from dateutil.relativedelta import relativedelta
    >>> from decimal import Decimal
    >>> from proteus import config, Model, Wizard
    >>> from trytond.modules.company.tests.tools import create_company, \
    ...     get_company
    >>> from trytond.modules.account.tests.tools import create_fiscalyear, \
    ...     create_chart, get_accounts
    >>> from.trytond.modules.account_invoice.tests.tools import \
    ...     set_fiscalyear_invoice_sequences, create_payment_term
    >>> from trytond.modules.account_asset.tests.tools \
    ...     import add_asset_accounts
    >>> today = datetime.date.today()

Create database::

    >>> config = config.set_trytond()
    >>> config.pool.test = True

Install account_asset::

    >>> Module = Model.get('ir.module.module')
    >>> module, = Module.find([
    ...     ('name', '=', 'account_asset'),
    ...     ])
    >>> module.click('install')
    >>> Wizard('ir.module.module.install_upgrade').execute('upgrade')

Create company::

    >>> _ = create_company()
    >>> company = get_company()

Reload the context::

    >>> User = Model.get('res.user')
    >>> config._context = User.get_preferences(True, config.context)

Create fiscal year::

    >>> fiscalyear = set_fiscalyear_invoice_sequences(
    ...     create_fiscalyear(company))
    >>> fiscalyear.click('create_period')

Create chart of accounts::

    >>> _ = create_chart(company)
    >>> accounts = add_asset_accounts(get_accounts(company), company)
    >>> revenue = accounts['revenue']
    >>> asset_account = accounts['asset']
    >>> expense = accounts['expense']
    >>> depreciation_account = accounts['depreciation']

Create an asset::

    >>> ProductUom = Model.get('product.uom')
    >>> unit, = ProductUom.find([('name', '=', 'Unit')])
    >>> ProductTemplate = Model.get('product.template')
    >>> Product = Model.get('product.product')
    >>> asset_product = Product()
    >>> asset_template = ProductTemplate()
    >>> asset_template.name = 'Asset'
    >>> asset_template.type = 'assets'
    >>> asset_template.default_uom = unit
    >>> asset_template.list_price = Decimal('1000')
    >>> asset_template.cost_price = Decimal('1000')
    >>> asset_template.depreciable = True
    >>> asset_template.account_expense = expense
    >>> asset_template.account_revenue = revenue
    >>> asset_template.account_asset = asset_account
    >>> asset_template.account_depreciation = depreciation_account
    >>> asset_template.depreciation_duration = Decimal(24)
    >>> asset_template.save()
    >>> asset_product.template = asset_template
    >>> asset_product.save()

Create supplier::

    >>> Party = Model.get('party.party')
    >>> supplier = Party(name='Supplier')
    >>> supplier.save()
    >>> customer = Party(name='Customer')
    >>> customer.save()

Create payment term::

    >>> payment_term = create_payment_term()
    >>> payment_term.save()

Buy an asset::

    >>> Invoice = Model.get('account.invoice')
    >>> InvoiceLine = Model.get('account.invoice.line')
    >>> supplier_invoice = Invoice(type='in_invoice')
    >>> supplier_invoice.party = supplier
    >>> invoice_line = InvoiceLine()
    >>> supplier_invoice.lines.append(invoice_line)
    >>> invoice_line.product = asset_product
    >>> invoice_line.quantity = 1
    >>> invoice_line.account == asset_account
    True
    >>> supplier_invoice.invoice_date = today + relativedelta(day=1, month=1)
    >>> supplier_invoice.click('post')
    >>> supplier_invoice.state
    u'posted'
    >>> invoice_line, = supplier_invoice.lines
    >>> (asset_account.debit, asset_account.credit) == \
    ...     (Decimal('1000'), Decimal('0'))
    True

Depreciate the asset::

    >>> Asset = Model.get('account.asset')
    >>> asset = Asset()
    >>> asset.product = asset_product
    >>> asset.supplier_invoice_line = invoice_line
    >>> asset.value
    Decimal('1000.00')
    >>> asset.start_date == supplier_invoice.invoice_date
    True
    >>> asset.end_date == (supplier_invoice.invoice_date +
    ...     relativedelta(years=2, days=-1))
    True
    >>> asset.quantity
    1.0
    >>> asset.unit == unit
    True
    >>> asset.residual_value = Decimal('100')
    >>> asset.click('create_lines')
    >>> len(asset.lines)
    24
    >>> [l.depreciation for l in asset.lines] == [Decimal('37.5')] * 24
    True
    >>> asset.lines[0].actual_value
    Decimal('962.50')
    >>> asset.lines[0].accumulated_depreciation
    Decimal('37.50')
    >>> asset.lines[11].actual_value
    Decimal('550.00')
    >>> asset.lines[11].accumulated_depreciation
    Decimal('450.00')
    >>> asset.lines[-1].actual_value
    Decimal('100.00')
    >>> asset.lines[-1].accumulated_depreciation
    Decimal('900.00')
    >>> asset.click('run')

Create Moves for 3 months::

    >>> create_moves = Wizard('account.asset.create_moves')
    >>> create_moves.form.date = (supplier_invoice.invoice_date
    ...     + relativedelta(months=3))
    >>> create_moves.execute('create_moves')
    >>> depreciation_account.debit
    Decimal('0.00')
    >>> depreciation_account.credit
    Decimal('112.50')
    >>> expense.debit
    Decimal('112.50')
    >>> expense.credit
    Decimal('0.00')

Update the asset::

    >>> update = Wizard('account.asset.update', [asset])
    >>> update.form.value = Decimal('1100')
    >>> update.execute('update_asset')
    >>> update.form.amount
    Decimal('100.00')
    >>> update.form.date = (supplier_invoice.invoice_date
    ...     + relativedelta(months=2))
    >>> update.form.latest_move_date == (supplier_invoice.invoice_date
    ...     + relativedelta(months=3, days=-1))
    True
    >>> update.form.next_depreciation_date == (supplier_invoice.invoice_date
    ...     + relativedelta(months=4, days=-1))
    True
    >>> update.execute('create_move')  # doctest: +IGNORE_EXCEPTION_DETAIL
    Traceback (most recent call last):
        ...
    ValueError: ...

    >>> update.form.date = (supplier_invoice.invoice_date
    ...     + relativedelta(months=3))
    >>> update.execute('create_move')
    >>> asset.reload()
    >>> asset.value
    Decimal('1100')
    >>> [l.depreciation for l in asset.lines[:3]]
    [Decimal('37.50'), Decimal('37.50'), Decimal('37.50')]
    >>> [l.depreciation for l in asset.lines[3:-1]] == [Decimal('42.26')] * 20
    True
    >>> asset.lines[-1].depreciation
    Decimal('42.30')
    >>> depreciation_account.reload()
    >>> depreciation_account.debit
    Decimal('100.00')
    >>> depreciation_account.credit
    Decimal('112.50')
    >>> expense.reload()
    >>> expense.debit
    Decimal('112.50')
    >>> expense.credit
    Decimal('100.00')

Create Moves for 3 other months::

    >>> create_moves = Wizard('account.asset.create_moves')
    >>> create_moves.form.date = (supplier_invoice.invoice_date
    ...     + relativedelta(months=6))
    >>> create_moves.execute('create_moves')
    >>> depreciation_account.reload()
    >>> depreciation_account.debit
    Decimal('100.00')
    >>> depreciation_account.credit
    Decimal('239.28')
    >>> expense.reload()
    >>> expense.debit
    Decimal('239.28')
    >>> expense.credit
    Decimal('100.00')

Sale the asset::

    >>> customer_invoice = Invoice(type='out_invoice')
    >>> customer_invoice.party = customer
    >>> invoice_line = InvoiceLine()
    >>> customer_invoice.lines.append(invoice_line)
    >>> invoice_line.product = asset_product
    >>> invoice_line.asset = asset
    >>> invoice_line.quantity = 1
    >>> invoice_line.unit_price = Decimal('600')
    >>> invoice_line.account == revenue
    True
    >>> customer_invoice.click('post')
    >>> customer_invoice.state
    u'posted'
    >>> asset.reload()
    >>> asset.customer_invoice_line == customer_invoice.lines[0]
    True
    >>> revenue.debit
    Decimal('860.72')
    >>> revenue.credit
    Decimal('600.00')
    >>> asset_account.reload()
    >>> asset_account.debit
    Decimal('1000.00')
    >>> asset_account.credit
    Decimal('1100.00')
    >>> depreciation_account.reload()
    >>> depreciation_account.debit
    Decimal('339.28')
    >>> depreciation_account.credit
    Decimal('239.28')

Generate the asset report::

    >>> print_depreciation_table = Wizard(
    ...     'account.asset.print_depreciation_table')
    >>> print_depreciation_table.execute('print_')
