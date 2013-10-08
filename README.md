-*- encoding: utf-8 -*-

trytond_scenari
===============

Scenario testing for trytond using behave BDD
(Behaviour Driven Development), and for loading 
trytond database information and code using BDD.

trytond_scenari is inspired by OpenERPScenario:
 <http:///launchpad.net/~camptocamp/oerpscenario/>
with uses behave 
 <http://pythonhosted.org/behave>
for BDD testing of OpenERP v6.x and 7.0. 
trytond_scenari uses proteus.

Tests are contained is textual feature files
   features/\*.feature
that draw on the definitions of their steps in
   features/steps/\*.py
For modularity, there is a local python module
of undecorated python code
  features/steps/support/

Once you have behave and proteus installed, there is no 
installation required for trytond_scenari: simply change 
to this directory and run behave. So far, it has only 
been tested on postgres backends using proteus. The
most trivial test, which does not even use trytond is:
  behave --stop features/1970-00-behave_test.feature 


Configuration
-------------

The file features/environment.cfg contains the configuration
information for the trytond server you are testing. Edit the
settings to suit your setup; the default values are:

```
[trytond]
user = admin
password = admin
database_name = test28
database_type = postgres
config_file = /etc/trytond.conf
```
If the trytond database does not exist, it will be
created.  As a rule, these tests to not tear down
what they have done at the end, so that can be
adapted to load database information and code
into production systems, as well as testing. This 
also means that the order of execution of feature
files may be important, if one step builds on a previous.

Organization
------------

By default, behave runs all \*.feature files in
the directory features/ and its sub-directories
(this can be controlled with the -i flag to behave).
This allows us to organize the feature tests
by the module layout in trytond. We will start
by pulling in the doctest \*.rst files, keeping
the same filename, to take advantage of behave's
refactoring, and to get the steps to have good coverage.

Feature filenames are often ordered with a year-month
numeric prefix to group together work of the same
timeframe, or to influence the execution order by behave.


