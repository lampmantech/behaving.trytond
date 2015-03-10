# -*- mode: python; py-indent-offset: 4; coding: utf-8-unix; encoding: utf-8 -*-
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
from .support.stepfuns import vAssertContentTable

@step('Create a bank associated to a party "{uParty}" with optional |bic| field')
def step_impl(context, uParty):
    r"""
    Given \
    Create a named bank associated to a party, with optional BIC
     | bic    |
     | THEBIC |
    Create the party first, with things like addresses, and
    then use this to create the bank.
    The uBic field can be missing; if not it has 11 characters.
    """
    Party = proteus.Model.get('party.party')
    oParty, = Party.find([('name', '=', uParty)])

    Bank = proteus.Model.get('bank')
    if not Bank.find([('party.id', '=', oParty.id)]):
        oBank = Bank(party=oParty)
        if hasattr(context, 'table') and context.table:
            for row in context.table:
                if row['bic']:
                    uBic = row['bic']
                    assert len(uBic) <= 11
                    oBank.bic=uBic
                    break
        oBank.save()

    assert Bank.find([('party.id', '=', oParty.id)])

@step('Create a bank account with IBAN "{uIban}" at a bank associated to a party "{uParty}", with following optional number, owner or currency')
def step_impl(context, uIban, uParty):
    r"""
    Given \
    Create a bank account with IBAN "{uBank}" associated with a party "{uParty}
    with a following table of | name | value |.
    Each name is one of: iban number owner or currency.
    Owner is a party name, and currency is a currency code.
    """
    config = context.oProteusConfig

    BankAccountNumber = proteus.Model.get('bank.account.number')
    BankAccount = proteus.Model.get('bank.account')
    Bank = proteus.Model.get('bank')
    Currency = proteus.Model.get('currency.currency')

    Party = proteus.Model.get('party.party')
    oParty, = Party.find([('name', '=', uParty)])
    oBank, = Bank.find([('party.id', '=', oParty.id)])
    lAccs = BankAccount.find([('bank.party.id', '=', oBank.id)])
    if not lAccs:
        # FixMe: cant search BankAccount Numbers 'numbers'
        uIban = uIban.replace(' ','')
        dBankAccount = {
            'bank': oBank.id,
            }
        # FixMe: the order of the numbers determines the record name
        # return self.numbers[0].number
        lNumbers  = [{
            'type': 'iban',
            'number': uIban,
        }]
        lOwners  = []
        for row in context.table:
            if row['name'] == u'currency':
                currency, = Currency.find([('code', '=', row['value'])])
                dBankAccount['currency'] = currency.id
            elif row['name'] == u'iban':
                # already in
                pass
            elif row['name'] == u'owner':
                #  FixMe: Party or Bank Party?
                oOwner, = Party.find([('name', '=', row['value'])])
                # lOwners.append({'code': oOwner.code})
                lOwners.append({'name': oOwner.name})
            elif row['name'] == u'number':
                lNumbers.append({
                    'type': 'other',
                    'number': row['value'],
                })

        dBankAccount['numbers'] = [('create', lNumbers)]
        iBankAccount, = BankAccount.create([dBankAccount], config.context)
        oBankAccount = BankAccount(iBankAccount)
        if lOwners:
            oBankAccount.owners.append(oOwner)
        oBankAccount.save()
        
# IBAN is NOT international: Canada and the US dont use them
@step('Create a bank account with number "{uNum}" at a bank associated to a party "{uParty}" with optional owner or currency following |name|value|')
def step_impl(context, uNum, uParty):
    r"""
    Create a bank account with number "{uNum}" \
    at a bank associated to a party "{uParty}" \
    with optional owner or currency following |name|value|
    Each name is one of: owner or currency.
    Owner is a party name, and currency is a currency code.
    """
    config = context.oProteusConfig

    BankAccountNumber = proteus.Model.get('bank.account.number')
    BankAccount = proteus.Model.get('bank.account')
    Bank = proteus.Model.get('bank')
    Currency = proteus.Model.get('currency.currency')

    Party = proteus.Model.get('party.party')
    oParty, = Party.find([('name', '=', uParty)])
    oBank, = Bank.find([('party.id', '=', oParty.id)])
    # FixMe should be looking for the account with number? self.numbers[0].number
    lAccs = BankAccount.find([('bank.party.id', '=', oBank.id)])
    if True or not lAccs:
        # FixMe: cant search BankAccount Numbers 'numbers'
        uNum = uNum.replace(' ','')
        dBankAccount = {
            'bank': oBank.id,
            }
        # FixMe: the order of the numbers determines the record name
        # return self.numbers[0].number
        lNumbers  = [{
            'type': 'other',
            'number': uNum,
        }]

        lOwners  = []
        for row in context.table:
            if row['name'] == u'currency':
                currency, = Currency.find([('code', '=', row['value'])])
                dBankAccount['currency'] = currency.id
            elif row['name'] == u'iban':
                # unused
                pass
            elif row['name'] == u'owner':
                #  FixMe: Party or Bank Party?
                oOwner, = Party.find([('name', '=', row['value'])])
                # lOwners.append({'code': oOwner.code})
                lOwners.append({'name': oOwner.name})
            elif row['name'] == u'number':
                pass
            
        assert lNumbers
        dBankAccount['numbers'] = [('create', lNumbers)]
        iBankAccount, = BankAccount.create([dBankAccount], config.context)
        oBankAccount = BankAccount(iBankAccount)
        if lOwners:
            oBankAccount.owners.append(oOwner)
        oBankAccount.save()

# Bank
@step('Create a sequence on account.journal named "{uBankSequenceName}"')
def step_impl(context, uBankSequenceName):
    r"""
    Given \
    Create a non-strict sequence on account.journal named "{uBankSequenceName}"
    Idempotent.
    """
    current_config = context.oProteusConfig

    sCompanyName = sGetFeatureData(context, 'party,company_name')
    Party = proteus.Model.get('party.party')
    party, = Party.find([('name', '=', sCompanyName)])
    Company = proteus.Model.get('company.company')
    company, = Company.find([('party.id', '=', party.id)])

    Sequence = proteus.Model.get('ir.sequence')
    if not Sequence.find([('name', '=', uBankSequenceName,)]):
        oSequence = Sequence(name=uBankSequenceName,
                            code='account.journal',
                            company=company)
        oSequence.save()

    assert Sequence.find([('name', '=', uBankSequenceName,)])

    # is this needed?
    Account = proteus.Model.get('account.account')
    cash, = Account.find([
                ('kind', '=', 'other'),
                ('company', '=', company.id),
                ('name', '=', sGetFeatureData(context, 'account.template,main_cash')),
                ])
    cash.bank_reconcile = True
    cash.save()

# DifferentCurrencySJ, StatementAJ, USD
@step('Create a Bank Statement Journal named "{uName}" from the account.journal named "{uStatementAJName}" with currency "{uCur}"')
def step_impl(context, uName, uStatementAJName, uCur):
    r"""
    Given \
    Create an account.bank.statement.journal named "{uName}"
    from the account.journal named "{uStatementAJName}"
    with currency "{uCur}"
    Idempotent.
    """
    Currency = proteus.Model.get('currency.currency')
    oCur, = Currency.find([('code', '=', uCur)])

    AccountJournal = proteus.Model.get('account.journal')
    oAccountJournal, =  AccountJournal.find([('name', '=', uStatementAJName),
                                             ('type', '=', 'cash')])

    StatementJournal = proteus.Model.get('account.bank.statement.journal')
    uStatementJournalName=uName
    if not StatementJournal.find([('name', '=', uStatementJournalName)]):
        oStatementJournalDollar = StatementJournal(name=uStatementJournalName,
                                                journal=oAccountJournal,
                                                currency=oCur)
        oStatementJournalDollar.save()

    assert StatementJournal.find([('name', '=', uStatementJournalName)])

#     StatementAJ, : Main Cash Main Cash
@step('Create a cash account.journal named "{uName}" from the sequence named "{uBankSequenceName}" with following |name|value| credit_account, debit_account fields')
def step_impl(context, uName, uBankSequenceName):
    r"""
    Given \
    Create a cash account.journal named "{uName}"
    with the sequence named "{uBankSequenceName}"
    with a following |name|value| table
    with credit_account, debit_account fields, e.g.
	| name 	     	  | value	  |
	| credit_account  | Main Cash	  |
	| debit_account   | Main Cash	  |
    The accounts must be of domain: ('kind', '=', 'other')
    Idempotent.
    """
    Account = proteus.Model.get('account.account')
    AccountJournal = proteus.Model.get('account.journal')

    sCompanyName = sGetFeatureData(context, 'party,company_name')
    Party = proteus.Model.get('party.party')
    party, = Party.find([('name', '=', sCompanyName)])
    Company = proteus.Model.get('company.company')
    company, = Company.find([('party.id', '=', party.id)])

    Sequence = proteus.Model.get('ir.sequence')
    oSequence, = Sequence.find([('name', '=', uBankSequenceName,)])

    if not AccountJournal.find([('name', '=', uName),
                                ('type', '=', 'cash')]):
            oDefaultCash, = Account.find([
                ('kind', '=', 'other'),
                ('company', '=', company.id),
                ('name', '=', sGetFeatureData(context, 'account.template,main_cash')),
            ])
            credit_account = debit_account = oDefaultCash

            for row in context.table:
                if row['name'] == 'credit_account':
                    credit_account, = Account.find([
                        ('kind', '=', 'other'),
                        ('company', '=', company.id),
                        ('name', '=', row['value'])])
                elif row['name'] == 'debit_account':
                    debit_account, = Account.find([
                        ('kind', '=', 'other'),
                        ('company', '=', company.id),
                        ('name', '=', row['value'])])

            oAccountJournal = AccountJournal(name=uName,
                                             type='cash',
                                             credit_account=credit_account,
                                             debit_account=credit_account,
                                             sequence=oSequence)
            oAccountJournal.save()

    oAccountJournal, = AccountJournal.find([('name', '=', uName),
                                            ('type', '=', 'cash')])

@step('Create a financial account under "{uTemplate}" for the bank account with IBAN "{uIban}"')
@step('Create a financial account under "{uTemplate}" for the bank account with number "{uIban}"')
def step_impl(context, uTemplate, uIban):
    r"""
    Given \
    Create a new account into the chart of accounts for a bank account.
    It takes "{uTemplate}" as an argument which is the name an existing account
    in the chart where the new account will be created: if uTemplate is of
    kind view, the new chart will have it as its parent; if not,
    the new chart will be the next available sibling, with code += 1.
    The step assumes that the sTemplate account has an integer code, <= 9999;
    it just adds 1 until it finds the next available account, so you can
    have many calls to this step with different IBANS.
    The name of the new account is the IBAN.

    The account_bank_statement module has to be loaded
    before ANY accounts are created or this will error.
    """
    # sFormat = sGetFeatureData('account.template', 'bank_account_format')
    o = oCreateNewChartAccountforBank(context, uIban, uTemplate)

def oCreateNewChartAccountforBank(context, sNumber, sTemplate, sFormat=""):
    r"""
    Given \
    Create a new account into the chart of accounts for a bank account.
    The account_bank_statement module has to be loaded
    before ANY accounts are created or this will error.

    """
    config = context.oProteusConfig
    # FixMe: do accounts have currency?
    Account = proteus.Model.get('account.account')

    sCompanyName = sGetFeatureData(context, 'party,company_name')
    Party = proteus.Model.get('party.party')
    party, = Party.find([('name', '=', sCompanyName)])
    Company = proteus.Model.get('company.company')
    company, = Company.find([('party.id', '=', party.id)])

    sNumber = sNumber.replace(' ','')
    if sFormat:
        sNewName = sFormat % (sNumber,)
    else:
        sNewName = sNumber
    # sTemplate = sGetFeatureData('account.template,bank_account_template')
    oTemplate, = Account.find([('name', '=', sTemplate),
                               ('company', '=', company.id),])
    if not Account.find([('name', '=', sNewName),
                         ('company', '=', company.id),]):
        iCode=int(oTemplate.code)
        while iCode < 9999 and Account.find([('code', '=', str(iCode)),
                                             ('company', '=', company.id),]):
            iCode += 1
        # bank_reconcile is added by trytond-account_bank_statement/account.py
        # account_bank_statement module has to be loaded
        # before accounts are created or this will error.
        iNewAccount, = Account.create([dict(name=sNewName,
                                            bank_reconcile=True,
                                            code=str(iCode))], config.context)
        oNewAccount= Account(iNewAccount)
        oParent = oTemplate.parent
        # FixMe: any others?
        for row in ['type', 'kind']:
            gValue = getattr(oTemplate, row)
            if not gValue: continue
            # gValue = string_to_python(row, value, Account)
            if row == 'kind' and gValue == 'view':
                # FixMe: is it kind other or kind cash?
                gValue = 'other'
                oParent = oTemplate
            setattr(oNewAccount, row, gValue)

        oNewAccount.parent = oParent
        #? is this right? are bank accounts always reconcile = True
        oNewAccount.reconcile = True
        oNewAccount.save()

    l = Account.find([('name', '=', sNewName),
                      ('company', '=', company.id),])
    assert l
    return l[0]


