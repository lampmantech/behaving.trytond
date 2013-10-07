# -*- encoding: utf-8 -*-

import os
import ConfigParser

from datetime import datetime
from optparse import OptionParser

import proteus
from proteus import Model, Wizard

ETC_TRYTOND_CONF='/etc/trytond.conf'

def vCreateConfigFile(oConfig, sFile):

    oConfig.add_section('trytond')
    oConfig.set('trytond', 'password', 'foobar')
    oConfig.set('trytond', 'user', 'admin')
    oConfig.set('trytond', 'database_name', 'test28')
    oConfig.set('trytond', 'database_type', 'postgres')
    oConfig.set('trytond', 'config_file', ETC_TRYTOND_CONF)

    oConfig.add_section('scenari')
    oConfig.set('scenari', 'verbosity', '0')

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
    assert sDatabaseType in ['postgres'], "Unsupported database type: " + sDatabaseType
    sTrytonConfigFile=oConfig.get('trytond', 'config_file')
    assert os.path.exists(sTrytonConfigFile), "Required file not found: " + sTrytonConfigFile

    context.oConfig = oConfig
    context.oProteusConfig = proteus.config.set_trytond(
        user=sUser,
        database_type=sDatabaseType,
        database_name=sDatabaseName,
        config_file=sTrytonConfigFile,
        password=sPassword)

def after_all(context):
    """These run before and after the whole shooting match.
    """
    pass


def before_step(context, step):
    """These run before and after every step.
    """
    pass

def after_step(context, step):
    """These run before and after every step.
    """
    pass

def before_scenario(context, scenario):
    """These run before and after each scenario is run.
    """
    pass

def after_scenario(context, scenario):
    """These run before and after each scenario is run.
    """
    pass

def before_feature(context, feature):
    """These run before and after each feature file is exercised.
    """
    pass

def after_feature(context, feature):
    """These run before and after each feature file is exercised.
    """
    pass

def before_tag(context, tag):
    """These run before and after a section tagged with the given name. They are
    invoked for each tag encountered in the order they're found in the
    feature file.
    """
    pass

def after_tag(context, tag):
    """These run before and after a section tagged with the given name. They are
    invoked for each tag encountered in the order they're found in the
    feature file.
    """
    pass

