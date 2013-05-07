# -*- coding: utf-8 -*-
"""Installer for the observatorio.transmogrifier package."""

from setuptools import find_packages
from setuptools import setup

import os


def read(*rnames):
    return open(os.path.join(os.path.dirname(__file__), *rnames)).read()

long_description = \
    read('README.rst') + \
    read('docs', 'CHANGELOG.rst') + \
    read('docs', 'LICENSE.rst')

setup(
    name='observatorio.transmogrifier',
    version='0.1',
    description=".",
    long_description=long_description,
    # Get more from http://pypi.python.org/pypi?%3Aaction=list_classifiers
    classifiers=[
        "Framework :: Plone",
        "Programming Language :: Python",
    ],
    keywords='.',
    author='Gustavo Lepri.',
    author_email='gustavolepri@gmail.com',
    url='http://pypi.python.org/pypi/observatorio.transmogrifier',
    license='BSD',
    packages=find_packages('src', exclude=['ez_setup']),
    namespace_packages=['observatorio'],
    package_dir={'': 'src'},
    include_package_data=True,
    zip_safe=False,
    install_requires=[
        'setuptools',
        'collective.transmogrifier',
        'plone.app.transmogrifier',
        'collective.blueprint.jsonmigrator',
        'transmogrify.dexterity',
    ],
    extras_require={
        'test': ['plone.app.testing',],
    },
    entry_points="""
    [z3c.autoinclude.plugin]
    target = plone
    """,
)
