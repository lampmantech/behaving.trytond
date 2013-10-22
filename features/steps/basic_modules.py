# -*- encoding: utf-8 -*-
"""
This is the elementary test of Trytons basic modules.

If this test fails, trytond is not properly installed.
"""

from behave import *
from proteus import Model
from .support import modules
from .support import tools

@given('we have proteus installed')
def step_impl(context):
    assert context.oProteusConfig

@step('Ensure that the "{mod}" module is loaded')
def step_impl(context, mod):
    lRetval = modules.lInstallModules([mod], context.oProteusConfig)

@step('the "{mod}" module is in the list of loaded modules')
def step_impl(context, mod):
    assert mod in modules.lInstalledModules(), \
           "%s NOT in %r" % (mod, modules.lInstalledModules(),)

@step('we print the list of loaded modules')
def step_impl(context):
    tools.puts(repr(modules.lInstalledModules()))

# party.party
@step('we have the following table of "{mod}" instances')
def step_impl(context, mod):
    Module = Model.get(mod)
    parties = [x.name for x in Module.find()]
    for row in context.table:
        name=row['name']
        if name in parties: continue
        party = Module()
        party.name=name
        party.save()
        assert party.id > 0


@then('there are some instances of "{mod}"')
def step_impl(context, mod):
    Module = Model.get(mod)
    parties = [x.name for x in Module.find([])]
    assert parties
