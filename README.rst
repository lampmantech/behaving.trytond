`http://github.com/lampmantech/trytond_scenari <http://github.com/lampmantech/trytond_scenari>`_

This module provides scenario testing for trytond using behave BDD
(Behaviour Driven Development), and for loading trytond database
information and code using BDD. The module is a work-in-progress.

Behaviour Driven Development allows us to refactor the scenarios
in Tryton's doctests, to provide easy-to-use templates for end-users
to carry out the major tasks of Tryton. By migrating doctest scenarios to
trytond_scenari, the testing moves from the developer into the hands
of the end-user. At the same time, duplication of code is eliminated.

Tests are contained is textual feature files written in a
domain specific natural language with a Gherkin syntax, in the files:
``features/*.feature``

The steps of the language draw on the Python definitions in:
``features/steps/*.py``

For modularity, there is a local python module of undecorated Python code:
``features/steps/support/``

trytond_scenari is inspired by OpenERPScenario:
`https:///github.com/camptocamp/oerpscenario/ <https:///github.com/camptocamp/oerpscenario/>`_
(formerly `http:///launchpad.net/~camptocamp/oerpscenario/) <http:///launchpad.net/~camptocamp/oerpscenario/)>`_
which uses behave: `http://pythonhosted.org/behave <http://pythonhosted.org/behave>`_
for BDD testing of OpenERP (v6.x and 7.0).
trytond_scenari uses proteus.

Active development is on Tryton 3.6; see

* Testing (https://github.com/lampmantech/trytond_scenari/wiki/Testing)

Documentation
=============

* Home (https://github.com/lampmantech/trytond_scenari/wiki/Home)

The feature files, and the summaries of the available steps, are in the Wiki:

* TitleIndex (https://github.com/lampmantech/trytond_scenari/wiki/TitleIndex)

Project
=======

Use the Wiki to start topics for discussion. You will need to be
signed into github.com to edit in the wiki.

Please format wiki pages as Creole.
For info on Creole, see `http://wikicreole.org/ <http://wikicreole.org/>`_

Please file any bugs in the
issues tracker (https://github.com/lampmantech/trytond_scenari/issues).