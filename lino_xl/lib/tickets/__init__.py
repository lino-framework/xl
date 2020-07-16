# Copyright 2008-2019 Rumma & Ko Ltd
# License: BSD (see file COPYING for details)
"""
Adds functionality for managing tickets.

See :doc:`/specs/noi/tickets`.

.. autosummary::
   :toctree:

    roles


"""

from lino.api import ad, _


class Plugin(ad.Plugin):
    """The descriptor for this plugin."""
    verbose_name = _("Tickets")
    # verbose_name = _("Projects")

    needs_plugins = [
        # 'lino_xl.lib.stars',
        'lino_xl.lib.excerpts',
        # 'lino_xl.lib.deploy',
        # 'lino.modlib.changes',
        'lino.modlib.comments']

    site_model = 'tickets.Site'
    """
    The model to be used for representing "sites".
    """

    milestone_model = 'meetings.Meeting'
    """
    The model to be used for representing "milestones".
    """

    end_user_model = 'contacts.Partner'
    """
    The model to be used for representing "end users".
    """

    def on_site_startup(self, site):
        self.site_model = site.models.resolve(self.site_model)
        self.milestone_model = site.models.resolve(self.milestone_model)
        self.end_user_model = site.models.resolve(self.end_user_model)
        super(Plugin, self).on_site_startup(site)

    def setup_main_menu(self, site, user_type, m):
        p = self.get_menu_group()
        m = m.add_menu(p.app_label, p.verbose_name)
        # m.add_action('tickets.MyCompetences')
        # m.add_action('tickets.PublicTickets')
        m.add_action('tickets.MyTickets')
        # m.add_action('tickets.MyTicketsToWork') #In noi
        if site.is_installed('skills'):
            m.add_action('skills.SuggestedTicketsByEndUser')
        # m.add_action('tickets.TicketsToDo')
        # m.add_action('tickets.MyOwnedTickets')
        m.add_action('tickets.ActiveTickets')
        m.add_action('tickets.AllTickets')
        # m.add_action('tickets.MyKnownProblems')
        m.add_action('tickets.UnassignedTickets')
        # m.add_action('tickets.ActiveProjects')
        # m.add_action('tickets.MyWishes')
        m.add_action('tickets.RefTickets')
        m.add_action('tickets.MySites')



    def setup_config_menu(self, site, user_type, m):
        p = self.get_menu_group()
        m = m.add_menu(p.app_label, p.verbose_name)
        # m.add_action('tickets.AllProjects')
        # m.add_action('tickets.TopLevelProjects')
        # m.add_action('tickets.ProjectTypes')
        m.add_action('tickets.TicketTypes')
        m.add_action('tickets.AllSites')

    def setup_explorer_menu(self, site, user_type, m):
        p = self.get_menu_group()
        m = m.add_menu(p.app_label, p.verbose_name)
        # m.add_action('tickets.Projects')
        m.add_action('tickets.Links')
        m.add_action('tickets.TicketStates')
        #m.add_action('tickets.Subscriptions')
        # m.add_action('tickets.AllCompetences')
        # m.add_action('tickets.AllWishes')

    def get_dashboard_items(self, user):
        if user.is_authenticated:
            yield self.site.models.tickets.MyTickets
            yield self.site.models.tickets.MySites
            # yield self.site.models.tickets.MyTicketsToWork #in noi
            yield self.site.models.tickets.TicketsToTriage
        else:
            yield self.site.models.tickets.PublicTickets
