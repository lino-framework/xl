# Copyright 2013-2019 Rumma & Ko Ltd
# License: BSD (see file COPYING for details)

"""
Provides a framework for configuring and generating printable
documents called "database excerpts".

See also :doc:`/specs/excerpts`.

.. autosummary::
   :toctree:

   roles
   doctools
   fixtures.std
   fixtures.demo2
"""

from lino import ad, _


class Plugin(ad.Plugin):
    "See :class:`lino.core.Plugin`."

    verbose_name = _("Excerpts")

    needs_plugins = [
        'lino.modlib.gfks', 'lino.modlib.printing',
        'lino.modlib.office', 'lino_xl.lib.xl']

    # _default_template_handlers = {}

    responsible_user = None
    """
    The username of the user responsible for monitoring the excerpts
    system.  This is currently used only by
    :mod:`lino_xl.lib.excerpts.fixtures.demo2`.
    """

    def setup_main_menu(self, site, user_type, m):
        mg = site.plugins.office
        m = m.add_menu(mg.app_label, mg.verbose_name)
        m.add_action('excerpts.MyExcerpts')

    def setup_config_menu(self, site, user_type, m):
        mg = site.plugins.office
        m = m.add_menu(mg.app_label, mg.verbose_name)
        m.add_action('excerpts.ExcerptTypes')

    def setup_explorer_menu(self, site, user_type, m):
        mg = site.plugins.office
        m = m.add_menu(mg.app_label, mg.verbose_name)
        m.add_action('excerpts.AllExcerpts')
