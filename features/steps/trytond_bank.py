# -*- encoding: utf-8 -*-
"""
WIP - unfinished

This would be a straight cut-and-paste from
trytond_bank-3.2.0/tests/
but trytond_bank doesn't have any meaningful tests.

trytond_bank also doesn't have any documentation, meaningful or not.
Which makes it pretty hard to figure out, especially as its classes
have self-referential fields. Grr.
"""

from behave import *
import proteus

from .support.fields import string_to_python, sGetFeatureData, vSetFeatureData

dBankCache={}
def oGetCached(uLocation, sType):
    """
    Cache the creation of instances for commonly occcuring things
    like location.
    """
    global dBankCache
    
    Location = proteus.Model.get('bank.'+sType)
    
    uKey= sType+','+uLocation
    if uKey not in dBankCache:
        iLocation, = Location.create([{'name': uLocation}], {})
        dBankCache[uKey] = Location(iLocation)
    return dBankCache[uKey]


@step('Create a bank associated to a party "{uParty}" with optional BIC "{uBic}"')
def step_impl(context, uParty, uBic):
    """
    Create a named bank associated to a party, with optional BIC.
    Create the party first, with things like addresses, and
    then use this to create the bank.
    The uBic field can be empty; if not it has 11 characters.
    """
    global dBankCache
    Party = proteus.Model.get('party.party')
    oParty, = Party.find([('name', '=', uParty)])
    
    Bank = proteus.Model.get('bank')
    if not Bank.find([('party.id', '=', oParty.id)]):
        oBank = Bank(party=oParty)
        if uBic:
            assert len(uBic) <= 11
            oBank.bic=uBic
        oBank.save()

    assert Bank.find([('party.id', '=', oParty.id)])

@step('Create a bank account with IBAN "{uIban}" at a bank associated to a party "{uParty}", with following optional number, owner or currency')
def step_impl(context, uIban, uParty):
    """
    Create a bank account at a bank "{uBank}" with optional currency "{uCur},
    with a following table of | name | value |.
    Each name is one of number or owner.
    At least one number is required; if you want to add more,
    just run this scenario again with the new number.
    """
    BankAccountNumber = proteus.Model.get('bank.account.number')
    BankAccount = proteus.Model.get('bank.account')
    Bank = proteus.Model.get('bank')
    Currency = proteus.Model.get('currency.currency')
    sType = 'iban'

    Party = proteus.Model.get('party.party')
    oParty, = Party.find([('name', '=', uParty)])
    oBank, = Bank.find([('party.id', '=', oParty.id)])
    return
    if True:
        # FixMe: cant search BankAccount or BankAccountNumber
        # and BankAccountNumber refers to BankAccount
        oBankAccount = BankAccount()
        oBankAccountNumber = BankAccountNumber(account=oBankAccount,
                                               type='iban',
                                               number=uIban)
        oBankAccount.numbers.append(oBankAccountNumber)
        for row in context.table:
            if row['name'] == u'currency':
                currency, = Currency.find([('code', '=', row['value'])])
                oBankAccount.currency = currency
        oBankAccount.save()
    
