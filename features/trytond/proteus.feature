# -*- encoding: utf-8 -*-


Feature: Loading Tryton modules via behave

   Scenario: load some basic modules
      Given we have proteus installed
       when Ensure that the "account" module is loaded
       then the "account" module is in the list of loaded modules

