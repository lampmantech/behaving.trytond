# -*- encoding: utf-8 -*-

import sys, os
import ConfigParser

from datetime import datetime
from optparse import OptionParser

import proteus
from proteus import Model, Wizard

from .steps.support import tools

ETC_TRYTOND_CONF='/n/data/TrytonOpenERP/etc/trytond-3.2.conf'

def vCreateConfigFile(oEnvironmentCfg, sFile):

    oEnvironmentCfg.add_section('trytond')
    oEnvironmentCfg.set('trytond', 'password', 'foobar')
    oEnvironmentCfg.set('trytond', 'user', 'admin')
    oEnvironmentCfg.set('trytond', 'database_name', 'test32')
    oEnvironmentCfg.set('trytond', 'database_type', 'postgresql')
    oEnvironmentCfg.set('trytond', 'config_file', ETC_TRYTOND_CONF)

    oEnvironmentCfg.add_section('scenari')
    oEnvironmentCfg.set('scenari', 'verbosity', '0')
    oEnvironmentCfg.set('scenari', 'tracer', '')

    # Writing our configuration file to 'example.cfg'
    with open(sFile, 'wb') as oFd:
        oEnvironmentCfg.write(oFd)

def oReadConfigFile():
    oEnvironmentCfg = ConfigParser.RawConfigParser()

    sFile = os.path.splitext(__file__)[0]+'.cfg'
    if os.path.exists(sFile):
        oEnvironmentCfg.read(sFile)
    else:
        vCreateConfigFile(oEnvironmentCfg, sFile)
    return oEnvironmentCfg


def before_all(context):
    """These run before and after the whole shooting match.
    """
    oEnvironmentCfg = oReadConfigFile()

    sUser=oEnvironmentCfg.get('trytond', 'user')
    assert sUser
    sDatabaseName=oEnvironmentCfg.get('trytond', 'database_name')
    assert sDatabaseName
    sPassword = oEnvironmentCfg.get('trytond', 'password')
    assert sPassword
    sDatabaseType=oEnvironmentCfg.get('trytond', 'database_type')
#?    assert sDatabaseType in ['postgresql'], "Unsupported database type: " + sDatabaseType
    sTrytonConfigFile=oEnvironmentCfg.get('trytond', 'config_file')
    assert os.path.exists(sTrytonConfigFile), \
        "Required file not found: " + sTrytonConfigFile

    context.oEnvironmentCfg = oEnvironmentCfg
    context.oProteusConfig = proteus.config.set_trytond(
        database_name=sDatabaseName,
        user=context.oEnvironmentCfg.get('trytond', 'user'),
        database_type=sDatabaseType,
        password=context.oEnvironmentCfg.get('trytond', 'password'),
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
    if not hasattr(context, 'dData'):
        context.dData = dict()

def after_all(context):
    """These run after the whole shooting match.
    """
    # This is REQUIRED if we dont want to leave a hanging
    # database connexion to postgres. It will show up
    # with netstat evan after the behave process is done.
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
    # use this dictionary as a last resort to pass data around
    if not 'scenario' in context.dData or context.dData['scenario'] is None:
        context.dData['scenario'] = dict()

def after_scenario(context, scenario):
    """These run after each scenario is run.
    """
    context.dData['scenario'] = None

def before_feature(context, feature):
    """These run before each feature file is exercised.
    """
    if not 'feature' in context.dData or context.dData['feature'] is None:
        context.dData['feature'] = dict()

def after_feature(context, feature):
    """These run after each feature file is exercised.
    """
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

