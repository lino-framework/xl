# Copyright 2015-2017 Rumma & Ko Ltd
# License: BSD (see file COPYING for details)

from lino.core.roles import UserRole


class SimpleContactsUser(UserRole):
    pass
    
class ContactsUser(SimpleContactsUser):
    pass


class ContactsStaff(ContactsUser):
    pass

