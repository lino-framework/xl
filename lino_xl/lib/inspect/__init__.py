# Copyright 2008-2018 Rumma & Ko Ltd
# License: GNU Affero General Public License v3 (see file COPYING for details)

"""
Site inspector.

"""

from lino.api import ad


class Plugin(ad.Plugin):

    def setup_site_menu(self, site, user_type, m):
        m.add_action(site.models.about.Models)
        m.add_action(site.models.about.Inspector)
        m.add_action(site.models.about.SourceFiles)
        # m.add_action(site.models.about.DetailLayouts)
        # m.add_action(site.models.about.WindowActions)
        # m.add_action(site.models.about.FormPanels)
