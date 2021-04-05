# Copyright 2017-2019 Rumma & Ko Ltd
# License: GNU Affero General Public License v3 (see file COPYING for details)


from etgen.html import E, join_elems

from lino.api import rt, dd, _
from lino.core.diff import ChangeWatcher
from lino.mixins import Contactable, Phonable
from .choicelists import ContactDetailTypes

class ContactDetailsOwner(Contactable, Phonable):

    class Meta:
        abstract = True

    if dd.is_installed('phones'):

        def after_ui_save(self, ar, cw):
            if cw is None:  # it's a new instance
                for cdt in ContactDetailTypes.get_list_items():
                    self.propagate_contact_detail(cdt)
                pass
            else:
                for k, old, new in cw.get_updates():
                    cdt = ContactDetailTypes.find(field_name=k)
                    # cdt = getattr(ContactDetailTypes, k, False)
                    if cdt:
                        self.propagate_contact_detail(cdt)
            super(ContactDetailsOwner, self).after_ui_save(ar, cw)

        def propagate_contact_detail(self, cdt):
            k = cdt.field_name
            if k:
                value = getattr(self, k)
                ContactDetail = rt.models.phones.ContactDetail
                kw = dict(partner=self, primary=True, detail_type=cdt)
                try:
                    cd = ContactDetail.objects.get(**kw)
                    if value:
                        cd.value = value
                        # don't full_clean() because no need to check
                        # primary of other items
                        cd.save()
                    else:
                        cd.delete()
                except ContactDetail.DoesNotExist:
                    if value:
                        kw.update(value=value)
                        cd = ContactDetail(**kw)
                        # self.phones_by_partner.add(cd, bulk=False)
                        cd.save()

        def propagate_contact_details(self, ar=None):
            watcher = ChangeWatcher(self)
            for cdt in ContactDetailTypes.get_list_items():
                self.propagate_contact_detail(cdt)
            if ar is not None:
                watcher.send_update(ar)

        def get_overview_elems(self, ar):
            # elems = super(ContactDetailsOwner, self).get_overview_elems(ar)
            yield rt.models.phones.ContactDetailsByPartner.get_table_summary(
                self, ar)

        @dd.displayfield(_("Contact details"))
        def contact_details(self, ar):
            if ar is None:
                return ''
            sar = rt.models.phones.ContactDetailsByPartner.request(parent=ar, master_instance=self)
            items = [o.detail_type.as_html(o, sar)
                     for o in sar if not o.end_date]
            return E.p(*join_elems(items, sep=', '))



    else:

        def get_overview_elems(self, ar):
            return []

        @dd.displayfield(_("Contact details"))
        def contact_details(self, ar):
            # if ar is None:
            #     return ''
            items = []
            for cdt in ContactDetailTypes.get_list_items():
                if cdt.field_name:
                    value = getattr(self, cdt.field_name)
                if value:
                    items.append(cdt.format(value))
            # items.append(ContactDetailTypes.email.format(self.email))
            # # items.append(E.a(self.email, href="mailto:" + self.email))
            # items.append(self.phone)
            # items.append(E.a(self.url, href=self.url))
            return E.p(*join_elems(items, sep=', '))
