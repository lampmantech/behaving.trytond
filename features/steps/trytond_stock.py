# -*- mode: python; py-indent-offset: 4; coding: utf-8-unix; encoding: utf-8 -*-
"""


"""
from behave import *
import proteus
import ProteusConfig

import datetime
from dateutil.relativedelta import relativedelta
from decimal import Decimal

from .support.fields import string_to_python, sGetFeatureData, vSetFeatureData
from .support.tools import *

TODAY = datetime.date.today()

# 'Stock Admin', 'stock_admin', 'Stock Administration'
@step('Create a stock admin user named "{uName}" with login "{uLogin}" in group "{uGroup}"')
def step_impl(context, uName, uLogin, uGroup):
    """
    Given \
    Create a stock admin user named "{uName}" with login "{uLogin}" in group "{uGroup}"
    """
    current_config = context.oProteusConfig

    User = proteus.Model.get('res.user')
    Company = proteus.Model.get('company.company')

    sCompanyName = sGetFeatureData(context, 'party,company_name')
    party, = Party.find([('name', '=', sCompanyName)])
    company, = Company.find([('party.id', '=', party.id)])

    if not User.find([('name', '=', uName)]):
        stock_admin_user = User()
        stock_admin_user.name = uName
        stock_admin_user.login = uLogin
        stock_admin_user.main_company = company

        Group = proteus.Model.get('res.group')
        stock_admin_group, = Group.find([('name', '=', uGroup)])
        stock_admin_user.groups.append(stock_admin_group)
        stock_admin_user.save()
    assert User.find([('name', '=', uName)])

@step('Create a new stock.location named "{uName}" of type warehouse')
def step_impl(context, uName):
    """
    Given \
    Create a new stock.location named "{uName}" of type warehouse"
    """
    current_config = context.oProteusConfig

# these can take a lot of fields including address

    Location = proteus.Model.get('stock.location')
    if not Location.find([('name', '=', uName)]):
        uCode = uName.split()[0]

        output_loc = Location()
        output_loc.name = uName + ' Output'
        output_loc.type = 'storage'
        output_loc.code = uCode+'OUT'
        output_loc.save()

        storage_loc = Location()
        storage_loc.name = uName + ' Storage'
        storage_loc.type = 'storage'
        storage_loc.code = uCode+'STO'
        storage_loc.save()

        input_loc = Location()
        input_loc.name = uName + ' Input'
        input_loc.type = 'storage'
        input_loc.code = uCode+'IN'
        input_loc.save()

        warehouse_loc = Location()
        warehouse_loc.name = uName
        warehouse_loc.type = 'warehouse'
        warehouse_loc.code = uCode+'WH'
        warehouse_loc.input_location = input_loc
        warehouse_loc.output_location = output_loc
        warehouse_loc.storage_location = storage_loc
        warehouse_loc.save()

    warehouse_loc, = Location.find([('name', '=', uName)])

# 'Provisioning Location', 'storage', 'WH'
@step('Create a new stock.location named "{uName}" of type "{uType}" of parent with code "{uParent}"')
def step_impl(context, uName, uType, uParent):
    """
    Given \
    Create a new stock.location named "{uName}" of type "{uType}" of parent with code "{uParent}"
    """
    current_config = context.oProteusConfig

# these can take a lot of fields including address

    # FixMe:
    #  config.user = stock_admin_user.id
    Location = proteus.Model.get('stock.location')
    if not Location.find([('name', '=', uName)]):
        # WH only?
        uCode = uName.split()[0]

        provisioning_loc = Location()
        provisioning_loc.name = uName
        provisioning_loc.code = uCode
        provisioning_loc.type = uType
        if uParent:
            storage_loc, = Location.find([('code', '=', uParent)])
            provisioning_loc.parent = storage_loc
        provisioning_loc.save()

    oLocation, = Location.find([('name', '=', uName)])


@step('Add to inventory as user named "{uUser}" with storage at the location coded "{uCode}" ProductTemplates with |product|quantity|expected_quantity| fields')
def step_impl(context, uUser, uCode):
    """
    Given \
    Create an Inventory as user named "{uUser}"
    with storage at the location with code "{uCode}"
    The following fields are the name of the product and the
    quantity and expected_quantity as floats.
    | name | quantity | expected_quantity |
    | product | 100.0    | 0.0               |
    """
    config = context.oProteusConfig

    User = proteus.Model.get('res.user')
    Inventory = proteus.Model.get('stock.inventory')
    Location = proteus.Model.get('stock.location')
    Product = proteus.Model.get('product.product')

    stock_user, = User.find([('name', '=', uUser)])
    proteus.config.user = stock_user.id
    inventory, = Inventory.find([('location.code', '=', uCode)])

    InventoryLine = proteus.Model.get('stock.inventory.line')
    for row in context.table:
        product, = Product.find([('name','=', row['name'])])
        inventory_line = InventoryLine(product=product, inventory=inventory)
        inventory_line.quantity = float(row['quantity'])
        inventory_line.expected_quantity = float(row['expected_quantity'])
        inventory.save()
        inventory_line.save()

    Inventory.confirm([inventory.id], config.context)
    assert inventory.state == u'done'
    admin_user = User(0)
    proteus.config.user = admin_user.id

@step('Create an Inventory as user named "{uUser}" with storage at the location coded "{uCode}"')
def step_impl(context, uUser, uCode):
    """
    Given \
    Create an Inventory as user named "{uUser}"
    with storage at the location with code "{uCode}"
    """
    config = context.oProteusConfig

    User = proteus.Model.get('res.user')
    Inventory = proteus.Model.get('stock.inventory')
    Location = proteus.Model.get('stock.location')

    stock_user, = User.find([('name', '=', uUser)])
    proteus.config.user = stock_user.id
    if not Inventory.find([('location.code', '=', uCode)]):
        storage, = Location.find([
                    ('code', '=', uCode),
                    ])
        inventory = Inventory()
        inventory.location = storage
        inventory.save()
    inventory, = Inventory.find([('location.code', '=', uCode)])
    admin_user = User(0)
    proteus.config.user = admin_user.id

@step('Stock Move of Product with description "{uProductDescription}" between locations with |name|value| fields')
def step_impl(context, uProductDescription):
    """
    Stock Move of Product with description "uProductDescription" \
    between locations with |name|value| fields
    | name              | value |
    | uom 	        | unit  |
    | quantity 	        | 1     |
    | from_location 	| SUP   |
    | to_location 	| STO   |
    | planned_date 	| TODAY |
    | effective_date 	| TODAY |
    | unit_price 	| 100   |
    | currency 		| USD   |
    """
    Product = proteus.Model.get('product.product')
    product, = Product.find([('description', '=', uProductDescription)])
    vStockMoveOfProductOrTemplate(context, product)

@step('Stock Move of ProductTemplate named "{uProductTemplate}" between locations with |name|value| fields')
@step('Stock Move of product of ProductTemplate named "{uProductTemplate}" between locations with |name|value| fields')
def step_impl(context, uProductTemplate):
    """
    Stock Move of product of ProductTemplate named "uProductTemplate" \
    between locations with |name|value| fields
    | name              | value |
    | uom 	        | unit  |
    | quantity 	        | 1     |
    | from_location 	| SUP |
    | to_location 	| STO |
    | planned_date 	| TODAY |
    | effective_date 	| TODAY |
    | unit_price 	| 100 |
    | currency 		| USD |

    Locations are location codes, not names.
    """
    ProductTemplate = proteus.Model.get('product.template')
    product, = ProductTemplate.find([('name', '=', uProductTemplate)])
    vStockMoveOfProductOrTemplate(context, product)

def vStockMoveOfProductOrTemplate(context, product):
    config = context.oProteusConfig
    StockMove = proteus.Model.get('stock.move')

    Party = proteus.Model.get('party.party')
    sCompanyName = sGetFeatureData(context, 'party,company_name')
    party, = Party.find([('name', '=', sCompanyName)])
    Company = proteus.Model.get('company.company')
    company, = Company.find([('party.id', '=', party.id)])

    Location = proteus.Model.get('stock.location')

    # should be ProductTemplate ? - nope, must be name
    # Product.find([('name', '=', uProductTemplate)]) works
    # ProductTemplate.find([('name', '=', uProductTemplate)]) works
    # ProductTemplate.find([])[0].name works
    # ProductTemplate.find([])[0].name works
    # but Product.find([])[0].name errors
    # and Product.find([('description', '=', uProductTemplate)]) is empty

    incoming_move = StockMove()
    incoming_move.product = product
    incoming_move.company = company

    for row in context.table:
        if row['name'] == 'from_location':
            loc, = Location.find([('code', '=', row['value'])])
            incoming_move.from_location = loc
        elif row['name'] == 'to_location':
            loc, = Location.find([('code', '=', row['value'])])
            incoming_move.to_location = loc
        elif row['name'] == 'planned_date':
            uDate = row['value']
            if uDate.lower() == 'today' or uDate.lower() == 'now':
                oDate = TODAY
            else:
                oDate = datetime.date(*map(int, uDate.split('-')))
            incoming_move.planned_date = oDate
        elif row['name'] == 'effective_date':
            uDate = row['value']
            if uDate.lower() == 'today' or uDate.lower() == 'now':
                oDate = TODAY
            else:
                oDate = datetime.date(*map(int, uDate.split('-')))
            incoming_move.effective_date = oDate
        else:
            gValue = string_to_python(row['name'], row['value'], StockMove)
            setattr(incoming_move, row['name'], gValue )

    incoming_move.save()
    StockMove.do([incoming_move.id], config.context)

@step('Stock Internal Shipment of ProductTemplate named "{uProductTemplate}" between locations with |name|value| fields')
def step_impl(context, uProductTemplate):
    """
    Given \
    Stock Internal Shipment of product of ProductTemplate named "uProductTemplate" \
    between locations with |name|value| fields
    | name              | value |
    | uom 	        | unit  |
    | quantity 	        | 1     |
    | from_location 	| SUP   |
    | to_location 	| STO   |
    | planned_date 	| TODAY |
    | effective_date 	| TODAY |

    Locations are location codes, not names.
    """
    ProductTemplate = proteus.Model.get('product.template')
    product, = ProductTemplate.find([('name', '=', uProductTemplate)])
    vStockInternalShipmentOfProductOrTemplate(context, product)

@step('Stock Internal Shipment of Product with description "{uProductDescription}" between locations with |name|value| fields')
def step_impl(context, uProductDescription):
    """
    Given \
    Stock Internal Shipment of product of Product \
    with description  "uProductDescription" \
    between locations with |name|value| fields
    | name              | value |
    | uom 	        | unit  |
    | quantity 	        | 1     |
    | from_location 	| SUP   |
    | to_location 	| STO   |
    | planned_date 	| TODAY |
    | effective_date 	| TODAY |

    Locations are location codes, not names.
    """
    Product = proteus.Model.get('product.product')
    product, = Product.find([('description', '=', uProductDescription)])
    vStockInternalShipmentOfProductOrTemplate(context, product)

def vStockInternalShipmentOfProductOrTemplate(context, product):
    config = context.oProteusConfig
    StockInternalShipment = proteus.Model.get('stock.shipment.internal')

    Party = proteus.Model.get('party.party')
    sCompanyName = sGetFeatureData(context, 'party,company_name')
    party, = Party.find([('name', '=', sCompanyName)])
    Company = proteus.Model.get('company.company')
    company, = Company.find([('party.id', '=', party.id)])

    Location = proteus.Model.get('stock.location')

    # should be ProductTemplate ? - nope, must be name
    # Product.find([('name', '=', uProductTemplate)]) works
    # ProductTemplate.find([('name', '=', uProductTemplate)]) works
    # ProductTemplate.find([])[0].name works
    # ProductTemplate.find([])[0].name works
    # but Product.find([])[0].name errors
    # and Product.find([('description', '=', uProductTemplate)]) is empty
    internal_shipment = StockInternalShipment()

    for row in context.table:
        if row['name'] == 'from_location':
            loc, = Location.find([('code', '=', row['value'])])
            internal_shipment.from_location = loc
        elif row['name'] == 'to_location':
            loc, = Location.find([('code', '=', row['value'])])
            internal_shipment.to_location = loc
        elif row['name'] == 'planned_date':
            uDate = row['value']
            if uDate.lower() == 'today' or uDate.lower() == 'now':
                oDate = TODAY
            else:
                oDate = datetime.date(*map(int, uDate.split('-')))
            internal_shipment.planned_date = oDate
        elif row['name'] == 'effective_date':
            uDate = row['value']
            if uDate.lower() == 'today' or uDate.lower() == 'now':
                oDate = TODAY
            else:
                oDate = datetime.date(*map(int, uDate.split('-')))
            internal_shipment.effective_date = oDate
        else:
            gValue = string_to_python(row['name'], row['value'], StockInternalShipment)
            setattr(internal_shipment, row['name'], gValue )

    internal_shipment.save()
    if not StockInternalShipment.assign_try([internal_shipment.id], current_config.context):
        sys.__stderr__.write('>>> WARN: forcing internal shipment on '+uDate+'\n')
        StockInternalShipment.assign_force([internal_shipment.id], current_config.context)
    StockInternalShipment.done([internal_shipment.id], config.context)
    internal_shipment.reload()

@step('Purchase on date "{uDate}" stock with description "{uDescription}" with their reference "{uRef}" as user named "{uUser}" in Currency coded "{uCur}" Products from supplier "{uSupplier}" to warehouse "{uWh}" with PaymentTerm "{uTerm}" and InvoiceMethod "{uMethod}" with |description|quantity|line_description|unit_price| fields')
def step_impl(context, uDate, uDescription, uRef, uUser, uCur, uSupplier, uWh, uTerm, uMethod):
    """
    Given \
    Purchase on date "TODAY" stock with description "Description"
    as user named "Purchase" Products from supplier "Supplier"
    to warehouse "WH"
    with PaymentTerm "Direct" and InvoiceMethod "order"
    If the quantity is the word comment, the line type is set to comment.
    with |description|quantity|line_description| fields
      | description | quantity | line_description | unit_price |
      | product | 2.0      |             | 10.00 |
      | product | comment  | Comment     |       |
      | product | 3.0      |             | 10.00 |
    """
    oPurchaseProducts(context, uDate, uDescription, uRef, uUser, uCur, uSupplier, uWh, uTerm, uMethod)

@step('Purchase on date "{uDate}" stock with description "{uDescription}" with their reference "{uRef}" as user named "{uUser}" in Currency coded "{uCur}" Products from supplier "{uSupplier}" to warehouse "{uWh}" with PaymentTerm "{uTerm}" and InvoiceMethod "{uMethod}" with |description|quantity|line_description| fields')
def step_impl(context, uDate, uDescription, uRef, uUser, uCur, uSupplier, uWh, uTerm, uMethod):
    """
    Given \
    Purchase on date "TODAY" stock with description "Description"
    as user named "Purchase" in Currency coded "uCur"
    Products from supplier "Supplier" to warehouse "WH"
    with PaymentTerm "Direct" and InvoiceMethod "order"
    If the quantity is the word comment, the line type is set to comment.
    with |description|quantity|line_description| fields
      | description | quantity | line_description |
      | product | 2.0      |             |
      | product | comment  | Comment     |
      | product | 3.0      |             |
    """
    oPurchaseProducts(context, uDate, uDescription, uRef, uUser, uCur, uSupplier, uWh, uTerm, uMethod)

def oPurchaseProducts(context, uDate, uDescription, uRef, uUser, uCur, uSupplier, uWh, uTerm, uMethod):
    # should we make quantity == 'comment'
    config = context.oProteusConfig

    Purchase = proteus.Model.get('purchase.purchase')

    Party = proteus.Model.get('party.party')
    sCompanyName = sGetFeatureData(context, 'party,company_name')
    party, = Party.find([('name', '=', sCompanyName)])
    Company = proteus.Model.get('company.company')
    company, = Company.find([('party.id', '=', party.id)])

    Product = proteus.Model.get('product.product')
    supplier, = Party.find([('name', '=', uSupplier),])

    PaymentTerm = proteus.Model.get('account.invoice.payment_term')
    payment_term, = PaymentTerm.find([('name', '=', uTerm)])

    if not Purchase.find([('description', '=', uDescription),
                          ('company.id',  '=', company.id),
                          ('party.id', '=', supplier.id)]):
        try:
            if uUser != u'Administrator':
                User = proteus.Model.get('res.user')
                purchase_user, = User.find([('name', '=', uUser)])
                proteus.config.user = purchase_user.id

            purchase = Purchase()
            purchase.party = supplier
            purchase.payment_term = payment_term
            purchase.invoice_method = uMethod
            purchase.description = uDescription
            purchase.supplier_reference = uRef

            Location = proteus.Model.get('stock.location')
            oWh, = Location.find([('name', '=', uWh),
                                  ('type', '=', 'warehouse')])
            purchase.warehouse = oWh

            Currency = proteus.Model.get('currency.currency')
            oCurrency, = Currency.find([('code', '=', uCur)])
            purchase.currency = oCurrency

            if uDate.lower() == 'today' or uDate.lower() == 'now':
                oDate = TODAY
            else:
                oDate = datetime.date(*map(int, uDate.split('-')))
            purchase.purchase_date = oDate
            #? purchase.save()

            PurchaseLine = proteus.Model.get('purchase.line')
            for row in context.table:
                purchase_line = PurchaseLine()
                # BUG? Product.find([('name' should FAIL
                product, = Product.find([('description', '=', row['description'])])
                if product.rec_name.find('Kg') >= 0:
                    if product.default_uom.digits < 3:
                        # FixMe: maybe unneeded because of use of Kilogramme
                        product.default_uom.digits = 3
                    # FixMe: maybe unneeded because of the line above - nope
                    purchase_line.unit_digits = 3
                #  delivery_date
                purchase.lines.append(purchase_line)
                purchase_line.product = product
                if row['quantity'] == 'comment':
                    purchase_line.type = 'comment'
                else:
                    # type == 'line' float?!
                    purchase_line.quantity = Decimal(row['quantity'])
                    if u'unit_price' in context.table.headings:
                        purchase_line.unit_price = Decimal(row['unit_price'])
                if row['line_description']:
                    purchase_line.description = row['line_description']

            purchase.save()
        finally:
            if uUser != 'Administrator':
                user, = User.find([('login', '=', 'admin')])
                proteus.config.user = user.id

    purchase, = Purchase.find([('description', '=', uDescription),
                               ('company.id',  '=', company.id),
                               ('party.id', '=', supplier.id)])
    return purchase
