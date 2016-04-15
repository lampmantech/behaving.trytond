# -*- encoding: utf-8 -*-
"""
This is the {{{environment.py}}} file  that is execed by behave before the
steps are run, to define the hooks for before and after features and steps.

There is a lot in here, that is used to parameterize the steps code
from {{{behaving.trytond}}} so that it is easier to use the behaving feature
files for more than just testing. We gather all of this parameterization
into a file {{{environment.cfg}}} that should sit beside the features
{{{environment.py}}} file. It lets you parameterize things like usernames,
passwords, and names of accounts in the accounting charts. 

So by simply editing the {{{environment.cfg}}} in the {{{tests/features/}}}
directory, you can adapt the features to entirely different charts of accounts
or use cases. In this way, the feature files can be used for loading
Tyrton with real-world test cases into real charts of accounts, not just tests.

You **must** edit the {{{environment.cfg}}} file before these tests will run,
as you have to set the Trytond {{{user/password/super_pwd}}} as well as
set the path to the {{{trytond.ini}}} file. Things will not work otherwise.

The test scenarios assume that they are run with the Postgres test database
freshly dropped, and will create it. Because the scenarios will be creating
a fresh Postgres test database, it will need the Postgress user and password
to create the database as. This is **not** set in the {{{environment.cfg}}}
for security reasons; set {{{PGPASSWORD}}} in the OS environment of caller
of {{{behave}}} to be the postgres password, and set {{{PGUSER}}} 
to be the postgres user.

Some of what is here may be old workarounds that are no longer needed.

"""

import sys, os
import ConfigParser

from trytond import __version__ as sTrytondVersion

from behaving.trytond import environment as tenv
from behaving.trytond.steps.support import tools, behave_better
from behaving.trytond.steps import ProteusConfig

# Some monkey patches to enhance Behave
# These should be reexamined to see if they are still needed.
behave_better.patch_all()

def oReadConfigFile():
    oEnvironmentCfg = ConfigParser.RawConfigParser()

    sFile = os.path.splitext(__file__)[0]+'.cfg'
    assert os.path.exists(sFile), \
        "ERROR: environment.cfg file not found: " + sFile
    oEnvironmentCfg.read(sFile)
    return oEnvironmentCfg


def before_all(context):
    """These run before and after the whole shooting match.
    """
    tenv.before_all(context)
    oEnvironmentCfg = oReadConfigFile()

    sAdminUser = oEnvironmentCfg.get('trytond', 'user')
    assert sAdminUser
    sDatabaseName = oEnvironmentCfg.get('trytond', 'database_name')
    assert sDatabaseName
    sAdminPassword = oEnvironmentCfg.get('trytond', 'password')
    assert sAdminPassword
    sDatabaseType = oEnvironmentCfg.get('trytond', 'database_type')
#?    assert sDatabaseType in ['postgresql'], "Unsupported database type: " + sDatabaseType
    sTrytonConfigFile = oEnvironmentCfg.get('trytond', 'config_file')
    assert os.path.exists(sTrytonConfigFile), \
        "ERROR: Tryton ini file not found: " + sTrytonConfigFile

    context.oEnvironmentCfg = oEnvironmentCfg
    if sTrytondVersion.startswith('3.2'):
        context.oProteusConfig = ProteusConfig.set_trytond(
            database_name=sDatabaseName,
            user=sAdminUser,
            database_type=sDatabaseType,
            password=sAdminPassword,
            language='en_US',
            config_file=sTrytonConfigFile)
    else:
        context.oProteusConfig = ProteusConfig.set_trytond(
            database_name=sDatabaseName,
            user=sAdminUser,
            # database_type=sDatabaseType,
            password=sAdminPassword,
            language='en_US',
            config_file=sTrytonConfigFile)

    # one of ['pdb', 'pydbgr']
    sTracer = oEnvironmentCfg.get('scenari', 'tracer')
    if sTracer:
        try:
            import pydbgr
            lTracers = ['pdb', 'pydbgr']
        except:
            lTracers = ['pdb']

        assert sTracer in lTracers, "Unsupported tracer: %s" % (sTracer,)
    # use this dictionary as a last resort to pass data around
    # we could put it in contex.userdata but for now we'll keep it separate
    if not hasattr(context, 'dData'):
        context.dData = dict()

def after_all(context):
    """These run after the whole shooting match.
    """
    tenv.after_all(context)
    # This is REQUIRED if we dont want to leave a hanging
    # database connexion to postgres. It will show up
    # with netstat even after the behave process is done.
    if context.oProteusConfig:
        if hasattr(context.oProteusConfig, 'database_connexion'):
            # a patch of ours to proteus 2.8 config.py to support this
            context.oProteusConfig.database_connexion.close()
        else:
            try:
                # works for Tryton 3.x
                from trytond import backend
                _connpool = backend.get('Database')._connpool
                if _connpool: 
                    _connpool.closeall()
                    _connpool = None
            except:
                # This is not fatal
                pass
        context.oProteusConfig = None

    # we still end up with a lingering closewait of the
    # socket in the trytond server, but that, I think, is OK.
    # tcp        1      0 127.0.0.1:37369         127.0.0.1:4070          CLOSE_WAIT  22425/python
    # # ps ax | grep 22425
    # 22425 pts/0    Sl     4:03 python /n/lib/python2.7/site-packages/tryton-2.8.2-py2.7.egg/EGG-INFO/scripts/tryton


def before_step(context, step):
    """These run before every step.
    """
    
    ctx = context # From OpenERPScenario
    ctx._messages = []
    # Extra cleanup (should be fixed upstream?)
    ctx.table = None
    ctx.text = None
    if not 'scenario' in context.dData or context.dData['scenario'] is None:
        before_scenario(context, None)
    if not 'feature'  in context.dData or context.dData['feature'] is None:
        before_feature(context, None)

def after_step(context, laststep):
    """These run after every step.
    N.B.: only called after a failed step if behave --stop
    """
    sTracer = context.oEnvironmentCfg.get('scenari', 'tracer')
    ctx = context # From OpenERPScenario
    if len(ctx.config.outputs):
        # FixMe: figure these out and formatters
        # Its of len(1) and class StreamOpener with attribute getvalue()
        output = ctx.config.outputs[0]
    # Sleazy - but works for me
    output = sys.__stdout__
    if ctx._messages:
        # Flush the messages collected with puts(...)
        for item in ctx._messages:
            for line in str(item).splitlines():
                output.write(u'      %s\n' % (line,))
        output.flush()

    if laststep.status == 'failed' and sTracer and ctx.config.stop:
        if sTracer == 'pdb':
            tools.set_trace_with_pdb()
        elif sTracer == 'pydbgr':
            tools.set_trace_with_pdb()

def before_scenario(context, scenario):
    """These run before each scenario is run.
    """
    tenv.before_scenario(context, scenario)
    # use this dictionary as a last resort to pass data around
    if not 'scenario' in context.dData or context.dData['scenario'] is None:
        context.dData['scenario'] = dict()

def after_scenario(context, scenario):
    """These run after each scenario is run.
    """
    tenv.after_scenario(context, scenario)
    context.dData['scenario'] = None

def before_feature(context, feature):
    """These run before each feature file is exercised.
    """
    tenv.before_feature(context, feature)
    if not 'feature' in context.dData or context.dData['feature'] is None:
        context.dData['feature'] = dict()

def after_feature(context, feature):
    """These run after each feature file is exercised.
    """
    tenv.after_feature(context, feature)
    context.dData['feature'] = None

def before_tag(context, tag):
    """These run before a section tagged with the given name. They are
    invoked for each tag encountered in the order they're found in the
    feature file.
    """
    pass

def after_tag(context, tag):
    """These run after a section tagged with the given name. They are
    invoked for each tag encountered in the order they're found in the
    feature file.
    """
    pass

