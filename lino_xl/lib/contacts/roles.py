# Copyright 2015-2016 Luc Saffre
# License: BSD (see file COPYING for details)
"""User roles for `lino_xl.lib.contacts`. """

from lino.core.roles import SiteUser


class SimpleContactsUser(SiteUser):
    """A user who has access to basic contacts functionality.

    """
    
class ContactsUser(SimpleContactsUser):
    """A user who has access to full contacts functionality.

    """


class ContactsStaff(ContactsUser):
    """A user who can configure contacts functionality.

    """

