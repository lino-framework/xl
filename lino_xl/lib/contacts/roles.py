# Copyright 2015-2017 Luc Saffre
# License: BSD (see file COPYING for details)

from lino.core.roles import SiteUser


class SimpleContactsUser(SiteUser):
    pass
    
class ContactsUser(SimpleContactsUser):
    pass


class ContactsStaff(ContactsUser):
    pass

