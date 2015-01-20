# -*- encoding: utf-8 -*-

"""
stepfuns has some convenience funtions used within steps.

"""

import time
import datetime
from dateutil.relativedelta import relativedelta
from decimal import Decimal
import proteus

from .fields import string_to_python, sGetFeatureData, vSetFeatureData

def gGetFeaturesRevExp(context, company):
        Account = proteus.Model.get('account.account')
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
        return revenue, expense

def gGetFeaturesPayExp(context, company):
    Account = proteus.Model.get('account.account')
    payable, = Account.find([
        ('kind', '=', 'payable'),
        ('name', '=', sGetFeatureData(context, 'account.template,main_payable')),
        ('company', '=', company.id),
        ])
    expense, = Account.find([
        ('kind', '=', 'expense'),
        ('name', '=', sGetFeatureData(context, 'account.template,main_expense')),
        ('company', '=', company.id),
        ])
    return payable, expense

def gGetFeaturesPayRec(context, company):
    Account = proteus.Model.get('account.account')
    payable, = Account.find([
        ('kind', '=', 'payable'),
        ('name', '=', sGetFeatureData(context, 'account.template,main_payable')),
        ('company', '=', company.id),
        ])
    receivable, = Account.find([
        ('kind', '=', 'receivable'),
        ('name', '=', sGetFeatureData(context, 'account.template,main_receivable')),
        ('company', '=', company.id),
        ])
    return payable, receivable

def gGetFeaturesStockAccs(context, company):
        """
        These are in by trytond_account_stock_continental/account.xml
        which is pulled in by trytond_account_stock_anglo_saxon
        """
        Account = proteus.Model.get('account.account')
        stock, = Account.find([
            ('kind', '=', 'stock'),
            ('company', '=', company.id),
            ('name', '=', sGetFeatureData(context, 'account.template,stock')),
            ])
        stock_customer, = Account.find([
            ('kind', '=', 'stock'),
            ('company', '=', company.id),
            ('name', '=', sGetFeatureData(context, 'account.template,stock_customer')),
            ])
        stock_lost_found, = Account.find([
            ('kind', '=', 'stock'),
            ('company', '=', company.id),
            ('name', '=', sGetFeatureData(context, 'account.template,stock_lost_found')),
            ])
        stock_production, = Account.find([
            ('kind', '=', 'stock'),
            ('company', '=', company.id),
            ('name', '=', sGetFeatureData(context, 'account.template,stock_production')),
            ])
        stock_supplier, = Account.find([
            ('kind', '=', 'stock'),
            ('name', '=', sGetFeatureData(context, 'account.template,stock_supplier')),
            ('company', '=', company.id),
            ])
        return stock, stock_customer, stock_lost_found, \
            stock_production, stock_supplier, 

def oAttachLinkToResource (sName, sDescription, sLink, oResource):
        
    Attachment = proteus.Model.get('ir.attachment')
    oAttachment = Attachment()

    oAttachment.type = 'link'
    oAttachment.name = sName
    oAttachment.description = sDescription
    oAttachment.link = sLink
    oAttachment.resource = oResource
    oAttachment.save()
    
    return oAttachment

def vAssertContentTable(context, iMin=2):
    assert context.table, "Please supply a table of field name and values"
    if hasattr(context.table, 'headings'):
        # if we have a real table, ensure it has 2 columns
        # otherwise, we will just fail during iteration
        assert len(context.table.headings) >= iMin

def vCreatePartyWithPayRec(context, uName, company):
    Party = proteus.Model.get('party.party')
    Company = proteus.Model.get('company.company')

    if not Party.find([('name', '=', uName)]):
        payable, receivable = gGetFeaturesPayRec(context, company)
        customer = Party(name=uName)
        customer.account_payable = payable
        customer.account_receivable = receivable
        customer.save()

    assert Party.find([('name', '=', uName)])
        
def vSetNamedInstanceFields(context, uName, uKlass):
    assert context.table, "Please supply a table of |name|value| fields"
    if hasattr(context.table, 'headings'):
        # if we have a real table, ensure it has 2 columns
        # otherwise, we will just fail during iteration
        assert len(context.table.headings) >= 2

    Klass = proteus.Model.get(uKlass)
    oInstance, = Klass.find([('name', '=', uName)])
    for row in context.table:
        setattr(oInstance, row['name'],
                string_to_python(row['name'], row['value'], Klass))
    oInstance.save()
        
