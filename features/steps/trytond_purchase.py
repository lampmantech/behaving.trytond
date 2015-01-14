# -*- encoding: utf-8 -*-
"""


"""
from behave import *
import proteus

import datetime
from decimal import Decimal

from .support.fields import string_to_python, sGetFeatureData, vSetFeatureData
from .support import modules
from .support.tools import *

today = datetime.date.today()

@step('Create a Purchase Order with description "{uDescription}" from supplier "{uSupplier}" with fields')
def step_impl(context, uDescription, uSupplier):
    """
    Create a Purchase Order from a supplier with a description.
    It expects a |name|value| table; the fields typically include:
    'payment_term', 'invoice_method', 'purchase_date', 'currency'
	  | invoice_method    | shipment |
	  | payment_term      | Direct 	 |
	  | purchase_date     | TODAY	 |
	  | currency          | EUR	 |
    Idempotent.
    """
    current_config = context.oProteusConfig

    Purchase = proteus.Model.get('purchase.purchase')

    Party = proteus.Model.get('party.party')
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


