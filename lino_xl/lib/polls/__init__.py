# Copyright 2013-2017 Rumma & Ko Ltd
# License: GNU Affero General Public License v3 (see file COPYING for details)

"""Provides database models and functionality for managing polls.

See also :doc:`/specs/polly` and :doc:`/specs/polls`.

.. autosummary::
   :toctree:

    fixtures.bible
    fixtures.feedback
    fixtures.compass

"""

from lino.api import ad, _


class Plugin(ad.Plugin):
    # See :doc:`/dev/plugins`

    verbose_name = _("Polls")
    needs_plugins = ['lino_xl.lib.xl']

    def setup_main_menu(self, site, user_type, m):
        m = m.add_menu(self.app_label, self.verbose_name)
        m.add_action('polls.MyPolls')
        m.add_action('polls.MyResponses')

    def setup_config_menu(self, site, user_type, m):
        m = m.add_menu(self.app_label, self.verbose_name)
        m.add_action('polls.ChoiceSets')

    def setup_explorer_menu(self, site, user_type, m):
        m = m.add_menu(self.app_label, self.verbose_name)
        m.add_action('polls.AllPolls')
        m.add_action('polls.Questions')
        m.add_action('polls.Choices')
        m.add_action('polls.AllResponses')
        m.add_action('polls.AnswerChoices')
        m.add_action('polls.AllAnswerRemarks')
        #~ m.add_action('polls.Answers')
