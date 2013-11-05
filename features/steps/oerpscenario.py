# -*- encoding: utf-8 -*-
"""
These are the elementary tests from OpenERPScenario:
 <http:///launchpad.net/~camptocamp/oerpscenario/>

The aim here is to make the same feature tests in OpenERPScenario
run in trytond_scenari on Tryton. YMMV!

UNFINISHED
"""

from behave import *

# module_config.py
# FixMe: UNFINISHED
@step('I do not want all demo data to be loaded on install')
def impl(ctx):
    """
    WIP
    """
    pass

# FixMe: UNFINISHED
@step('I update the module list')
def impl(ctx):
    """
    WIP
    """
    pass

from support import modules
@step('I install the required modules with dependencies')
def impl(ctx):
    """
    Install the required modules.
    It expects a |name| table.
    Idempotent.
    """
    # module_config.py
    to_install = []
    for row in ctx.table:
        to_install.append(row['name'])
    if to_install: lInstallModules(to_install, ctx.oProteusConfig)


@step('my modules should have been installed and models reloaded')
def impl(ctx):
    """
    Null.
    """
    # module_config.py
    pass

