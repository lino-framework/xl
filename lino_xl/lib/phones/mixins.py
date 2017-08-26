# Copyright 2017 Luc Saffre
#
# License: BSD (see file COPYING for details)

"""
Model mixins for `lino_xl.lib.phones`.

"""

from __future__ import unicode_literals
from __future__ import print_function

from django.utils.translation import ugettext_lazy as _

from lino.utils import join_elems
from lino.api import rt, dd
from lino.utils.xmlgen.html import E
from lino.core.diff import ChangeWatcher
from lino.mixins import Contactable, Phonable

from .choicelists import ContactDetailTypes


class ContactDetailsOwner(Contactable, Phonable):
    """Base class for the potential owner of contact details.

    """
    class Meta:
        abstract = True

    def sync_primary_contact_detail(self, ar):
        watcher = ChangeWatcher(self)
        self.sync_primary_contact_detail_()
        watcher.send_update(ar)

    def sync_primary_contact_detail_(self):
        ContactDetail = rt.modules.phones.ContactDetail
        for cdt in ContactDetailTypes.get_list_items():
            k = cdt.field_name
            if k:
                fld = self._meta.get_field(k)
                kw = dict(partner=self, primary=True, detail_type=cdt)
                try:
                    cd = ContactDetail.objects.get(**kw)
                    setattr(self, k, cd.value)
                except ContactDetail.DoesNotExist:
                    setattr(self, k, fld.get_default())
                self.save()

    def get_overview_elems(self, ar):
        # elems = super(ContactDetailsOwner, self).get_overview_elems(ar)
        yield rt.models.phones.ContactDetailsByPartner.get_slave_summary(
            self, ar)
        
        # elems = []
        # sar = ar.spawn('phones.ContactDetailsByPartner',
        #                master_instance=self)
        
        # items = [o.detail_type.as_html(o, sar) for o in sar]
        # if len(items) > 0:
        #     elems += join_elems(items, sep=', ')
        
        # btn = sar.as_button(_("Manage contact details"))
        # # elems.append(E.p(btn, align="right"))
        # elems.append(E.p(btn))
        # return elems

