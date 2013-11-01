-*- encoding: utf-8 -*-

trytond_scenari
===============

Scenario testing for trytond using behave BDD
(Behaviour Driven Development), and for loading
trytond database information and code using BDD.
<http://github.com/lampmantech/trytond_scenari>

trytond_scenari is inspired by OpenERPScenario:
 <http:///launchpad.net/~camptocamp/oerpscenario/>
with uses behave
 <http://pythonhosted.org/behave>
for BDD testing of OpenERP (v6.x and 7.0).
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
```
  behave --stop features/behave_test.feature
```

Configuration
-------------

The file
```
features/environment.cfg
```
contains the configuration information for the trytond
server you are testing. Edit the settings to suit your setup;
the default values are:

```
[trytond]
user = admin
password = admin
database_name = test28
database_type = postgres
config_file = /etc/trytond.conf

[scenari]
verbosity = 0
tracer =
```

If the trytond database does not exist, it will be
created.  As a rule, these tests to not tear down
what they have done at the end, so that can be
adapted to load database information and code
into production systems, as well as testing. This
also means that the order of execution of feature
files may be important, if one step builds on a previous,
or interferes with it.

As a rule, all tests within a directory should not
interfere with each other, but dont be surprised
if there in interference between directories.

If you set tracer in the scenari section of the
configuration file to be pdb, it will drop you into
the pdb debugger on an error, if you invoked behave 
with the --stop flag (stop at the first error).

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

Steps are often preceded by a label such as TS/SAR
as a way of keeping steps from different modules from
interfering with each other. The label is arbitrary
but should be short, like T/A/SAR for
trytond/account/scenario_account_reconciliation
Generic steps, that are likely to be used by all scenari,
may have no label.

Versions
--------

To see what this version is, look at the first date in 
the file CHANGELOG.txt.

Active development is on Tryton 3.0.

This should work with Tryton 2.8, but you should make a
simple change to the trytond_proteus source code.
proteus-2.8.*/proteus/config.py in class TrytondConfig
after the line:
        database = Database().connect()
add the line:
        self.database = database


Issues
------

Use the issue tracker on github.com:
<http://github.com/lampmantech/trytond_scenari>

