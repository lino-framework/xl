# Copyright 2014-2017 Luc Saffre
#
# License: BSD (see file COPYING for details)

"""
Model mixins for `lino_xl.lib.addresses`.

"""

from __future__ import unicode_literals
from __future__ import print_function

from django.utils.translation import ugettext_lazy as _

from lino.api import rt, dd
from lino.utils.xmlgen.html import E
from lino.core.diff import ChangeWatcher


class AddressOwner(dd.Model):
    """Base class for the "addressee" of any address.

    """
    class Meta:
        abstract = True

    if dd.is_installed('addresses'):

        def get_address_by_type(self, address_type):
            Address = rt.modules.addresses.Address
            try:
                return Address.objects.get(
                    partner=self, address_type=address_type)
            except Address.DoesNotExist:
                return self.get_primary_address()
            except Address.MultipleObjectsReturned:
                return self.get_primary_address()

        def get_primary_address(self):
            """Return the primary address of this partner.

            """
            Address = rt.modules.addresses.Address
            try:
                return Address.objects.get(partner=self, primary=True)
            except Address.DoesNotExist:
                pass

        def sync_primary_address(self, ar):
            watcher = ChangeWatcher(self)
            self.sync_primary_address_()
            watcher.send_update(ar)

        def sync_primary_address_(self):
            Address = rt.modules.addresses.Address
            kw = dict(partner=self, primary=True)
            try:
                pa = Address.objects.get(**kw)
                for k in Address.ADDRESS_FIELDS:
                    setattr(self, k, getattr(pa, k))
            except Address.DoesNotExist:
                pa = None
                for k in Address.ADDRESS_FIELDS:
                    fld = self._meta.get_field(k)
                    setattr(self, k, fld.get_default())
            self.save()

        def get_overview_elems(self, ar):
            # elems = super(AddressOwner, self).get_overview_elems(ar)
            elems = []
            sar = ar.spawn('addresses.AddressesByPartner',
                           master_instance=self)
            # btn = sar.as_button(_("Manage addresses"), icon_name="wrench")
            btn = sar.as_button(_("Manage addresses"))
            # elems.append(E.p(btn, align="right"))
            elems.append(E.p(btn))
            return elems
    else:

        def get_overview_elems(self, ar):
            return []
