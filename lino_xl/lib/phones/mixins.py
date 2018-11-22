# Copyright 2017 Rumma & Ko Ltd
#
# License: BSD (see file COPYING for details)


from __future__ import unicode_literals
from __future__ import print_function

from lino.api import rt, dd
from lino.core.diff import ChangeWatcher
from lino.mixins import Contactable, Phonable

class ContactDetailsOwner(Contactable, Phonable):
    
    class Meta:
        abstract = True

    if dd.is_installed('phones'):

        def after_ui_save(self, ar, cw):
            ContactDetailTypes = rt.models.phones.ContactDetailTypes
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
            ContactDetailTypes = rt.models.phones.ContactDetailTypes
            watcher = ChangeWatcher(self)
            for cdt in ContactDetailTypes.get_list_items():
                self.propagate_contact_detail(cdt)
            if ar is not None:
                watcher.send_update(ar)
                
        def get_overview_elems(self, ar):
            # elems = super(ContactDetailsOwner, self).get_overview_elems(ar)
            yield rt.models.phones.ContactDetailsByPartner.get_table_summary(
                self, ar)

    else:

        def get_overview_elems(self, ar):
            return []
        
