# -*- coding: UTF-8 -*-
# Copyright 2009-2016 Luc Saffre
#
# This file is part of Lino XL.
#
# Lino XL is free software: you can redistribute it and/or modify it
# under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.
#
# Lino XL is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public
# License along with Lino XL.  If not, see
# <http://www.gnu.org/licenses/>.

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
    version='1.7.3',
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

SETUP_INFO.update(long_description="""

The **Lino Extensions Library** is a collection of plugins used by
many Lino projects.

This package is written and maintained by the same author, but not
part of the Lino core because it adds a given set of solutions for
"Enterprise" style applications.  It is documented together with the
core at http://www.lino-framework.org

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
lino_xl.lib.teams
lino_xl.lib.cal
lino_xl.lib.cal.fixtures
lino_xl.lib.cal.management
lino_xl.lib.cal.management.commands
lino_xl.lib.cal.workflows
lino_xl.lib.concepts
lino_xl.lib.contacts
lino_xl.lib.contacts.fixtures
lino_xl.lib.contacts.management
lino_xl.lib.contacts.management.commands
lino_xl.lib.countries
lino_xl.lib.countries.fixtures
lino_xl.lib.cv
lino_xl.lib.cv.fixtures
lino_xl.lib.dupable_partners
lino_xl.lib.dupable_partners.fixtures
lino_xl.lib.eid_jslib
lino_xl.lib.eid_jslib.beid
lino_xl.lib.events
lino_xl.lib.events.fixtures
lino_xl.lib.events.tests
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
lino_xl.lib.polls
lino_xl.lib.polls.fixtures
lino_xl.lib.postings
lino_xl.lib.products
lino_xl.lib.products.fixtures
lino_xl.lib.projects
lino_xl.lib.properties
lino_xl.lib.properties.fixtures
lino_xl.lib.reception
lino_xl.lib.rooms
lino_xl.lib.stars
lino_xl.lib.statbel
lino_xl.lib.statbel.countries
lino_xl.lib.statbel.countries.fixtures
lino_xl.lib.thirds
lino_xl.lib.topics
lino_xl.lib.workflows
lino_xl.lib.xl
""".splitlines() if n])

SETUP_INFO.update(message_extractors={
    'lino_xl': [
        ('**/sandbox/**', 'ignore', None),
        ('**/cache/**', 'ignore', None),
        ('**.py', 'python', None),
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
# add_package_data('lino_xl.lib.cal', 'config/*.odt')
# add_package_data('lino_xl.lib.notes', 'config/notes/Note/*.odt')
# add_package_data('lino_xl.lib.outbox', 'config/outbox/Mail/*.odt')

# l = add_package_data('lino_xl.lib.lino_startup')
# for lng in 'de fr et nl'.split():
#     l.append('lino/modlib/lino_startup/locale/%s/LC_MESSAGES/*.mo' % lng)
