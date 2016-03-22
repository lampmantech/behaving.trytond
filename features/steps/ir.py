# -*- mode: python; py-indent-offset: 4; coding: utf-8-unix; encoding: utf-8 -*-
"""

Test the core trytond/ir/ functionalities.

1) Try to make an attachment in the form on a link


"""
import random, os, sys

import proteus

from behave import *

from .support import stepfuns
from .support.tools import *

@step('ir/attachment test')
def step_impl(context):
    """
    Try to make an attachment in the form of a link
    onto the admin user. Not working.
    FixMe:
    """
    User = proteus.Model.get('res.user')

    oUser = User.find([('login', '=', 'admin')])[0]

    oResource = oUser
    sFile = os.path.join(os.path.dirname(__file__), 'environment.cfg')
    sLink = 'file://' + sFile
    sDescription = 'Test Link to ' + sFile
    sName = 'Test Link %d' % int(random.random() * 1000000)

    oAttachment = stepfuns.oAttachLinkToResource(sName, sDescription, sLink, oResource)

    assert oAttachment.resource == oUser,  str(oAttachment.resource) +" not == " +str(oUser)

@step('Attach to an instance named "{uName}" of class "{uClass}" the content of this feature file')
def step_impl(context, uName, uClass):
    uFile = context.feature.filename
    # FixMe: this can be a relative filename; need to add
    # os.path.dirname(__file__)
    context.execute_steps(u'''
    Given Attach to an instance named "%s" of class "%s" a link to an existing file with the following |filename| fields
    | filename |
    | %s |
''' % (uName, uClass, uFile))


# This wont work with a table and  context.execute_steps
@step('Attach to an instance named "{uName}" of class "{uClass}" a link to an existing file with the following |filename| fields')
def step_impl(context, uName, uClass):
    assert context.table
    Class = proteus.Model.get(uClass)
    uField = 'name'
    
    # FixMe: were not ready for account.move from account.voucher yet
    try:
        oResources = Class.find([(uField, '=', uName)])
    except KeyError:
        return
    else:
        if not oResources:
            return
    oResource = oResources[0]
    assert context.table
    bNeedSave = False
    for row in context.table:
        uFile = row['filename']
        o = stepfuns.oAttachLinkToFileToResource(oResource, uFile)
        if o: bNeedSave = True
    if bNeedSave and hasattr(oResource, 'save'):
        #?
        oResource.save()

@step('Attach to an instance with field "{uField}" "{uValue}" of class "{uClass}" a link to an existing file with the following |filename| fields')
def step_impl(context, uField, uValue, uClass):
    """
    Given \
    Attach to an existing instance with name "{uName}" of class "{uClass}" \
    a link to an existing file with the following |filename| fields
    """
    Class = proteus.Model.get(uClass)

    # FixMe: were not ready for account.move from account.voucher yet
    try:
        oResources = Class.find([(uField, '=', uValue)])
    except KeyError:
        return
    else:
        if not oResources:
            return
    oResource = oResources[0]
    assert context.table
    for row in context.table:
        uFile = row['filename']
        stepfuns.oAttachLinkToFileToResource(oResource, uFile)

@step('Attach to an instance with field "{uField}" "{uValue}" of class "{uClass}" the content of an existing file with the following |filename| fields')
def step_impl(context, uField, uValue, uClass):
    """
    Given \
    Attach to an existing instance with name "{uName}" of class "{uClass}" \
    the content of an existing file with the following |filename| fields
    """
    Class = proteus.Model.get(uClass)

    oResource = Class.find([(uField, '=', uValue)])[0]
    assert context.table
    for row in context.table:
        uFile = row['filename']
        assert os.path.exists(uFile), "Does not exist: " +uFile
        o = stepfuns.oAttachFileContentToResource(oResource, uFile)
        assert o

@step('Prefix all Strict Sequences of code "{uCode}" with the year')
def step_impl(context, uCode):
    """
    Prefix all Strict Sequences of code "Invoice" with the year
    """
    SequenceStrict = proteus.Model.get('ir.sequence.strict')
    lElts = SequenceStrict.find([('code', '=', uCode)])
    #! assert lElts
    for oElt in lElts:
        if not oElt.prefix:
            oElt.prefix = "${year}-"
        if not oElt.padding:
            oElt.padding = 2
        oElt.save()
