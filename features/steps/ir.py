# -*- encoding: utf-8 -*-
"""

Test the core trytond/ir/ functionalities.

1) Try to make an attachment in the form on a link


"""
from behave import *
import proteus
import random, os, sys

from .support.stepfuns import oAttachLinkToResource

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

    oAttachment = oAttachLinkToResource (sName, sDescription, sLink, oResource)

    assert oAttachment.resource == oUser
