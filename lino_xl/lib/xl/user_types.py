# Copyright 2016-2020 Rumma & Ko Ltd
# License: BSD (see file COPYING for details)

"""
Defines a default set of user roles for Lino XL applications.

To be used as a :attr:`user_types_module
<lino.core.site.Site.user_types_module>`.
"""

from lino.core.roles import UserRole, SiteUser
from lino.modlib.office.roles import OfficeStaff, OfficeUser
from lino.modlib.comments.roles import CommentsUser, CommentsStaff
from lino_xl.lib.contacts.roles import ContactsUser, ContactsStaff
from lino_xl.lib.cal.roles import GuestOperator
from lino_xl.lib.notes.roles import NotesUser, NotesStaff
from lino_xl.lib.polls.roles import PollsUser, PollsAdmin
from lino_xl.lib.excerpts.roles import ExcerptsUser, ExcerptsStaff


class SiteUser(SiteUser, OfficeUser, GuestOperator, ContactsUser, PollsUser,
               ExcerptsUser, CommentsUser, NotesUser):
    pass


class SiteAdmin(PollsAdmin, GuestOperator, OfficeStaff, ContactsStaff,
                ExcerptsStaff, CommentsStaff, NotesStaff):
    pass


from django.utils.translation import ugettext_lazy as _
from lino.modlib.users.choicelists import UserTypes
UserTypes.clear()
add = UserTypes.add_item
add('000', _("Anonymous"), UserRole, name='anonymous', readonly=True)
add('100', _("User"), SiteUser, name='user')
add('900', _("Administrator"), SiteAdmin, name='admin')
