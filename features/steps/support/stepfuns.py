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
