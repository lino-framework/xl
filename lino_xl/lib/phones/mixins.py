# Copyright 2017 Luc Saffre
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

        def phone_changed(self, ar):
            self.propagate_contact_detail(
                rt.models.phones.ContactDetailTypes.phone)
            
        def gsm_changed(self, ar):
            self.propagate_contact_detail(
                rt.models.phones.ContactDetailTypes.mobile)
            
        def url_changed(self, ar):
            self.propagate_contact_detail(
                rt.models.phones.ContactDetailTypes.url)
            
        def fax_changed(self, ar):
            self.propagate_contact_detail(
                rt.models.phones.ContactDetailTypes.fax)
            
        def email_changed(self, ar):
            self.propagate_contact_detail(
                rt.models.phones.ContactDetailTypes.email)
            
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
                        cd.save()

        def propagate_contact_details(self, ar=None):
            watcher = ChangeWatcher(self)
            ContactDetailTypes = rt.models.phones.ContactDetailTypes
            for cdt in ContactDetailTypes.get_list_items():
                self.propagate_contact_detail(cdt)
            if ar is not None:
                watcher.send_update(ar)
                
        def get_overview_elems(self, ar):
            # elems = super(ContactDetailsOwner, self).get_overview_elems(ar)
            yield rt.models.phones.ContactDetailsByPartner.get_slave_summary(
                self, ar)

    else:

        def get_overview_elems(self, ar):
            return []
        
