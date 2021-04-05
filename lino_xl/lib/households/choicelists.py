# -*- coding: UTF-8 -*-
# Copyright 2012-2019 Rumma & Ko Ltd
# License: GNU Affero General Public License v3 (see file COPYING for details)

from lino.api import dd, _
from lino_xl.lib.contacts.roles import ContactsStaff


class MemberDependencies(dd.ChoiceList):
    verbose_name = _("Dependency")
    verbose_name_plural = _("Household Member Dependencies")

add = MemberDependencies.add_item
add('01', _("At full charge"), 'full')
add('02', _("Not at charge"), 'none')
add('03', _("At shared charge"), 'shared')


class MemberRoles(dd.ChoiceList):
    required_roles = dd.login_required(ContactsStaff)
    verbose_name = _("Role")
    verbose_name_plural = _("Household member roles")

add = MemberRoles.add_item
add('01', _("Head of household"), 'head')
add('02', _("Spouse"), 'spouse')  # married
add('03', _("Partner"), 'partner')  # not married
add('04', _("Cohabitant"), 'cohabitant')  # not a relative but living here
add('05', _("Child"), 'child')  # i.e. of at least one parent
add('06', _("Relative"), 'relative')  # relative who does not live here
add('07', _("Adopted child"), 'adopted')
add('08', _("Foster-child"), 'foster')
add('10', _("Other"), 'other')  # neither cohabitant nor relaive
# add('10', _("Child of head"), 'child_of_head')
# add('11', _("Child of partner"), 'child_of_partner')

parent_roles = (MemberRoles.head, MemberRoles.spouse,
                MemberRoles.partner, MemberRoles.cohabitant)

child_roles = (MemberRoles.child, MemberRoles.adopted)
               # MemberRoles.child_of_head, MemberRoles.child_of_partner)
