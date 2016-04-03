# -*- encoding: utf-8 -*-

@works32 @works34 @works36
Feature:    test_model.py from proteus-3.2.2/proteus/tests

  Scenario: proteus test_model.py
   
      Given Ensure that the "party" module is loaded
        And proteus/test_model test_class_cache
        And proteus/test_model test_class_method
        And proteus/test_model test_find
        And proteus/test_model test_many2one
        And proteus/test_model test_one2many
        And proteus/test_model test_many2many
        And proteus/test_model test_reference
        And proteus/test_model test_id_counter
        And proteus/test_model test_init
        And proteus/test_model test_save
        And proteus/test_model test_save_many2one
# ininite recursion:
#       and proteus/test_model test_save_one2many
        And proteus/test_model test_save_many2many
        And proteus/test_model test_cmp
        And proteus/test_model test_default_set
        And proteus/test_model test_delete
        And proteus/test_model test_on_change
        And proteus/test_model test_on_change_with
        And proteus/test_model test_on_change_set
