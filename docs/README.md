# -*- mode: text; fill-column: 75; coding: utf-8-unix; encoding: utf-8 -*-

A quick hack to pull the docstrings out of each step is in
  bash steps_to_txt.bash
to make a starting point for documentation.

We'll do more when the docstrings are more complete,
and the steps get clearer names.

Converting doctest scenarios to trytond_scenari:

A quick hack to format the Python code in a doctest scenario is in
  bash ../bin/rst_to_feature.sh
if you have Emacs installed, to make a starting point for features.

Steps are often preceded by a label such as T/A/SAR
as a way of keeping steps from different modules from
interfering with each other. The label is arbitrary
but should be short, like T/A/SAR for
trytond/account/scenario_account_reconciliation etc.

Generic steps, that are likely to be used by all scenari, may have no
label, and are usually defined either in the generic
scenario_doctests.py, or the name equivalent to the trytond_ module
(e.g. trytond_account.py). As specific steps get generalized and serve
for many different scenari, they will get pulled out of the
scenario_*.py into the generic file trytond_*.py.  If you are
contributing on github, it's best to write your steps with a label and
add FixMe tag to signal that you think the step is generic.

You will probably have to clean up the doctest code to make it
able to be broken up in steps, but there are lots of good examples.
