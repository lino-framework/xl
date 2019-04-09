# Copyright 2008-2019 Rumma & Ko Ltd
"""Belgian VAT declarations.  See :doc:`/specs/bevat`.

"""

from lino import ad


class Plugin(ad.Plugin):
    "This is a subclass of :class:`lino.core.plugin.Plugin`."

    needs_plugins = ['lino_xl.lib.vat']

    def setup_explorer_menu(self, site, user_type, m):
        m = m.add_menu("vat", site.plugins.vat.verbose_name)
        m.add_action('bevat.Declarations')
        m.add_action('bevat.DeclarationFields')


