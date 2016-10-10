# Copyright 2016 Luc Saffre
#
# License: BSD (see file COPYING for details)

"""Defines a default set of user roles for Lino XL applications.

See also :attr:`lino.core.site.Site.user_profiles_module`.

"""

from lino.core.roles import UserRole, SiteAdmin
from lino.modlib.office.roles import OfficeStaff, OfficeUser


class SiteUser(OfficeUser):
    pass


class SiteAdmin(SiteAdmin, OfficeStaff):
    pass


from django.utils.translation import ugettext_lazy as _
from lino.modlib.users.choicelists import UserProfiles
UserProfiles.clear()
add = UserProfiles.add_item
add('000', _("Anonymous"), UserRole, name='anonymous', readonly=True)
add('100', _("User"), SiteUser, name='user')
add('900', _("Administrator"), SiteAdmin, name='admin')
