`http://github.com/lampmantech/behaving.trytond <http://github.com/lampmantech/behaving.trytond>`_

This package provides scenario testing for trytond using behave and behaving
BDD (Behaviour Driven Development), and for loading trytond database
data and code using BDD. The module is a work-in-progress.

Behaviour Driven Development allows us to refactor the scenarios
in Tryton's doctests, to provide easy-to-use templates for end-users
to carry out the major tasks of Tryton. By migrating doctest scenarios to
behave scenari, the testing moves from the developer into the hands
of the end-user. At the same time, duplication of code is eliminated.

Tests are contained is textual feature files written in a
domain specific natural language with a Gherkin syntax, in the files:
``src/behaving/tests/features/*/*.feature``

The steps of the domain language draw on the Python definitions in:
``src/behaving/tests/features/steps/*.py``

For modularity, there is a local python module of undecorated Python code:
``src/behaving/tests/features/steps/support/``

behaving.trytond is inspired by OpenERPScenario:
`https:///github.com/camptocamp/oerpscenario/ <https:///github.com/camptocamp/oerpscenario/>`_
(formerly `http:///launchpad.net/~camptocamp/oerpscenario/) <http:///launchpad.net/~camptocamp/oerpscenario/)>`_
which uses behave: `http://pythonhosted.org/behave <http://pythonhosted.org/behave>`_
for BDD testing of OpenERP (v6.x and 7.0).
behaving.trytond uses proteus.

It has been structured to use the ``behaving`` namespace from
`https://github.com/ggozad/behaving/ <https://github.com/ggozad/behaving/>`_ and requires that package as a prerequisite.
This allows us to draw from other ``behaving`` namespace packages, to use
``behaving.web`` for example to test ``sao``.

Active development is on Tryton 3.6; see

* `https://github.com/lampmantech/behaving.trytond/wiki/Testing <Testing>`_

Documentation
=============

The Documentation is in the Wiki:

* `https://github.com/lampmantech/behaving.trytond/wiki/Home <Home>`_

The feature files, and the summaries of the available steps, are in the Wiki:

* `https://github.com/lampmantech/behaving.trytond/wiki/Features <Features>`_

* `https://github.com/lampmantech/behaving.trytond/wiki/Steps <Steps>`_

* `https://github.com/lampmantech/behaving.trytond/wiki/TitleIndex <TitleIndex>`_

Project
=======

Use the Wiki to start topics for discussion. You will need to be
signed into github.com to edit in the wiki.

Please format wiki pages as Creole.
For info on Creole, see `http://wikicreole.org/ <http://wikicreole.org/>`_

Please file any bugs in the
`https://github.com/lampmantech/behaving.trytond/issues <issues tracker>`_.