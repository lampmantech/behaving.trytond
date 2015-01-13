# -*- encoding: utf-8 -*-

import sys, os
import ConfigParser

from datetime import datetime
from optparse import OptionParser

import proteus
from proteus import Model, Wizard

from .steps.support import tools

ETC_TRYTOND_CONF='/n/data/TrytonOpenERP/etc/trytond-3.2.conf'

def vCreateConfigFile(oConfig, sFile):

    oConfig.add_section('trytond')
    oConfig.set('trytond', 'password', 'foobar')
    oConfig.set('trytond', 'user', 'admin')
    oConfig.set('trytond', 'database_name', 'test28')
    oConfig.set('trytond', 'database_type', 'postgresql')
    oConfig.set('trytond', 'config_file', ETC_TRYTOND_CONF)

    oConfig.add_section('scenari')
    oConfig.set('scenari', 'verbosity', '0')
    oConfig.set('scenari', 'tracer', '')

    # Writing our configuration file to 'example.cfg'
    with open(sFile, 'wb') as oFd:
        oConfig.write(oFd)

def oReadConfigFile():
    oConfig = ConfigParser.RawConfigParser()

    sFile = os.path.splitext(__file__)[0]+'.cfg'
    if os.path.exists(sFile):
        oConfig.read(sFile)
    else:
        vCreateConfigFile(oConfig, sFile)
    return oConfig


def before_all(context):
    """These run before and after the whole shooting match.
    """
    oConfig = oReadConfigFile()

    sUser=oConfig.get('trytond', 'user')
    assert sUser
    sDatabaseName=oConfig.get('trytond', 'database_name')
    assert sDatabaseName
    sPassword = oConfig.get('trytond', 'password')
    assert sPassword
    sDatabaseType=oConfig.get('trytond', 'database_type')
#?    assert sDatabaseType in ['postgresql'], "Unsupported database type: " + sDatabaseType
    sTrytonConfigFile=oConfig.get('trytond', 'config_file')
    assert os.path.exists(sTrytonConfigFile), \
        "Required file not found: " + sTrytonConfigFile

    context.oConfig = oConfig
    context.oProteusConfig = proteus.config.set_trytond(
        database_name=sDatabaseName,
        user=sUser,
        database_type=sDatabaseType,
        password=sPassword,
        language='en_US',
        config_file=sTrytonConfigFile)

    # one of ['pdb', 'pydbgr']
    sTracer = oConfig.get('scenari', 'tracer')
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
    context.dData['trytond,user'] = sUser
    context.dData['trytond,password'] = sPassword
    context.dData['trytond,database_name'] = sDatabaseName
    context.dData['trytond,database_type'] = sDatabaseType
    context.dData['trytond,config_file'] = sTrytonConfigFile

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
    sTracer = context.oConfig.get('scenari', 'tracer')
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

