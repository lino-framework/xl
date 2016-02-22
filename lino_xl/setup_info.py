# -*- coding: UTF-8 -*-
# Copyright 2009-2016 Luc Saffre
# License: BSD (see file COPYING for details)

# ~ Note that this module may not have a docstring because any
# ~ global variable defined here will override the global
# ~ namespace of lino/__init__.py who includes it with execfile.

# This module is part of the Lino test suite.
# To test only this module:
#
#   $ python setup.py test -s tests.PackagesTests

from __future__ import unicode_literals

SETUP_INFO = dict(
    name='lino_xl',
    version='1.0.0',
    install_requires=['lino', 'appy', 'fuzzy', ],
    tests_require=[],
    description="Lino Extensions Library",
    license='BSD License',
    include_package_data=True,
    zip_safe=False,
    author='Luc Saffre',
    author_email='luc.saffre@gmail.com',
    url="http://www.lino-framework.org",
    # ~ test_suite = 'lino_xl.test_apps',
    test_suite='tests',
    classifiers="""\
  Programming Language :: Python
  Programming Language :: Python :: 2
  Development Status :: 5 - Production/Stable
  Environment :: Web Environment
  Framework :: Django
  Intended Audience :: Developers
  Intended Audience :: System Administrators
  License :: OSI Approved :: BSD License
  Natural Language :: English
  Natural Language :: French
  Natural Language :: German
  Operating System :: OS Independent
  Topic :: Database :: Front-Ends
  Topic :: Home Automation
  Topic :: Office/Business
  Topic :: Software Development :: Libraries :: Application Frameworks""".splitlines())

SETUP_INFO.update(long_description="""\
This is a collection of plugins for the Lino framework.
""")

SETUP_INFO.update(packages=[str(n) for n in """
lino_xl
lino_xl.lib
lino_xl.lib.addresses
lino_xl.lib.addresses.fixtures
lino_xl.lib.appypod
lino_xl.lib.beid
lino_xl.lib.blogs
lino_xl.lib.boards
lino_xl.lib.cal
lino_xl.lib.cal.fixtures
lino_xl.lib.cal.management
lino_xl.lib.cal.management.commands
lino_xl.lib.cal.workflows
lino_xl.lib.cv
lino_xl.lib.cv.fixtures
lino_xl.lib.dupable_partners
lino_xl.lib.dupable_partners.fixtures
lino_xl.lib.excerpts
lino_xl.lib.excerpts.fixtures
lino_xl.lib.extensible
lino_xl.lib.families
lino_xl.lib.households
lino_xl.lib.households.fixtures
lino_xl.lib.humanlinks
lino_xl.lib.humanlinks.fixtures
lino_xl.lib.lists
lino_xl.lib.lists.fixtures
lino_xl.lib.notes
lino_xl.lib.notes.fixtures
lino_xl.lib.outbox
lino_xl.lib.outbox.fixtures
lino_xl.lib.pages
lino_xl.lib.pages.fixtures
lino_xl.lib.postings
lino_xl.lib.products
lino_xl.lib.products.fixtures
lino_xl.lib.projects
lino_xl.lib.properties
lino_xl.lib.properties.fixtures
lino_xl.lib.reception
lino_xl.lib.rooms
lino_xl.lib.stars
lino_xl.lib.thirds
lino_xl.lib.workflows
lino_xl.projects
lino_xl.projects.cms
lino_xl.projects.cms.fixtures
lino_xl.projects.cms.tests
lino_xl.projects.crl
lino_xl.projects.crl.fixtures
lino_xl.projects.homeworkschool
lino_xl.projects.homeworkschool.fixtures
lino_xl.projects.homeworkschool.settings
lino_xl.projects.i18n
lino_xl.projects.igen
lino_xl.projects.igen.tests
lino_xl.projects.min1
lino_xl.projects.min1.settings
lino_xl.projects.min2
lino_xl.projects.min2.modlib
lino_xl.projects.min2.modlib.contacts
lino_xl.projects.min2.modlib.contacts.fixtures
lino_xl.projects.min2.settings
lino_xl.projects.min2.tests
""".splitlines() if n])

SETUP_INFO.update(message_extractors={
    'lino_xl': [
        ('**/sandbox/**', 'ignore', None),
        ('**/cache/**', 'ignore', None),
        ('**.py', 'python', None),
        ('**/linoweb.js', 'jinja2', None),
        ('**/config/**.html', 'jinja2', None),
    ],
})

SETUP_INFO.update(package_data=dict())


def add_package_data(package, *patterns):
    package = str(package)
    l = SETUP_INFO['package_data'].setdefault(package, [])
    l.extend(patterns)
    return l


add_package_data('lino_xl', 'config/*.odt')
add_package_data('lino_xl.lib.cal', 'config/*.odt')
add_package_data('lino_xl.lib.outbox', 'config/outbox/Mail/*.odt')

# l = add_package_data('lino_xl.lib.lino_startup')
# for lng in 'de fr et nl'.split():
#     l.append('lino/modlib/lino_startup/locale/%s/LC_MESSAGES/*.mo' % lng)
