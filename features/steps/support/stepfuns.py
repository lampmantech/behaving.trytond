# -*- mode: python; py-indent-offset: 4; coding: utf-8-unix; encoding: utf-8 -*-

"""
stepfuns has some convenience funtions used within steps.

"""
import proteus

import time
import datetime
from dateutil.relativedelta import relativedelta
from decimal import Decimal
import hashlib

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
    so the module "account_stock_anglo_saxon" is required
    unless you create them yourself.
    """
    Account = proteus.Model.get('account.account')
    # Fixme:             ('kind', '=', 'stock'), should be flagged early
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

def oAttachLinkToFileToResource(oResource, uFile):
    sLink = 'file://' + uFile
    sDescription = uFile
    # ToDo cannonicalize the filename
    # Use a md5 of the filename to make it unique
    # This is the filename that will be used by the
    # Tryton server when it stores it on disk.
    sName = hashlib.md5(uFile).hexdigest()
    try:
        oAttachment = oAttachLinkToResource (sName, sDescription, sLink, oResource)
        return oAttachment
    except Exception, e:
        sys.__stderr__.write(">>> ERROR: creating link, %s,\n%s\n%s\n" % (
            str(e), uFile, sName,))


def oAttachFeatureFileContentToResource(oResource, context):
    uFile = context.scenario.filename
    return oAttachFileContentToResource(oResource, uFile)

def oAttachFileContentToResource(oResource, uFile):
    sLink = 'file://' + uFile
    with open(uFile, 'rt') as oFd:
        sDescription = oFd.read()
        
    # ToDo cannonicalize the filename
    # Use a sha of the filename to make it unique
    sName = hashlib.sha1(uFile).hexdigest()
    try:
        oAttachment = oAttachLinkToResource (sName, sDescription, sLink, oResource)
        return oAttachment
    except Exception, e:
        sys.__stderr__.write(">>> ERROR: creating link, %s,\n%s\n%s\n" % (
            str(e), uFile, sName,))


def oAttachLinkToResource(sName, sDescription, sLink, oResource):
    """
    Attach to an existing instance "{uResource}" a link to
    to something with a name sName and description sDescription.
    Updates the fields if the named attachment exists.
    Idempotent.
    """
    Attachment = proteus.Model.get('ir.attachment')

    #? oResource.__class__.rec_name
    #? oResource.__class__.name
    l = Attachment.find([('type', '=', 'link'), ('name', '=', sName)])
    if not l:
        oAttachment = Attachment(type='link')
    else:
        oAttachment = l[0]
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

def vSetDescribedInstanceFields(context, uName, uKlass):
    # e.g. account.invoice
    vSetNamedInstanceFields(context, uName, uKlass, 'description')
    
def vSetNamedInstanceFields(context, uName, uKlass, sSlot='name'):
    assert context.table, "Please supply a table of |name|value| fields"
    if hasattr(context.table, 'headings'):
        # if we have a real table, ensure it has 2 columns
        # otherwise, we will just fail during iteration
        assert len(context.table.headings) >= 2

    Klass = proteus.Model.get(uKlass)
    oInstance, = Klass.find([(sSlot, '=', uName)])
    for row in context.table:
        setattr(oInstance, row['name'],
                string_to_python(row['name'], row['value'], Klass))
    oInstance.save()

