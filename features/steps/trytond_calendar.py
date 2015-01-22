# -*- mode: python; py-indent-offset: 4; coding: utf-8-unix; encoding: utf-8 -*-
"""


"""
import sys, os
from behave import *
import proteus

import datetime
from decimal import Decimal

from .support.fields import string_to_python, sGetFeatureData, vSetFeatureData
from .support import modules
from .support.tools import *
from .support.stepfuns import oAttachLinkToResource
from .support.stepfuns import vAssertContentTable

today = datetime.date.today()


@step('Create a calendar named "{uCalName}" owned by the user "{uUserName}"')
def step_impl(context, uCalName, uUserName):
    """
    WIP.
    Idempotent.
    """
    oCurrentConfig = context.oProteusConfig

    Calendar = proteus.Model.get('calendar.calendar')

    User = proteus.Model.get('res.user')
    # FixMe: derive this
    uUserName=sGetFeatureData(context, 'user,'+uUserName+',name')
    uUserLogin=sGetFeatureData(context, 'user,'+uUserName+',login')
    uUserPassword=sGetFeatureData(context, 'user,'+uUserName+',password')
    oUser, = User.find([('name', '=', uUserName)])

    oAdminUser, = User.find([('name', '=', 'Administrator')])
    # calendar names must be unique
    if not Calendar.find([('name', '=', uCalName)]):
        try:
            dNewConfig=dict(user=uUserLogin,
                                   password=uUserPassword,
                                   config_file=oCurrentConfig.config_file,
                                   database_name=oCurrentConfig.database_name)
            oNewConfig = proteus.config.set_trytond(**dNewConfig)

            dElt = dict(name=uCalName,
                        write_users=[('add', [oAdminUser.id])],
                        read_users=[('add', [oAdminUser.id])],
                        owner=oUser.id)
            iCalendar, = Calendar.create([dElt], dNewConfig)
            oCalendar = Calendar(iCalendar)
            oCalendar._config = oNewConfig
            oCalendar.save()
        finally:
            proteus.config.set_trytond(user=context.oEnvironmentCfg.get('trytond', 'user'),
                                       password=context.oEnvironmentCfg.get('trytond', 'password'),
                                       config_file=oCurrentConfig.config_file,
                                       database_name=oCurrentConfig.database_name)

    assert Calendar.find([('name', '=', uCalName)])

@step('I need a set of "{uKind}" events in a calendar named "{uCalName}" owned by the user named "{uUserName}" with fields')
def step_impl(context, uKind, uCalName, uUserName):
    """WIP.
    Create "{uKind}" events in the calendar named "{uCalName}"
    owned by the user named "{uUserName}". {uKind} can be empty, but
    if not, it is the category.
    You must firstly create the user with the step 'Create a
    user named'... in order to fields in the FeatureData, or use 'Set
    the feature data with values' ...
    It expects a |date|name|location|description| table.
    Idempotent.

    """
    oCurrentConfig = context.oProteusConfig

    Calendar = proteus.Model.get('calendar.calendar')
    Event = proteus.Model.get('calendar.event')
    Location = proteus.Model.get('calendar.location')
    Category = proteus.Model.get('calendar.category')

    # NewCalendar=proteus.Model.get('calendar.calendar', proteus.config.TrytondConfig('meec32', 'accountant', 'postgresql', config_file='/n/data/TrytonOpenERP/etc/trytond-3.2.conf'))

    if True:
        uUserLogin=sGetFeatureData(context, 'user,'+uUserName+',login')
        uUserPassword=sGetFeatureData(context, 'user,'+uUserName+',password')
        uUserEmail=sGetFeatureData(context, 'user,'+uUserName+',email')
    else:
        # FixMe: is the password derivable? I think its hashed
        User = proteus.Model.get('res.user')
        oUser, = User.find([('name', '=', uUserName)])
        uUserEmail = oUser.email

    # I think Calendar names are unique across all users
    oCalendar, = Calendar.find([('name', '=', uCalName)])

    try:
        dNewConfig=dict(user=uUserLogin,
                                   password=uUserPassword,
                                   config_file=oCurrentConfig.config_file,
                                   database_name=oCurrentConfig.database_name)
        oNewConfig = proteus.config.set_trytond(**dNewConfig)
        # name date
        for row in context.table:
            uName = row['name']
            uDate = row['date']
            uSummary = uName
            uDescription = row['description']
            #! ('UserError', ('The name of calendar location must be unique.', ''))
            iLocation = 0
            if row['location']:
                l = Location.find([('name', '=', row['location'],)])
                if len(l):
                    iLocation = l[0].id
                else:
                    oLocation = Location(name=row['location'])
                    oLocation._config = oNewConfig
                    oLocation.save()
                    iLocation = oLocation.id

            iCategory = 0
            if uKind:
                l = Category.find([('name', '=', uKind,)])
                if len(l):
                    iCategory = l[0].id
                else:
                    oCategory = Category(name=uKind)
                    oCategory._config = oNewConfig
                    oCategory.save()
                    iCategory = oCategory.id

            if not Event.find([
                    ('calendar.owner.email', '=', uUserEmail),
                    ('classification', '=', 'public'),
                    ('status', '=', 'confirmed'),
                    ('summary', '=', uSummary),
                    ('description', '=', uDescription),
#?                    ('location', '!=', None),
            ]):
                oDate = datetime.datetime(*map(int,uDate.split('-')))
                dElt = dict(calendar=oCalendar.id,
                            summary=uSummary,
                            description=uDescription,
                            all_day=True,
                            classification='public',
                            transp='transparent',
                            status='confirmed',
                            dtstart=oDate)
                if iLocation:
                    dElt['location'] = iLocation
                if iCategory:
                    dElt['categories']=[('add', [iCategory])]
                iEvent, = Event.create([dElt], dNewConfig)
                oEvent = Event(iEvent)
                oEvent._config = oNewConfig
                oEvent.save()
                if uDescription:
                    uDescription = uDescription.strip().replace('file://', '')
                    if uDescription[0] == '/':
                        if os.path.exists(uDescription):
                            sLink = 'file://' + uDescription
                            sName = uDescription
                            # I think this has to be unique on the resource
                            sName = "%s %d" % (uSummary, id(oEvent))
                            oAttachment = oAttachLinkToResource(sName,
                                                                uDescription,
                                                                sLink,
                                                                oEvent)
                            assert oAttachment.type == 'link'
                        else:
                            puts('>>> WARN: Not found '+uDescription+'\n')
            assert Event.find([
                    ('calendar.owner.email', '=', uUserEmail),
                    ('classification', '=', 'public'),
                    ('status', '=', 'confirmed'),
                    ('description', '=', uDescription),
#                    ('location', '!=', None),
                ])

    # accountant_calendar = proteus.Model.get('calendar.calendar', proteus.config.TrytondConfig('test30', 'accountant', 'postgresql', config_file='/etc/trytond.conf'))(2)

    finally:
        proteus.config.set_trytond(user=context.oEnvironmentCfg.get('trytond', 'user'),
                                   password=context.oEnvironmentCfg.get('trytond', 'password'),
                                   config_file=oCurrentConfig.config_file,
                                   database_name=oCurrentConfig.database_name)

iTHIS_YEAR = datetime.date.today().year
# unfinished
@step('I need a set of "{uKind}" annual events in the calendar named "{uCalName}" owned by the user named "{uUserName}" with fields')
def step_impl(context, uKind, uCalName, uUserName):
    """WIP.   Needs recurrence rule.
    Create "{uKind}" annual events in the calendar named "{uCalName}"
    owned by the user named "{uUserName}". {uKind} can be empty, but
    if not, it is the category; things like Holiday or Birthday are
    common.  Use 0000 as the year of any dates you want to recur.
    You must firstly create the user with the step 'Create a
    user named'... in order to fields in the FeatureData, or use 'Set
    the feature data with values' ...
    It expects a |name|date| table.
    Idempotent.
    """
    oCurrentConfig = context.oProteusConfig

    Calendar = proteus.Model.get('calendar.calendar')
    Event = proteus.Model.get('calendar.event')
    Category = proteus.Model.get('calendar.category')
    RRule = proteus.Model.get('calendar.event.rrule') # create write
#?    oAnnualRule = RRule.create([{'freq': 'yearly'}], {})

    if True:
        uUserLogin=sGetFeatureData(context, 'user,'+uUserName+',login')
        uUserPassword=sGetFeatureData(context, 'user,'+uUserName+',password')
        uUserEmail=sGetFeatureData(context, 'user,'+uUserName+',email')
    else:
        # FixMe: is the password derivable? I think its hashed
        User = proteus.Model.get('res.user')
        oUser, = User.find([('name', '=', uUserName)])
        uUserEmail = oUser.email
    try:
        dNewConfig=dict(user=uUserLogin,
                                   password=uUserPassword,
                                   config_file=oCurrentConfig.config_file,
                                   database_name=oCurrentConfig.database_name)
        oNewConfig = proteus.config.set_trytond(**dNewConfig)

        # name date
        for row in context.table:
            uName = row['name']
            uDate = row['date']
            if uKind:
                uSummary = u"%s %s" % (uName, uKind)
            else:
                uSummary = uKind
            iCategory = 0
            if uKind:
                l = Category.find([('name', '=', uKind,)])
                if len(l):
                    iCategory = l[0].id
                else:
                    oCategory = Category(name=uKind)
                    oCategory._config = oNewConfig
                    oCategory.save()
                    iCategory = oCategory.id
            if not Event.find([
                    ('calendar.owner.email', '=', uUserEmail),
                    ('classification', '=', 'public'),
                    ('status', '=', 'confirmed'),
                    ('summary', '=', uSummary),
            ]):
                lDate = map(int,uDate.split('-'))
                if not lDate[0]:
                    lDate[0] = iTHIS_YEAR
                oDate = datetime.datetime(*lDate)
                # I think Calendar names are unique across all users
                oCalendar, = Calendar.find([('name', '=', uCalName)])
                dElt = dict(calendar=oCalendar.id,
                            summary=uSummary,
                            all_day=True,
                            classification='public',
                            transp='transparent',
                            status='confirmed',
                            dtstart=oDate)
                if iCategory:
                    dElt['categories']=[('add', [iCategory])]
                iEvent = Event.create([dElt], dNewConfig)
                oEvent = Event(iEvent)
                # oEvent._config = oNewConfig
                oEvent.save()

            assert Event.find([
                ('calendar.owner.email', '=', uUserEmail),
                ('summary', '=', uSummary),
                ])

    # accountant_calendar = proteus.Model.get('calendar.calendar', proteus.config.TrytondConfig('test30', 'accountant', 'postgresql', config_file='/etc/trytond.conf'))(2)

    finally:
        proteus.config.set_trytond(user=context.oEnvironmentCfg.get('trytond', 'user'),
                                   password=context.oEnvironmentCfg.get('trytond', 'password'),
                                   config_file=oCurrentConfig.config_file,
                                   database_name=oCurrentConfig.database_name)

