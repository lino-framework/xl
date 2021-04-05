# Copyright 2008-2015-2019 Rumma & Ko Ltd
# License: GNU Affero General Public License v3 (see file COPYING for details)

"""
Adds functionality for managing properties.

See :doc:`/specs/properties`.

.. autosummary::
   :toctree:

    fixtures.std
    fixtures.demo

"""

from builtins import str
from lino import ad, _


class Plugin(ad.Plugin):
    "See :class:`lino.core.Plugin`."

    verbose_name = _("Properties")

    def setup_explorer_menu(self, site, user_type, m):
        m = m.add_menu(self.app_label, self.verbose_name)
        m.add_action('properties.Properties')

    def setup_config_menu(self, site, user_type, m):
        m = m.add_menu(self.app_label, self.verbose_name)
        m.add_action('properties.PropGroups')
        m.add_action('properties.PropTypes')
        PropGroup = site.modules.properties.PropGroup
        PropsByGroup = site.modules.properties.PropsByGroup
        for pg in PropGroup.objects.all():
            m.add_action(
                PropsByGroup,
                params=dict(master_instance=pg),
                #~ label=pg.name)
                label=str(pg))
