# Copyright 2017-2020 Rumma & Ko Ltd
# License: GNU Affero General Public License v3 (see file COPYING for details)

"""
Adds the concept of trends.

See :doc:`/specs/trends`.

"""

from lino import ad

from django.utils.translation import gettext_lazy as _


class Plugin(ad.Plugin):
    "See :class:`lino.core.plugins.Plugin`."
    verbose_name = _("Trends")

    subject_model = None
    """The Django model used to represent the "subject" being observed.

    For example in :ref:`avanti` this points to a client.

    """

    def on_site_startup(self, site):
        self.subject_model = site.models.resolve(self.subject_model)
        super(Plugin, self).on_site_startup(site)

    def setup_config_menu(self, site, user_type, m):
        mg = self.get_menu_group()
        m = m.add_menu(mg.app_label, mg.verbose_name)
        m.add_action('trends.TrendAreas')
        m.add_action('trends.TrendStages')

    def setup_explorer_menu(self, site, user_type, m):
        mg = self.get_menu_group()
        m = m.add_menu(mg.app_label, mg.verbose_name)
        m.add_action('trends.AllTrendEvents')
