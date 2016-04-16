# -*-mode: python; py-indent-offset: 4; indent-tabs-mode: nil; encoding: utf-8-dos; coding: utf-8 -*-

"""
Behavior-Driven-Development testing for Tryton ERP: http://tryton.org

It has been structured to use the {{{behaving}}} namespace from
https://github.com/ggozad/behaving/ and requires that package as a prerequisite,
which must be installed before installing this package.

This package is Python 2 only for the moment.

The code is being developed Unix-only for now but there is no reason
that it will not work on Windows.
 
"""
import sys
import os
import glob
from setuptools import setup, find_packages

version = '0.1.0'

dParams = dict(name='behaving.trytond',
               version=version,
               description="Behavior-Driven-Development testing for Tryton ERP",
               long_description=open("README.rst").read(),
               classifiers=[
                   "Development Status :: 4 - Beta",
                   "Environment :: Console",
                   "Framework :: Tryton",
                   "Intended Audience :: Developers",
                   "Intended Audience :: Financial and Insurance Industry",
                   "Topic :: Software Development :: Testing",
                   "Topic :: Software Development :: Libraries",
                   "Topic :: Software Development :: Libraries :: Python Modules"
#                   "Topic :: Utilities",
#                   "Operating System :: Microsoft :: Windows",
                   "Operating System :: POSIX",
                   "Programming Language :: Python",
                   "Programming Language :: Python :: 2",
                   "Programming Language :: Python :: 2 :: Only",
                   "Topic :: Software Development :: Quality Assurance",
                   "Topic :: Software Development :: Testing",
                   ],
               keywords="BDD Behavior-Driven-Development testing tryton behave",
               author='Lampman Tech',
               url='http://github.com/lampmantech/behaving.trytond',
               license='GPL',
               packages=find_packages('src', exclude=['tests']),
               package_dir={'': 'src'},
               namespace_packages=['behaving'],
               include_package_data=True,
               zip_safe=False,
               install_requires=['behaving', 'configobj'], # sh
               # The code is being developed Unix-only for now - 'Windows', 
               platforms = ['Linux', 'Unix', 'MacOS X'],
               tests_require=['behave', 'proteus', 'trytond'],
               data_files=[('share/doc/behaving.trytond/html',
                                glob.glob('docs/html/*.html'))],
           )

BEHAVE_ARGS="--no-capture --no-capture-stderr --no-skipped --verbose"
def iMain():
    if sys.argv[-1] == 'publish':
        os.system(sys.executable +" setup.py sdist --formats=gztar upload --show-response")
        os.system(sys.executable +" setup.py bdist_wheel upload --show-response")
        print "You probably want to also tag the version now:"
        print "  git tag -a %s -m 'version %s'" % (version, version, )
        print "  git push --tags"
        return 0
    if sys.argv[-1] == 'test':
        try:
            modules = map(__import__, dParams['tests_require'])
        except ImportError as e:
            err_msg = e.message.replace("No module named ", "")
            msg = "%s is not installed. Install your test requirments." % err_msg
            raise ImportError(msg)
        sStartDir = os.path.dirname(os.path.realpath(__file__))
        sCfgFile = os.path.join(sStartDir, 'src/behaving/tests/features/environment.cfg')
        assert os.file.exists(sCfgFile), \
          "You must create and edit the configuration file before you can run the tests\n" \
          + "Look at the documentation in wiki/Installation.creole\n" \
          sCfgFile
          
        from behave.__main__ import main as behave_main
        # We run the behave tests from the src directory
        # so that behaving in on our sys.path, to run from source.
        os.chdir(os.path.join(sStartDir, 'src'))
        
        largs = BEHAVE_ARGS.split()
        # You cannot run all the features recursively.
        # Look at the documentation in wiki/Installation.creole
        largs.extend(['behaving/tests/features/behave_test.feature'])
        iRetval = behave_main(largs)
        return iRetval
    
    if '--help' in sys.argv:
        print """
Extra commands:

  setup.py publish    will sdist upload the distribution to pypi
  setup.py test       will run a very basic test of the software
"""
        # drop through
        
    setup(**dParams)
    return 0

if __name__ == '__main__':
    if sys.version_info[:2] < (2, 6):
        sys.exit('behaving.trytond requires Python 2.6 or higher.')
    sys.exit(iMain())
