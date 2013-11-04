# -*- encoding: utf-8 -*-

"""
Convenience functions.
"""

import datetime
import time
from decimal import Decimal
from proteus import config, Model, Wizard

def sGetFeatureData(context, sKey):
    assert sKey in context.dData['feature'], \
           "Use 'Set the feature data with values' to set the value of "+sKey
    return context.dData['feature'][sKey]

def vSetFeatureData(context, sKey, sValue):
    context.dData['feature'][sKey] = sValue

def string_to_python (sField, sValue, Party=None):
    #? should replace this with DSL
    
    if Party is None: 
        sType = ''
    else:
        dFields = Party._fields
        assert sField in dFields.keys(), \
               "ERROR: Unknown field %s; not in %r" % (sField, dFields.keys(),)
        dField = dFields[sField]
        assert 'type' in dField.keys(), \
               "PANIC: key %s; not in %r" % ('type', dFields.keys(),)
        sType = dField['type']

    if sType == 'boolean':
        if sValue.lower() in ('false', 'nil'): return False
        if sValue.lower() in ('true'): return True
    if sType == 'numeric' or sField.endswith('_price'):
        return Decimal(sValue)
    if sType in ('char', 'text', 'sha',) or sField in ['name',]:
        return sValue
    if sType == 'integer':
        return int(sValue)
    if sType == 'float':
        return int(sValue)
    if sType == 'selection':
        # FixMe: are selections always strings or can they be otherwise?
        # sSelection = dField['selection']
        return sValue
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

    #? This is not always true
    #assert 'searchable' in dField.keys(), \
    #       "Sorry, dont know how to look in slots of %s " % (sField,)
    #assert dField['searchable']
    
    assert 'relation' in dField.keys(), \
               "PANIC: key %s; not in %r" % ('relation', dFields.keys(),)
    sRelation = dField['relation']
    #? FixMe: if sType == 'many2one':
        
    # FixMe: assume name for now
    Klass = Model.get(sRelation)
    #? name or code
    lElts = Klass.find([('name', '=', sValue)])
    assert len(lElts) != 0, \
           "ERROR: No instance of %s found named '%s'" % (sRelation, sValue,)
    assert len(lElts) == 1, \
           "ERROR: Too many instances of %s found named '%s'" % (sRelation, sValue,)
    return lElts[0]
