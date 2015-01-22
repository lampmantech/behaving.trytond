# -*- encoding: utf-8 -*-

@orks32
Feature: Run the Trytond scenario_account_stock_anglo_saxon doctests
    adapted from scenario_account_stock_anglo_saxon_with_drop_shipment.rst
    in trytond_account_stock_anglo_saxon-3.2.1/tests/
    UNFINISHED.
    
    Scenario: Setup the tests of the module named "account_stock_anglo_saxon"

      Given Create database with pool.test set to True
       Then Account Stock Anglo-Saxon with Drop Shipment Scenario
