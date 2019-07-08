# Copyright 2013-2018 Rumma & Ko Ltd
# License: BSD (see file COPYING for details)


"""
Adds a multipurpose concept of "Note". See :doc:`/specs/notes`.

.. autosummary::
   :toctree:

   fixtures.demo
   fixtures.std

"""

from lino import ad
from django.utils.translation import ugettext_lazy as _


class Plugin(ad.Plugin):

    "See :class:`lino.core.Plugin`."

    verbose_name = _("Notes")

    # needs_plugins = ['lino.modlib.notify']
    needs_plugins = ['lino.modlib.memo']
    menu_group = 'office'

    def post_site_startup(self, site):
        super(Plugin, self).post_site_startup(site)

        if site.is_installed('memo'):
            site.plugins.memo.parser.register_django_model(
                'note', site.models.notes.Note,
                title=lambda obj: obj.subject)
    
    def setup_main_menu(self, site, user_type, m):
        mg = self.get_menu_group()
        m = m.add_menu(mg.app_label, mg.verbose_name)
        m.add_action('notes.MyNotes')

    def setup_config_menu(self, site, user_type, m):
        mg = self.get_menu_group()
        m = m.add_menu(mg.app_label, mg.verbose_name)
        m.add_action('notes.NoteTypes')
        m.add_action('notes.EventTypes')

    def setup_explorer_menu(self, site, user_type, m):
        mg = self.get_menu_group()
        # mg = site.plugins.office
        m = m.add_menu(mg.app_label, mg.verbose_name)
        m.add_action('notes.AllNotes')

