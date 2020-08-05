# -*- coding: UTF-8 -*-
# Copyright 2009-2020 Rumma & Ko Ltd
# License: BSD (see file COPYING for details)

# Note that this module may not have a docstring because any
# global variable defined here will override the global
# namespace of lino/__init__.py who includes it with execfile.

# This module is part of the Lino test suite.
# To test only this module:
#
#   $ python setup.py test -s tests.PackagesTests


SETUP_INFO = dict(
    name='lino-xl',
    version='20.8.0',
    install_requires=['lino'],  # odfpy dependency now in lino_xl.lib.appypod
    tests_require=[],
    description="Lino Extensions Library",
    license='BSD-2-Clause',
    author='Rumma & Ko Ltd',
    author_email='info@saffre-rumma.net',
    url="http://www.lino-framework.org",
    # ~ test_suite = 'lino_xl.test_apps',
    test_suite='tests')

SETUP_INFO.update(long_description="""

The **Lino Extensions Library** is a collection of plugins used by many Lino
applications.

- This repository is considered an integral part of the Lino framework, which is
  documented as a whole in the `Lino Book
  <http://www.lino-framework.org/about/overview.html>`__.

- Your feedback is welcome.  Our `community page
  <http://www.lino-framework.org/community>`__ explains how to contact us.

- API changes to this repository are logged at
  http://www.lino-framework.org/changes/


""")

SETUP_INFO.update(packages=[str(n) for n in """
lino_xl
lino_xl.lib
lino_xl.lib.addresses
lino_xl.lib.addresses.fixtures
lino_xl.lib.ana
lino_xl.lib.ana.fixtures
lino_xl.lib.b2c
lino_xl.lib.b2c.fixtures
lino_xl.lib.appypod
lino_xl.lib.beid
lino_xl.lib.blogs
lino_xl.lib.boards
lino_xl.lib.github
lino_xl.lib.groups
lino_xl.lib.groups.fixtures
lino_xl.lib.googleapi_people
lino_xl.lib.teams
lino_xl.lib.bevat
lino_xl.lib.bevat.fixtures
lino_xl.lib.bevats
lino_xl.lib.bevats.fixtures
lino_xl.lib.eevat
lino_xl.lib.eevat.fixtures
lino_xl.lib.cal
lino_xl.lib.cal.fixtures
lino_xl.lib.cal.management
lino_xl.lib.cal.management.commands
lino_xl.lib.cal.workflows
lino_xl.lib.calview
lino_xl.lib.calview.fixtures
lino_xl.lib.clients
lino_xl.lib.coachings
lino_xl.lib.coachings.fixtures
lino_xl.lib.concepts
lino_xl.lib.contacts
lino_xl.lib.contacts.fixtures
lino_xl.lib.contacts.management
lino_xl.lib.contacts.management.commands
lino_xl.lib.countries
lino_xl.lib.countries.fixtures
lino_xl.lib.courses
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
lino_xl.lib.orders
lino_xl.lib.extensible
lino_xl.lib.families
lino_xl.lib.households
lino_xl.lib.households.fixtures
lino_xl.lib.healthcare
lino_xl.lib.healthcare.fixtures
lino_xl.lib.humanlinks
lino_xl.lib.humanlinks.fixtures
lino_xl.lib.lists
lino_xl.lib.lists.fixtures
lino_xl.lib.caldav
lino_xl.lib.mailbox
lino_xl.lib.mailbox.fixtures
lino_xl.lib.meetings
lino_xl.lib.notes
lino_xl.lib.notes.fixtures
lino_xl.lib.outbox
lino_xl.lib.outbox.fixtures
lino_xl.lib.pages
lino_xl.lib.pages.fixtures
lino_xl.lib.phones
lino_xl.lib.phones.fixtures
lino_xl.lib.pisa
lino_xl.lib.polls
lino_xl.lib.polls.fixtures
lino_xl.lib.postings
lino_xl.lib.products
lino_xl.lib.products.fixtures
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
lino_xl.lib.userstats
lino_xl.lib.xl

lino_xl.lib.finan
lino_xl.lib.finan.fixtures
lino_xl.lib.ledger
lino_xl.lib.ledger.fixtures
lino_xl.lib.ledger.management
lino_xl.lib.ledger.management.commands
lino_xl.lib.sales
lino_xl.lib.sales.fixtures
lino_xl.lib.sepa
lino_xl.lib.inbox
lino_xl.lib.inspect
lino_xl.lib.invoicing
lino_xl.lib.invoicing.fixtures
lino_xl.lib.sepa.fixtures
lino_xl.lib.tim2lino
lino_xl.lib.tim2lino.fixtures
lino_xl.lib.trends
lino_xl.lib.trends.fixtures
lino_xl.lib.vat
lino_xl.lib.vat.fixtures
lino_xl.lib.vatless

lino_xl.lib.deploy
lino_xl.lib.deploy.fixtures
lino_xl.lib.sheets
lino_xl.lib.sheets.fixtures
lino_xl.lib.tickets
lino_xl.lib.tickets.fixtures
lino_xl.lib.skills
lino_xl.lib.working
lino_xl.lib.working.fixtures
lino_xl.lib.online
lino_xl.lib.online.users
lino_xl.lib.online.users.fixtures
lino_xl.lib.votes
lino_xl.lib.votes.fixtures
lino_xl.lib.uploads
lino_xl.lib.uploads.fixtures
""".splitlines() if n])

SETUP_INFO.update(classifiers="""\
Programming Language :: Python
Programming Language :: Python :: 3
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
Topic :: Office/Business
Topic :: Software Development :: Libraries :: Application Frameworks""".splitlines())

SETUP_INFO.update(message_extractors={
    'lino_xl': [
        ('**/sandbox/**', 'ignore', None),
        ('**/cache/**', 'ignore', None),
        ('**.py', 'python', None),
        ('**/config/**.html', 'jinja2', None),
    ],
})

# SETUP_INFO.update(include_package_data=True, zip_safe=False)
SETUP_INFO.update(include_package_data=True)

# SETUP_INFO.update(package_data=dict())


# def add_package_data(package, *patterns):
#     package = str(package)
#     l = SETUP_INFO['package_data'].setdefault(package, [])
#     l.extend(patterns)
#     return l
#
#
# add_package_data('lino_xl.lib.mailbox', 'fixtures/*.mbox')
# add_package_data('lino_xl.lib.tickets', 'fixtures/*.tsv')
# add_package_data('lino_xl.lib.tickets', 'config/tickets/Site/*.html')
# add_package_data('lino_xl.lib.tickets', 'config/tickets/Ticket/*.html')
# add_package_data('lino_xl.lib.tickets', 'config/tickets/Ticket/*.eml')
# add_package_data('lino_xl.lib.beid', 'config/beid/*.js')
# add_package_data('lino_xl.lib.beid', 'static/eidreader/*.jar')
# add_package_data('lino_xl.lib.beid', 'static/eidreader/*.jnlp')
# add_package_data('lino_xl.lib.beid', '*.jpg')
# add_package_data('lino_xl.lib.finan', 'config/finan/PaymentOrder/*.*')
# add_package_data('lino_xl.lib.finan', 'config/finan/BankStatement/*.dtl')
# add_package_data('lino_xl.lib.finan', 'templates/*.html')
# add_package_data('lino_xl.lib.countries', 'fixtures/*.xml')
# add_package_data('lino_xl.lib.countries', 'fixtures/*.csv')
# add_package_data('lino_xl.lib.contacts', 'config/contacts/Person/*.odt')
# add_package_data('lino_xl.lib.contacts', 'templates/*.html')
# add_package_data('lino_xl.lib.working', 'config/working/ServiceReport/*.html')
# add_package_data('lino_xl.lib.sales', 'config/sales/VatProductInvoice/*.html')
# add_package_data('lino_xl.lib.sales', 'config/sales/VatProductInvoice/*.odt')
# add_package_data('lino_xl.lib.pisa', 'config/*.html')
# add_package_data('lino_xl.lib.pages', 'config/pages/*.html')
# add_package_data('lino_xl.lib.outbox', 'config/outbox/Mail/*.odt')
# add_package_data('lino_xl.lib.notes', 'config/notes/Note/*.odt')
# add_package_data('lino_xl.lib.notes', 'config/notes/Note/*.html')
# add_package_data('lino_xl.lib.notes', 'templates/notes/Note/*.html')
# add_package_data('lino_xl.lib.notes', 'templates/*.html')
# add_package_data('lino_xl.lib.lists', 'config/lists/List/*.html')
# add_package_data('lino_xl.lib.ledger', 'config/contacts/Partner/*.html')
# add_package_data('lino_xl.lib.ledger', 'config/ledger/Situation/*.odt')
# add_package_data('lino_xl.lib.excerpts', 'config/excerpts/Excerpt/*.odt')
# add_package_data('lino_xl.lib.excerpts', 'config/excerpts/Excerpt/*.html')
# add_package_data('lino_xl.lib.deploy', 'config/deploy/Milestone/*.html')
# add_package_data('lino_xl.lib.extensible', 'config/snippets/*.js')
# add_package_data('lino_xl.lib.sepa', 'config/iban/*.js')
#
# add_package_data('lino_xl', 'config/*.odt')
# add_package_data('lino_xl.lib.cal', 'config/*.odt')
# add_package_data('lino_xl.lib.outbox', 'config/outbox/Mail/*.odt')
# # add_package_data('lino_xl.lib.cal', 'config/*.odt')
# # add_package_data('lino_xl.lib.notes', 'config/notes/Note/*.odt')
# # add_package_data('lino_xl.lib.outbox', 'config/outbox/Mail/*.odt')

# l = add_package_data('lino_xl.lib.xl')
# for lng in 'de es fr et nl pt pt-br'.split():
#     l.append('lino/modlib/xl/locale/%s/LC_MESSAGES/*.mo' % lng)
