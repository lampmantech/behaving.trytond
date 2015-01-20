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

@step('Create a bank associated to a party "{uParty}" with optional BIC "{uBic}"')
def step_impl(context, uParty, uBic):
    """
    Create a named bank associated to a party, with optional BIC.
    Create the party first, with things like addresses, and
    then use this to create the bank.
    The uBic field can be empty; if not it has 11 characters.
    """
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

# Bank
@step('Create a sequence on account.journal named "{uBankSequenceName}"')
def step_impl(context, uBankSequenceName):
    """
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
    """
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
    """
    Create a cash account.journal named "{uName}" 
    with the sequence named "{uBankSequenceName}" 
    with a following |name|value| table
    with credit_account, debit_account fields, e.g.
	| name 	     	  | value	  |
	| credit_account  | Main Cash	  |
	| debit_account   | Main Cash	  |
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
            
    assert AccountJournal.find([('name', '=', uName),
                                ('type', '=', 'cash')])
