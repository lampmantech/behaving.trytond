# -*- encoding: utf-8 -*-

Feature: test_model.py from proteus-3.2.2/proteus/tests

   Scenario: proteus test_model.py
   
      Given Ensure that the "party" module is loaded
        and proteus/test_model test_class_cache
        and proteus/test_model test_class_method
        and proteus/test_model test_find
        and proteus/test_model test_many2one
        and proteus/test_model test_one2many
        and proteus/test_model test_many2many
        and proteus/test_model test_reference
        and proteus/test_model test_id_counter
        and proteus/test_model test_init
        and proteus/test_model test_save
        and proteus/test_model test_save_many2one
        and proteus/test_model test_save_one2many
        and proteus/test_model test_save_many2many
        and proteus/test_model test_cmp
        and proteus/test_model test_default_set
        and proteus/test_model test_delete
        and proteus/test_model test_on_change
        and proteus/test_model test_on_change_with
        and proteus/test_model test_on_change_set
