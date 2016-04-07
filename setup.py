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
import glob
from setuptools import setup, find_packages

version = '0.0.8.dev1'

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
                   "Operating System :: POSIX :: AIX",
                   "Operating System :: POSIX :: Linux",
                   "Programming Language :: Python",
                   "Programming Language :: Python :: 2",
                   "Programming Language :: Python :: 2.7",
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
               install_requires=['setuptools', 'behaving'],
               # The code is being developed Unix-only for now - 'Windows', 
               platforms = ['Linux', 'Unix', 'MacOS X'],
               tests_require=['behave', 'proteus', 'trytond'],
               data_files=[('share/doc/behaving.trytond/html',
                                glob.glob('docs/html/*.html'))],
           )

if __name__ == '__main__':
    if sys.version_info[:2] < (2, 6):
        sys.exit('behaving.trytond requires Python 2.6 or higher.')

    setup(**dParams)
