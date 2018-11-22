# -*- coding: UTF-8 -*-
# Copyright 2008-2018 Rumma & Ko Ltd
# License: BSD (see file COPYING for details)

from __future__ import unicode_literals
from __future__ import print_function

import logging
logger = logging.getLogger(__name__)

from django.db import models
from django.db.models import Q
from django.conf import settings
from django.core.exceptions import ValidationError
from django.utils.translation import ugettext_lazy as _
from lino.api import dd, rt

from lino import mixins

from lino.modlib.users.mixins import UserAuthored
from lino.modlib.checkdata.choicelists import Checker

from .mixins import ClientContactBase
from .choicelists import ClientStates, ClientEvents, KnownContactTypes


try:
    client_model = dd.plugins.clients.client_model
except AttributeError:  # for Sphinx autodoc
    client_model = None
    
class ClientContactType(mixins.BabelNamed):
    class Meta:
        app_label = 'clients'
        verbose_name = _("Client Contact type")
        verbose_name_plural = _("Client Contact types")
        abstract = dd.is_abstract_model(__name__, 'ClientContactType')

    known_contact_type = KnownContactTypes.field(blank=True)

class ClientContact(ClientContactBase):
    class Meta:
        app_label = 'clients'
        verbose_name = _("Client Contact")
        verbose_name_plural = _("Client Contacts")
        abstract = dd.is_abstract_model(__name__, 'ClientContact')
    #~ type = ClientContactTypes.field(blank=True)
    client = dd.ForeignKey(client_model)
    remark = models.TextField(_("Remarks"), blank=True)  # ,null=True)
    
    # allow_cascaded_delete = 'client'

    def full_clean(self, *args, **kw):
        if not self.remark and not self.type \
           and not self.company and not self.contact_person:
            raise ValidationError(_("Must fill at least one field."))
        super(ClientContact, self).full_clean(*args, **kw)


dd.update_field(ClientContact, 'contact_person',
                verbose_name=_("Contact person"))


dd.inject_field(
    'contacts.Partner', 'client_contact_type',
    dd.ForeignKey(
        'clients.ClientContactType', blank=True, null=True))

from lino_xl.lib.contacts.models import Partners

class PartnersByClientContactType(Partners):
    master_key = 'client_contact_type'
    column_names = "name address_column phone gsm email *"
    auto_fit_column_widths = True

