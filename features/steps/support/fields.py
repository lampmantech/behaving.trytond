# -*- encoding: utf-8 -*-

"""
Convenience functions.
"""

from decimal import Decimal

def string_to_python (sField, sValue):
    # Grody - should look it up on the field from trytond
    if sField in ['salable', 'purchasable']:
        if sValue in ['True', 'true']: return True
        if sValue in ['False', 'false']: return False
    if sField in ['list_price', 'cost_price'] or sField.endswith('_price'):
        return Decimal(sValue)
    if sField in ['name', 'cost_price_method']:
        return sValue
    if sField in ['delivery_time']:
        return int(sValue)

    if sValue in ['True', 'true']: return True
    if sValue in ['False', 'false']: return False

    return sValue

