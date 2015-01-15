# -*- encoding: utf-8 -*-
"""

Test the core trytond/ir/ functionalities.

1) Try to make an attachment in the form on a link


"""
from behave import *
from proteus import *
import random

from .support.stepfuns import oAttachLinkToResource

@step('ir/attachment test')
def step_impl(context):
    """
    Try to make an attachment in the form of a link
    onto the admin user. Not working.
    FixMe:
    """
    User = Model.get('res.user')
    
    oUser = User.find([('login', '=', 'admin')])[0]
    
    oResource = oUser
    sLink = 'file:///mnt/n/data/TrytonOpenERP/3.2/trytond_scenari/features/steps/ir.py'
    sDescription = 'Test Link to /n/data/TrytonOpenERP/3.2/trytond_scenari/features/steps/ir.py'
    sName = 'Test Link %d' % int(random.random() * 1000000)
    
    oAttachment = oAttachLinkToResource (sName, sDescription, sLink, oResource)
    
    assert oAttachment.resource == oUser
