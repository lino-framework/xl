# Copyright 2013-2015 Luc Saffre
#
# This file is part of Lino XL.
#
# Lino XL is free software: you can redistribute it and/or modify it
# under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.
#
# Lino XL is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public
# License along with Lino XL.  If not, see
# <http://www.gnu.org/licenses/>.

"""Adds functionality for sending emails from within a Lino application.

.. autosummary::
   :toctree:

   models
   mixins
   choicelists
   fixtures.hello


"""

from lino import ad
from django.utils.translation import ugettext_lazy as _


class Plugin(ad.Plugin):

    verbose_name = _("Outbox")

    needs_plugins = ['lino.modlib.uploads']

    MODULE_LABEL = _("Outbox")

    def setup_main_menu(config, site, profile, m):
        mg = site.plugins.office
        m = m.add_menu(mg.app_label, mg.verbose_name)
        m.add_action('outbox.MyOutbox')

    def setup_explorer_menu(config, site, profile, m):
        mg = site.plugins.office
        m = m.add_menu(mg.app_label, mg.verbose_name)
        m.add_action('outbox.Mails')
        m.add_action('outbox.Attachments')
