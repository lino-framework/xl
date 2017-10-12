# Copyright 2013-2017 Luc Saffre
#
# License: BSD (see file COPYING for details)


"""
Adds a multipurpose model "Note"

.. autosummary::
   :toctree:

   choicelists
   models
   fixtures.demo
   fixtures.std

"""

from lino import ad
from django.utils.translation import ugettext_lazy as _


class Plugin(ad.Plugin):

    "See :class:`lino.core.Plugin`."

    verbose_name = _("Notes")

    # needs_plugins = ['lino.modlib.notify']
    needs_plugins = ['lino.modlib.gfks']

    def post_site_startup(self, site):
        super(Plugin, self).post_site_startup(site)
        site.kernel.memo_parser.register_django_model(
            'note', site.models.notes.Note,
            title=lambda obj: obj.subject)
    
    def setup_main_menu(config, site, user_type, m):
        mg = site.plugins.office
        m = m.add_menu(mg.app_label, mg.verbose_name)
        m.add_action('notes.MyNotes')

    def setup_config_menu(config, site, user_type, m):
        mg = site.plugins.office
        m = m.add_menu(mg.app_label, mg.verbose_name)
        m.add_action('notes.NoteTypes')
        m.add_action('notes.EventTypes')

    def setup_explorer_menu(config, site, user_type, m):
        mg = site.plugins.office
        m = m.add_menu(mg.app_label, mg.verbose_name)
        m.add_action('notes.AllNotes')

