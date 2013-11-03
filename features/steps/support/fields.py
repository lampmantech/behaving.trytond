# -*- encoding: utf-8 -*-

"""
Convenience functions.
"""

import datetime
import time
from decimal import Decimal
from proteus import config, Model, Wizard

def string_to_python (sField, sValue, Party=None):
    #? should replace this with DSL
    
    if Party is None: 
        sType = ''
    else:
        dFields = Party._fields
        assert dFields
        assert sField in dFields.keys(), \
               "Unknown field %s; not in %r" % (sField, dFields.keys(),)
        dField = dFields[sField]
        assert 'type' in dField.keys()
        sType = dField['type']

    if sType == 'boolean' or sField in ['active']:
        if sValue.lower() in ('false', 'nil'): return False
        if sValue.lower() in ('true'): return True
    if sType == 'numeric' or sField.endswith('_price'):
        return Decimal(sValue)
    if sType in ('char', 'text',) or sField in ['name']:
        return sValue
    if sType == 'integer':
        return int(sValue)
    if sType == 'float':
        return int(sValue)
    if sType == 'date' or sField.endswith('_date'):
        # tryton wants a datetime.date object?
        if sValue == 'TODAY': return datetime.date.today()
        return datetime.date(*map(int,sValue.split('-')))

    if sType == 'time':
        # FixMe: wants a datetime.datetime object?
        if sValue == 'TODAY': return datetime.datetime.today()
        return datetime.datetime(*map(int,sValue.split('-')))

    # give up or error?
    if sType == '': return sValue
    
    assert 'searchable' in dField.keys(), \
           "Sorry, dont know how to look in slots of %s " % (sField,)
    assert dField['searchable']
    assert 'relation' in dField.keys()
    sRelation = dField['relation']
    #? FixMe: if sType == 'many2one':
        
    # FixMe: assume name for now
    Klass = Model.get(sRelation)
    #? name or code
    lElts = Klass.find([('name', '=', sValue)])
    assert len(lElts) != 0, \
           "No instance of %s found named '%s'" % (sRelation, sValue,)
    assert len(lElts) == 1, \
           "Too many instances of %s found named '%s'" % (sRelation, sValue,)
    return lElts[0]
