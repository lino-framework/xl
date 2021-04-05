# Copyright 2008-2015 Rumma & Ko Ltd
#
# License: GNU Affero General Public License v3 (see file COPYING for details)

"""
Not used. Adds functionality for managing families.

.. autosummary::
   :toctree:

    models

"""

from lino import ad, _


class Plugin(ad.Plugin):

    "See :class:`lino.core.Plugin`."

    verbose_name = _("Families")

    def setup_explorer_menu(config, site, user_type, m):
        mg = site.plugins.contacts
        m = m.add_menu(mg.app_label, mg.verbose_name)
        m.add_action('families.Couples')
