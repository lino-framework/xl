# -*- coding: UTF-8 -*-
# Copyright 2008-2017 Luc Saffre
# License: BSD (see file COPYING for details)

from __future__ import unicode_literals
from __future__ import print_function

from lino.api import dd, _

from lino_xl.lib.contacts.roles import ContactsStaff


class ClientContactTypes(dd.Table):
    help_text = _("Liste des types de contacts client.")
    model = 'clients.ClientContactType'
    required_roles = dd.login_required(ContactsStaff)

    # TODO: `can_refund` is injected in aids, `is_bailiff` in debts
    # NOTE: this is being overridden by lino_welfare.projects.eupen
    detail_layout = """
    id name
    clients.PartnersByClientContactType
    clients.ClientContactsByType
    """

    column_names = 'id name common_contact_type *'

    stay_in_grid = True


class ClientContacts(dd.Table):
    required_roles = dd.login_required(ContactsStaff)
    # help_text = _("Liste des contacts clients.")
    model = 'clients.ClientContact'


class ContactsByClient(ClientContacts):
    required_roles = dd.login_required()
    master_key = 'client'
    column_names = 'type company contact_person remark *'
    label = _("Contacts")
    auto_fit_column_widths = True


class ClientContactsByType(ClientContacts):
    required_roles = dd.login_required()
    master_key = 'type'
    column_names = 'company contact_person client remark *'
    label = _("Contacts")
    auto_fit_column_widths = True


class ClientContactsByCompany(ClientContacts):
    required_roles = dd.login_required()
    master_key = 'company'
    column_names = 'client contact_person remark *'
    label = _("Client contacts")
    auto_fit_column_widths = True


contacts = dd.resolve_app('contacts')

class PartnersByClientContactType(contacts.Partners):
    master_key = 'client_contact_type'
    column_names = 'name id mti_navigator *'


