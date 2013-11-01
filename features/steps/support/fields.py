# -*- encoding: utf-8 -*-

"""
Convenience functions.
"""

import datetime
import time
from decimal import Decimal
from proteus import config, Model, Wizard

def string_to_python (sField, sValue):
    # Grody - should replace this with DSL
    
    if sField in ['salable', 'purchasable']:
        if sValue in ['True', 'true']: return True
        if sValue in ['False', 'false']: return False
    if sField in ['list_price', 'cost_price'] or sField.endswith('_price'):
        return Decimal(sValue)
    if sField in ['name', 'reference'] or sField.endswith('_method'):
        return sValue
    if sField in ['delivery_time']:
        # days
        return int(sValue)
    # slippery slope
    if sField in ['purchase_date'] or sField.endswith('_date'):
        # tryton wants a datetime.date object?
        if sValue == 'TODAY': return datetime.date.today()
        return datetime.date(*map(int,sValue.split('-')))

    if sField in ['payment_term']:
        PaymentTerm = Model.get('account.invoice.payment_term')
        payment_term, = PaymentTerm.find([('name', '=', sValue)])
        return payment_term

    if sField in ['currency']:
        Currency = Model.get('currency.currency')
        #? name or code
        currency, = Currency.find([('name', '=', sValue)])
        return currency
        
    if sValue.lower() in ('false', 'nil'): return False
    if sValue.lower() in ('true'): return True

    return sValue

