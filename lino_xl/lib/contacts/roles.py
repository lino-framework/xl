# Copyright 2015-2017 Rumma & Ko Ltd
# License: BSD (see file COPYING for details)

from lino.core.roles import UserRole


class SimpleContactsUser(UserRole):
    """Has limited access to contact data."""
    
class ContactsUser(SimpleContactsUser):
    """Has full access to contact data."""



class ContactsStaff(ContactsUser):
    """Has configure contacts functionality."""


