# -*- mode: python; py-indent-offset: 4; coding: utf-8-unix; encoding: utf-8 -*-

import sys
import os
# We would have to do this if we used absolute imports, for some calling cases
if False and __name__ == '__main__' and not __package__:
    __package__ = 'behaving.trytond.steps'
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

# make it easy to do a 'from behaving.trytond.steps import *'

from behaving.trytond.steps.ProteusConfig import *
from behaving.trytond.steps.basic_modules import *
from behaving.trytond.steps.behave_test import *
from behaving.trytond.steps.dsl import *
from behaving.trytond.steps.ir import *
from behaving.trytond.steps.oerpscenario import *
from behaving.trytond.steps.proteus_doctests import *
from behaving.trytond.steps.scenario_account_asset import *
from behaving.trytond.steps.scenario_account_payment import *
from behaving.trytond.steps.scenario_account_reconciliation import *
from behaving.trytond.steps.scenario_account_statement import *
from behaving.trytond.steps.scenario_account_stock_anglo_saxon import *
from behaving.trytond.steps.scenario_account_stock_anglo_saxon_with_drop_shipment import *
from behaving.trytond.steps.scenario_doctests import *
from behaving.trytond.steps.scenario_invoice_supplier import *
from behaving.trytond.steps.scenario_move_template import *
from behaving.trytond.steps.scenario_purchase import *
from behaving.trytond.steps.scenario_stock_average_cost_price import *
from behaving.trytond.steps.scenario_stock_internal_supply import *
from behaving.trytond.steps.trytond_account import *
from behaving.trytond.steps.trytond_account_invoice import *
from behaving.trytond.steps.trytond_account_payment_clearing import *
from behaving.trytond.steps.trytond_bank import *
from behaving.trytond.steps.trytond_calendar import *
from behaving.trytond.steps.trytond_constants import *
from behaving.trytond.steps.trytond_move_template import *
from behaving.trytond.steps.trytond_product import *
from behaving.trytond.steps.trytond_purchase import *
from behaving.trytond.steps.trytond_sale import *
from behaving.trytond.steps.trytond_stock import *
