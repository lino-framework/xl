# Copyright 2013-2020 Rumma & Ko Ltd
# License: GNU Affero General Public License v3 (see file COPYING for details)

"""This is Lino's calendar module. See :doc:`/specs/cal`.

.. autosummary::
   :toctree:

    utils

"""

from lino.api import ad, _
from dateutil.relativedelta import relativedelta


class Plugin(ad.Plugin):
    verbose_name = _("Calendar")

    needs_plugins = ['lino.modlib.gfks', 'lino.modlib.printing',
                     # 'lino.modlib.notify',
                     'lino_xl.lib.xl', 'lino.modlib.checkdata']

    # partner_model = 'contacts.Partner'
    partner_model = 'contacts.Person'  # TODO: rename to "guest_model"
    """
    The model to use as the guest of a presence.
    """

    ignore_dates_before = None
    """
    Ignore dates before the given date.

    Default value is `None`, meaning "no limit".

    Unlike :attr:`hide_events_before
    <lino.modlib.system.SiteConfig.hide_events_before>`
    this is not editable through the web interface.
    """

    ignore_dates_after = None
    """
    Ignore dates after the given date.  This should never be `None`.
    Default value is 5 years after :meth:`today
    <lino.core.site.Site.today>`.
    """

    beginning_of_time = None

    demo_absences = True
    """Whether to generate absences in demo calendar."""

    default_guest_state = 'invited'
    """Default value for the Guest.state field."""

    mytasks_start_date = None
    """Offset (in days from today) to compute the default value
    for :attr:`MyTasks.start_date`.  `None` means no start date.

    """

    mytasks_end_date = 30
    """Offset (in days from today) to compute the default value
    for :attr:`MyTasks.end_date`.  `None` means no end date."""


    def on_init(self):
        tod = self.site.today()
        # self.ignore_dates_after = tod.replace(year=tod.year+5, day=28)
        # above code should not fail on February 29 of a leap year.
        self.ignore_dates_after = tod + relativedelta(years=5)
        self.beginning_of_time = tod + relativedelta(years=-5)

    def on_site_startup(self, site):
        self.partner_model = site.models.resolve(self.partner_model)
        super(Plugin, self).on_site_startup(site)
    #     from lino_xl.lib.cal.mixins import Reservation
    #     from lino.core.utils import models_by_base
    #     for m in models_by_base(Reservation):
    #         state_field = m.get_field()

    def setup_main_menu(self, site, user_type, m):
        m = m.add_menu(self.app_label, self.verbose_name)

        m.add_action('cal.MyEntries')  # string spec to allow overriding
        m.add_action('cal.OverdueAppointments')
        m.add_action('cal.MyUnconfirmedAppointments')

        # m.add_separator('-')
        # m  = m.add_menu("tasks",_("Tasks"))
        m.add_action('cal.MyTasks')
        # m.add_action(MyTasksToDo)
        m.add_action('cal.MyGuests')
        m.add_action('cal.MyPresences')
        m.add_action('cal.MyOverdueAppointments')
        # m.add_action('cal.DailyPlanner')

    def setup_config_menu(self, site, user_type, m):
        m = m.add_menu(self.app_label, self.verbose_name)
        m.add_action('cal.Calendars')
        # m.add_action('cal.MySubscriptions')
        m.add_action('cal.AllRooms')
        # m.add_action('cal.Priorities')
        m.add_action('cal.RecurrentEvents')
        # m.add_action(AccessClasses)
        # m.add_action(EventStatuses)
        # m.add_action(TaskStatuses)
        # m.add_action(EventTypes)
        m.add_action('cal.GuestRoles')
        # m.add_action(GuestStatuses)
        m.add_action('cal.EventTypes')
        m.add_action('cal.EventPolicies')
        m.add_action('cal.RemoteCalendars')

    def setup_explorer_menu(self, site, user_type, m):
        m = m.add_menu(self.app_label, self.verbose_name)
        # m.add_action('cal.Days')
        m.add_action('cal.AllEntries')
        m.add_action('cal.Tasks')
        m.add_action('cal.AllGuests')
        m.add_action('cal.Subscriptions')
        # m.add_action(Memberships)
        m.add_action('cal.EntryStates')
        m.add_action('cal.GuestStates')
        m.add_action('cal.TaskStates')
        m.add_action('cal.PlannerColumns')
        m.add_action('cal.AccessClasses')
        m.add_action('cal.DisplayColors')
        # m.add_action(RecurrenceSets)

    def get_dashboard_items(self, user):
        from lino.core.dashboard import ActorItem

        if user.is_authenticated:
            # yield self.site.models.cal.LastWeek
            # yield self.site.models.cal.ComingWeek
            yield self.site.models.cal.MyTasks
            yield ActorItem(
                self.site.models.cal.MyEntries, min_count=None)
            yield self.site.models.cal.MyOverdueAppointments
            yield self.site.models.cal.MyUnconfirmedAppointments
            yield self.site.models.cal.MyPresences
        else:
            yield self.site.models.cal.PublicEntries

    def get_requirements(self, site):
        yield "num2words"
