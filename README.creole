-*- encoding: utf-8 -*-

trytond_scenari
===============

This module provides scenario testing for trytond using behave BDD
(Behaviour Driven Development), and for loading trytond database
information and code using BDD. The module is a work-in-progress:
<http://github.com/lampmantech/trytond_scenari>

Behaviour Driven Development allows us to refactor the scenarios
in Tryton's doctests, to provide easy-to-use templates for end-users
to carry out the major tasks of Tryton. By migrating doctest scenarios to
trytond_scenari, the testing moves from the developer into the hands
of the end-user. At the same time, duplication of code is eliminated.

Tests are contained is textual feature files written in a
domain specific natural language with a Gherkin syntax, in the files:
   features/*.feature
The steps of the language draw on the definitions in:
   features/steps/*.py
For modularity, there is a local python module of undecorated python code:
  features/steps/support/

trytond_scenari is inspired by OpenERPScenario:
 <http:///launchpad.net/~camptocamp/oerpscenario/>
with uses behave:
 <http://pythonhosted.org/behave>
for BDD testing of OpenERP (v6.x and 7.0).
trytond_scenari uses proteus.

Installation
------------

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
database_name = test30
database_type = postgres
config_file = /etc/trytond.conf

[scenari]
verbosity = 0
tracer =
```

If the trytond database does not exist, it will be created.  As a
rule, these tests to not tear down what they have done at the end, so
that can be adapted to load database information and code into
production systems, as well as testing. If you are running the tests
in trytond_scenari, you must drop the database created in a previous run.
This also means that the order of execution of feature files may be
important, if one step builds on a previous one, or interferes with it.

As a rule, all tests within a directory should not
interfere with each other, but dont be surprised
if there in interference between directories.

If you set tracer in the scenari section of the
configuration file to be pdb, it will drop you into
the pdb debugger on an error, if you invoked behave 
with the --stop flag (stop at the first error).
You must also use the behave option --no-capture.

Behave is monkey-patched by environment.py to allow backslashes \
at the end of a line in feature files, to allow long verbose steps.
Whitespace both sides of the backslash are collapsed to one space.

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

Documentation
-------------

For the moment, the documentation is in the docstrings to the steps. 
I've writen a simple shell script that can harvest these for the
documentation so that the documentation can be automatically generated
from the steps; if you think it's a hack (it is), write a better one!


Versions
--------

To see what this version is, look at the first date in 
the file CHANGELOG.txt.

Active development is on Tryton 3.2. There is a bug under
3.2 that hits the country field in party.address; look for
the comment "Just junk the field value for now" in
features/steps/support/fields.py

This should work with Tryton 3.0 with no problems.

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

