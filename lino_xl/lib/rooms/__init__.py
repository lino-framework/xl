# -*- coding: UTF-8 -*-
# Copyright 2013-2015 Rumma & Ko Ltd
#
# License: BSD (see file COPYING for details)

from lino import ad

from django.utils.translation import ugettext_lazy as _


class Plugin(ad.Plugin):
    "See :class:`lino.core.Plugin`."
    verbose_name = _("Rooms")

    def setup_main_menu(self, site, user_type, main):
        m = main.get_item("cal")
        m.add_action('rooms.Bookings')
