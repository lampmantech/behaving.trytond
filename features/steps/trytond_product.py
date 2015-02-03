# -*- mode: python; py-indent-offset: 4; coding: utf-8-unix; encoding: utf-8 -*-
"""


"""
from behave import *
import proteus

import time
import datetime
from dateutil.relativedelta import relativedelta
from decimal import Decimal

from .support.fields import string_to_python, sGetFeatureData, vSetFeatureData
from .support import modules
from .support.tools import *
from .support import stepfuns
from .support.stepfuns import vAssertContentTable

TODAY = datetime.date.today()

from .support.stepfuns import gGetFeaturesRevExp
from .support import stepfuns

# Category
@step('Create a ProductCategory named "{uName}"')
def step_impl(context, uName):
    """
    Create a saved instance of "product.category" named "{uName}"
    Idempotent.
    """
    context.execute_steps(u'''
    Given Create a saved instance of "product.category" named "%s"
    ''' % (uName,))

# product , Category
@step('Create a ProductTemplate named "{uName}" with stock accounts from features from a ProductCategory named "{uCatName}" with |name|value| fields')
def step_impl(context, uName, uCatName):
    """
    Create a ProductTemplate named "{uName}"
    from a ProductCategory named "{uCatName}" with |name|value| fields
	  | name              | value |
	  | type	      | goods |
	  | cost_price_method | fifo  |
	  | purchasable       | True  |
	  | salable 	      | True  |
	  | list_price 	      | 10    |
	  | cost_price 	      | 5     |
	  | delivery_time     | 0     |
	  | default_uom	      | Unit  |
	  | account_expense   | Main Expense |
	  | account_revenue   | Main Revenue |
	  | account_cogs      | COGS  |
          | stock_journal     | STO   |
    This requires that anglo_saxon
    Idempotent.
    """
    # FixMe: with supllier tax "{uTax}"

    current_config = context.oProteusConfig
    ProductTemplate = proteus.Model.get('product.template')

    sCompanyName = sGetFeatureData(context, 'party,company_name')
    Party = proteus.Model.get('party.party')
    party, = Party.find([('name', '=', sCompanyName)])
    Company = proteus.Model.get('company.company')
    company, = Company.find([('party.id', '=', party.id)])

    if not ProductTemplate.find([('name', '=', uName),
                                 ('category.name', '=', uCatName),
                             ]):
        ProductCategory = proteus.Model.get('product.category')

        ProductUom = proteus.Model.get('product.uom')

        AccountJournal = proteus.Model.get('account.journal')
        # This account jourmal is created by Tryton
        # Tryton-3.2/trytond_stock-3.2.3/location.xml
        stock_journal, = AccountJournal.find([('code', '=', 'STO'),])
        Account = proteus.Model.get('account.account')

        template = ProductTemplate()
        template.name = uName
        # default these in case they are not provided
        revenue, expense, = stepfuns.gGetFeaturesRevExp(context, company)
        # These are in by trytond_account_stock_continental/account.xml
        # which is pulled in by trytond_account_stock_anglo_saxon
        stock, stock_customer, stock_lost_found, stock_production, \
            stock_supplier, = stepfuns.gGetFeaturesStockAccs(context, company)

        cogs, = Account.find([
# what kind is cogs and why is it not in the default accounts?
#?            ('kind', '=', 'other'),
            ('name', '=', sGetFeatureData(context, 'account.template,main_cogs')),
            ('company', '=', company.id),
            ])
        # template_average.cost_price_method = 'fixed'
        # type, cost_price_method, default_uom
        for row in context.table:
            if row['name'] == 'stock_journal':
                stock_journal, = AccountJournal.find([('code', '=', row['value']),])
            elif row['name'] == 'account_expense':
                expense, = Account.find([
                    ('kind', '=', 'expense'),
                    ('name', '=', row['value']),
                    ('company', '=', company.id),
                ])
            elif row['name'] == 'account_revenue':
                revenue, = Account.find([
                    ('kind', '=', 'revenue'),
                    ('name', '=', row['value']),
                    ('company', '=', company.id),
                ])
            elif row['name'] == 'account_stock':
                stock, = Account.find([
                    ('kind', '=', 'stock'),
                    ('name', '=', row['value']),
                    ('company', '=', company.id),
                ])
            elif row['name'] == 'account_cogs':
                cogs, = Account.find([
# Fixme - what is the right kind for COGS? goods? other? expense?
#                    ('kind', '=', 'other'),
                    ('name', '=', row['value']),
                    ('company', '=', company.id),
                ])
            else:
                setattr(template, row['name'],
                        string_to_python(row['name'], row['value'], ProductTemplate))

        template.account_expense = expense
        template.account_revenue = revenue
        # this requires anglo_saxon
        template.account_cogs = cogs

        category, = ProductCategory.find([('name', '=', uCatName)])
        template.category = category

        template.account_stock = stock
        template.account_stock_supplier = stock_supplier
        template.account_stock_customer = stock_customer
        template.account_stock_production = stock_production
        template.account_stock_lost_found = stock_lost_found

        template.account_journal_stock_supplier = stock_journal
        template.account_journal_stock_customer = stock_journal
        template.account_journal_stock_lost_found = stock_journal

        if template.cost_price_method == 'fifo':
            modules.lInstallModules(['product_cost_fifo'], current_config)

        template.save()

    assert ProductTemplate.find([('name', '=', uName),
                                 ('category.name', '=', uCatName),
                             ])


# Service Product
@step('Create a ProductTemplate named "{uTemplateName}" with supplier_tax named "{uTaxName}" with |name|value| fields')
def step_impl(context, uTemplateName, uTaxName):
    """
    Create a ProductTemplate named "{uTemplateName}"
    with a supplier_tax named "{uTaxName}"
    with |name|value| fields such as:
      type, cost_price_method, default_uom, list_price, cost_price.
    The fields account_expense, account_revenue become the related accounts.
    E. g.
	  | name              | value   |
	  | type	      | service |
	  | list_price 	      | 40      |
	  | cost_price 	      | 20      |
	  | default_uom	      | Unit    |
	  | account_expense   | Main Expense |
	  | account_revenue   | Main Revenue |
#	  | cost_price_method | fixed        |
    We'll put a hack to work on systems without a CoTs:
    just call the tax "NO Sales Tax".
    Idempotent.
    """

    ProductTemplate = proteus.Model.get('product.template')
    Account = proteus.Model.get('account.account')

    Party = proteus.Model.get('party.party')
    sCompanyName = sGetFeatureData(context, 'party,company_name')
    party, = Party.find([('name', '=', sCompanyName)])
    Company = proteus.Model.get('company.company')
    company, = Company.find([('party.id', '=', party.id)])

    if not ProductTemplate.find([('name', '=', uTemplateName)]):
        template = ProductTemplate()
        template.name = uTemplateName
        # consumable
        # NOT currency
        # default these in case they are not provided
        revenue, expense, = stepfuns.gGetFeaturesRevExp(context, company)

        # type, cost_price_method, default_uom, list_price, cost_price
        # account_expense, account_revenue
        for row in context.table:
            if row['name'] == 'account_expense':
                expense, = Account.find([
                    ('kind', '=', 'expense'),
                    ('name', '=', row['value']),
                    ('company', '=', company.id),
                ])
            elif row['name'] == 'account_revenue':
                revenue, = Account.find([
                    ('kind', '=', 'revenue'),
                    ('name', '=', row['value']),
                    ('company', '=', company.id),
                ])
            else:
                setattr(template, row['name'],
                    string_to_python(row['name'], row['value'],
                                     ProductTemplate))

        template.account_expense = expense
        template.account_revenue = revenue

        # We'll put a hack to work on systems without a CoTs
        # Just call the tax "NO Sales Tax" and the taxes will be ignored
        if uTaxName != "NO Sales Tax":
            Tax = proteus.Model.get('account.tax')
            # FixMe: need to handle supplier_tax as an append in string_to_python
            tax, = Tax.find([('name', '=', uTaxName)])
            template.supplier_taxes.append(tax)

        template.save()
    assert ProductTemplate.find([('name', '=', uTemplateName)])

# Services Bought, Service Product
@step('Create a product with description "{uDescription}" from template "{uTemplateName}"')
def step_impl(context, uDescription, uTemplateName):
    """
    Create a product with description "{uDescription}" from template "{uTemplateName}"
    Idempotent.
    """
    ProductTemplate = proteus.Model.get('product.template')
    template, = ProductTemplate.find([('name', '=', uTemplateName)])

    Product = proteus.Model.get('product.product')
    if not Product.find([('description', '=', uDescription)]):
        product = Product()
        product.template = template
        product.description = uDescription
        product.save()
    assert Product.find([('description', '=', uDescription)])

