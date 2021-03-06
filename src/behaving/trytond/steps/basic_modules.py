# -*- mode: python; py-indent-offset: 4; coding: utf-8-unix; encoding: utf-8 -*-
"""
This is the elementary test of Trytons basic modules.

If this test fails, trytond is not properly installed.
"""

from behave import *
import proteus
from .support import modules
from .support import tools
from .support.stepfuns import vAssertContentTable

@step('we have proteus installed')
def we_have_proteus_installed(context):
    assert context.oProteusConfig

@step('Ensure that the "{mod}" module is loaded')
def step_impl(context, mod):
    """
    Load the "{mod}" module if it is not already loaded.
    Idempotent.
    """
    lRetval = modules.lInstallModules([mod], context.oProteusConfig)

@step('the "{mod}" module is in the list of loaded modules')
def step_impl(context, mod):
    assert mod in modules.lInstalledModules(), \
           "%s NOT in %r" % (mod, modules.lInstalledModules(),)

@step('we print the list of loaded modules')
def step_impl(context):
    """
    Print the list of loaded modules on behave's stdout.
    """
    tools.puts(repr(modules.lInstalledModules()))

@step('Ensure that the WebDAV modules are loaded')
def step_impl(context):
    """
    Given \
    Ensure that the WebDAV modules are loaded

    So that we can access the calendars and contacts via WebDAV
    """
    context.execute_steps(u'''
    Given Ensure that the "%s" module is loaded
    ''' % ('party_vcarddav',))

# party.party
@step('we have the following table of "{mod}" instances')
def step_impl(context, mod):
    """
    Creates the instances of the Model 'uMod' with the names from the table.
    It expects a |name| table.
    Idempotent.
    """
    Module = proteus.Model.get(mod)
    parties = [x.name for x in Module.find()]
    for row in context.table:
        name=row['name']
        if name in parties: continue
        party = Module()
        party.name=name
        party.save()
        assert party.id > 0


@step('there are some instances of "{uMod}"')
def there_are_some_instances_of(context, uMod):
    """
    Asserts that there are some instances of the Model 'uMod'.
    Idempotent.
    """
    Module = proteus.Model.get(uMod)
    lParties = [x.name for x in Module.find([])]
    assert lParties
