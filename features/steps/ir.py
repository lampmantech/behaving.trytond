# -*- encoding: utf-8 -*-
"""

Test the core trytond/ir/ functionalities.

1) Try to make an attachment in the form on a link


"""
from behave import *
from proteus import *
import random

@step('ir/attachment test')
def step_impl(context):
    """
    Try to make an attachment in the form of a link
    onto the admin user. Not working.
    FixMe:
    """
    Attachment = Model.get('ir.attachment')
    User = Model.get('res.user')
    
    admin = User.find([('login', '=', 'admin')])[0]
    
    attachment = Attachment()
    attachment.type = 'link'
    attachment.name = 'Test Link %d' % int(random.random() * 1000000)
    
    attachment.description = 'Test Link to /n/data/TrytonOpenERP/3.2/trytond_scenari/features/steps/ir.py'
    attachment.link = 'file:///mnt/n/data/TrytonOpenERP/3.2/trytond_scenari/features/steps/ir.py'
    attachment.resource = admin
    attachment.save()
    
    assert attachment.resource == admin
