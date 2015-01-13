# -*- encoding: utf-8 -*-
"""


"""
from behave import *
import proteus

import datetime
from decimal import Decimal

from .support.fields import string_to_python, sGetFeatureData, vSetFeatureData
from .support import modules
from .support.tools import *

dCalendarCache={}
def oGetCached(uLocation, sType):
    global dCalendarCache
    
    Location = proteus.Model.get('calendar.'+sType)
    
    uKey= sType+','+uLocation
    if uKey not in dCalendarCache:
        iLocation, = Location.create([{'name': uLocation}], {})
        dCalendarCache[uKey] = Location(iLocation)
    return dCalendarCache[uKey]

@step('Create a calendar named "{uCalName}" owned by the user "{uUserName}"')
def step_impl(context, uCalName, uUserName):
    """
    WIP.
    Idempotent.
    """
    oCurrentConfig = context.oProteusConfig

    Calendar = proteus.Model.get('calendar.calendar')

    # FixMe: derive this
    uUserName=sGetFeatureData(context, 'user,'+uUserName+',name')
    uUserLogin=sGetFeatureData(context, 'user,'+uUserName+',login')
    uUserPassword=sGetFeatureData(context, 'user,'+uUserName+',password')
    
    User = proteus.Model.get('res.user')
    oUser, = User.find([('name', '=', uUserName)])
    oAdminUser, = User.find([('name', '=', 'Administrator')])
    # calendar names must be unique
    if not Calendar.find([('name', '=', uCalName)]):
        try:
            oNewConfig = proteus.config.set_trytond(user=uUserLogin,
                                                password=uUserPassword,
                                                config_file=oCurrentConfig.config_file,
                                                database_name=oCurrentConfig.database_name)
            calendar = Calendar(name=uCalName, owner=oUser)
            calendar.write_users.append(oAdminUser)
#!?            calendar.read_users.append(oAdminUser)
            calendar.save()
        finally:
            # FixMe: is password in oCurrentConfig? user=oCurrentConfig._user
            proteus.config.set_trytond(user=context.dData['trytond,user'],
                                       password=context.dData['trytond,password'],
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
    Category = proteus.Model.get('calendar.category')
    
    # I think Calendar names are unique across all users
    oCalendar, = Calendar.find([('name', '=', uCalName)])
    
    uUserName=sGetFeatureData(context, 'user,'+uUserName+',name')
    uUserLogin=sGetFeatureData(context, 'user,'+uUserName+',login')
    uUserPassword=sGetFeatureData(context, 'user,'+uUserName+',password')
    
    User = proteus.Model.get('res.user')
    oUser, = User.find([('name', '=', uUserName)])
    # FixMe: is the password derivable?
    owner_email = oUser.email
    try:
        oNewConfig = proteus.config.set_trytond(user=uUserLogin,
                                            password=uUserPassword,
                                            config_file=oCurrentConfig.config_file,
                                            database_name=oCurrentConfig.database_name)


        # name date
        for row in context.table:
            uName = row['name']
            uDate = row['date']
            sSummary = uName
            uDescription = row['description']
#! ('UserError', ('The name of calendar location must be unique.', ''))
            oLocation = oGetCached(row['location'], 'location')            
            if not Event.find([
                    ('calendar.owner.email', '=', owner_email),
                    ('classification', '=', 'public'),
                    ('status', '=', 'confirmed'),                    
                    ('summary', '=', sSummary),
                    ('description', '=', uDescription),
#?                    ('location', '!=', None),
            ]):
                oDate = datetime.datetime(*map(int,uDate.split('-')))
                event = Event(calendar=oCalendar,
                              summary=sSummary,
                              description=uDescription,
                              location=oLocation,
                              classification='public',
                              transp='transparent',
                              status='confirmed',
                              dtstart=oDate)
                if uKind:
                    pass
#?FixMe                    oCategory = oGetCached(uKind, 'category')
#?                    event.categories = [oCategory]
                event.save()
            assert Event.find([
                    ('calendar.owner.email', '=', owner_email),
                    ('classification', '=', 'public'),
                    ('status', '=', 'confirmed'),                    
                    ('summary', '=', sSummary),
                    ('description', '=', uDescription),
#                    ('location', '!=', None),
                ])

    # accountant_calendar = proteus.Model.get('calendar.calendar', proteus.config.TrytondConfig('test30', 'accountant', 'postgresql', config_file='/etc/trytond.conf'))(2)

    finally:
        proteus.config.set_trytond(user=context.dData['trytond,user'],
                                   password=context.dData['trytond,password'],
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
    common.  You must firstly create the user with the step 'Create a
    user named'... in order to fields in the FeatureData, or use 'Set
    the feature data with values' ...
    It expects a |name|date| table.  
    Idempotent.
    """
    oCurrentConfig = context.oProteusConfig

    Calendar = proteus.Model.get('calendar.calendar')
    Event = proteus.Model.get('calendar.event')
    RRule = proteus.Model.get('calendar.event.rrule') # create write
#?    oAnnualRule = RRule.create([{'freq': 'yearly'}], {})
    
    uUserName=sGetFeatureData(context, 'user,'+uUserName+',name')
    uUserLogin=sGetFeatureData(context, 'user,'+uUserName+',login')
    uUserPassword=sGetFeatureData(context, 'user,'+uUserName+',password')
    User = proteus.Model.get('res.user')
    oUser, = User.find([('name', '=', uUserName)])
    # FixMe: is the password derivable?
    owner_email = oUser.email
    try:
        oNewConfig = proteus.config.set_trytond(user=uUserLogin,
                                            password=uUserPassword,
                                            config_file=oCurrentConfig.config_file,
                                            database_name=oCurrentConfig.database_name)


        # name date
        for row in context.table:
            uName = row['name']
            uDate = row['date']
            if uKind:
                sSummary = "%s %s" % (uName, uKind)
            else:
                sSummary = uKind
            if not Event.find([
                    ('calendar.owner.email', '=', owner_email),
                    ('classification', '=', 'public'),
                    ('status', '=', 'confirmed'),                    
                    ('summary', '=', sSummary),
            ]):
                lDate = map(int,uDate.split('-'))
                lDate[0] = iTHIS_YEAR
                oDate = datetime.datetime(*lDate)
                # I think Calendar names are unique across all users
                oCalendar, = Calendar.find([('name', '=', uCalName)])
                event = Event(calendar=oCalendar,
                              summary=sSummary,
                              all_day=True,
                              classification='public',
                              transp='transparent',
                              status='confirmed',
                              dtstart=oDate)
                event.save()
            assert Event.find([
                ('calendar.owner.email', '=', owner_email),
                ('summary', '=', sSummary),
                ])

    # accountant_calendar = proteus.Model.get('calendar.calendar', proteus.config.TrytondConfig('test30', 'accountant', 'postgresql', config_file='/etc/trytond.conf'))(2)

    finally:
        proteus.config.set_trytond(user=context.dData['trytond,user'],
                                   password=context.dData['trytond,password'],
                                   config_file=oCurrentConfig.config_file,
                                   database_name=oCurrentConfig.database_name)
    
        
