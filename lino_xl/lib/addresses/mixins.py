# Copyright 2014-2020 Rumma & Ko Ltd
# License: GNU Affero General Public License v3 (see file COPYING for details)

from django.utils.translation import gettext_lazy as _

from lino.api import rt, dd
from etgen.html import E
from lino.core.diff import ChangeWatcher
from lino_xl.lib.countries.mixins import AddressLocation


class AddressOwner(AddressLocation):
    class Meta:
        abstract = True

    if dd.is_installed('addresses'):

        # def disabled_fields(self, ar):
        #     df = super(AddressOwner, self).disabled_fields(ar)
        #     return df | self.ADDRESS_FIELDS

        def get_address_by_type(self, address_type):
            Address = rt.models.addresses.Address
            try:
                return Address.objects.get(
                    partner=self, address_type=address_type)
            except Address.DoesNotExist:
                return self.get_primary_address()
            except Address.MultipleObjectsReturned:
                return self.get_primary_address()

        def get_primary_address(self):
            if not isinstance(self, dd.plugins.addresses.partner_model):
                return super(AddressOwner,self).get_primary_address()

            Address = rt.models.addresses.Address
            try:
                return Address.objects.get(partner=self, primary=True)
            except Address.DoesNotExist:
                p = self.get_address_parent()
                while p:
                    addr = p.get_primary_address()
                    if addr:
                        return addr
                    p = p.get_address_parent()
            except Address.MultipleObjectsReturned:
                return

        # def before_ui_save(self, ar, cw):
        #     self.sync_to_addresses(ar)
        #     # self.sync_from_address(self.get_primary_address())
        #     super(AddressOwner, self).before_ui_save(ar, cw)

        def after_ui_save(self, ar, cw):
            self.sync_to_addresses(ar)
            # self.sync_from_address(self.get_primary_address())
            super(AddressOwner, self).after_ui_save(ar, cw)

        def sync_primary_address(self, request):
            watcher = ChangeWatcher(self)
            self.sync_from_address(self.get_primary_address())
            self.save()
            watcher.send_update(request)

        def sync_to_addresses(self, ar):
            Address = rt.models.addresses.Address
            pa = self.get_primary_address()
            if pa is None:
                values = {}
                for k in Address.ADDRESS_FIELDS:
                    fld = self._meta.get_field(k)
                    v = getattr(self, k)
                    if v != fld.get_default():
                        values[k] = v
                if len(values):
                    # print(20200812, values)
                    addr = Address(partner=self, primary=True, **values)
                    addr.full_clean()
                    addr.save()
                else:
                    for o in self.addresses_by_partner.filter(primary=True):
                        o.primary = False
                        o.save()

            elif pa != self:
                pa.sync_from_address(self)
                pa.full_clean()
                pa.save()

        def get_overview_elems(self, ar):
            # elems = super(AddressOwner, self).get_overview_elems(ar)
            elems = []
            # e.g. in amici a company inherits from AddressOwner but
            # is not a partner_model because there we want multiple
            # addresses only for persons, not for companies.
            if isinstance(self, dd.plugins.addresses.partner_model):
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

    def get_address_parent(self):
        pass
