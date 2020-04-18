# -*- coding: UTF-8 -*-
# Copyright 2016-2017 Rumma & Ko Ltd
# License: BSD (see file COPYING for details)


from django.db import models
from django.utils import timezone

from lino.api import dd, rt, _

from lino.mixins.periods import Monthly
from lino.modlib.printing.mixins import DirectPrintAction
from lino.core.roles import SiteUser
from .roles import Worker
from lino_xl.lib.tickets.roles import Triager

class WorkerAction(dd.Action):
    show_in_workflow = True
    show_in_bbar = False
    readonly = False
    required_roles = dd.login_required(Worker)

    # def get_workables(self, ar):
    #     return ar.selected_rows

class EndSession(WorkerAction):
    label = u"■"  # BLACK SQUARE (U+25A0)
    # label = u"◉"  # FISHEYE (U+25C9)
    # label = u"↘"  # u"\u2198"
    # label = _("End session")
    # label = u"\u231a\u2198"
    # todo: Move to Noi somehow...
    # parameters = dict(
    #     summary= models.CharField(
    #     _("Summary"), max_length=200, blank=True,
    #     help_text=_("Summary of the session.")),
    # )

    def get_sessions(self, ar):
        return ar.selected_rows

    def end_session(self, ar, obj, now=None):
        if now is None:
            now = timezone.now()
        obj.set_datetime('end', now)
        if ar.action_param_values and ar.action_param_values.summary:
                obj.summary = ar.action_param_values.summary
        obj.full_clean()
        obj.save()

    def run_from_ui(self, ar, **kw):

        def ok(ar2):
            now = timezone.now()
            for obj in self.get_sessions(ar):
                self.end_session(ar, obj, now)
            ar2.set_response(refresh=True)

        if True:
            ok(ar)
        else:
            msg = _("Close {0} sessions.").format(len(ar.selected_rows))
            ar.confirm(ok, msg, _("Are you sure?"))

class EndThisSession(EndSession):

    def get_action_permission(self, ar, obj, state):
        if obj.end_time:
            return False
        return super(EndThisSession, self).get_action_permission(ar, obj, state)

class EndTicketSession(EndSession):
    def get_sessions(self, ar):
        Session = rt.models.working.Session
        for obj in ar.selected_rows:
            ses = Session.objects.get(
                user=ar.get_user(), ticket=obj.get_ticket(),
                end_time__isnull=True)
            yield ses

    # def get_action_permission(self, ar, obj, state):
    #     # u = ar.get_user()
    #     # if not u.user_type.has_required_roles([SiteUser]):
    #     #     # avoid query with AnonymousUser
    #     #     return False
    #     if not super(EndTicketSession, self).get_action_permission(
    #             ar, obj, state):
    #         return False
    #     user = ar.get_user()

    #     Session = rt.models.working.Session
    #     qs = Session.objects.filter(
    #         user=user, ticket=obj.get_ticket(), end_time__isnull=True)
    #     if qs.count() == 0:
    #         return False
    #     return True

class StartTicketSession(WorkerAction):
    # label = _("Start session")
    # label = u"\u262d"
    # label = u"\u2692"
    # label = u"\u2690"
    # label = u"\u2328"
    # label = u"\u231a\u2197"
    # label = u"↗"  # \u2197
    label = u"▶"  # BLACK RIGHT-POINTING TRIANGLE (U+25B6)
    # icon_name = 'emoticon_smile'
    # show_in_workflow = True
    # show_in_bbar = False
    readonly = True
    # required_roles = dd.login_required(Worker)

    # def get_action_permission(self, ar, obj, state):
    #     user = ar.get_user()
    #     if not obj.is_workable_for(user):
    #         return False
    #     if not super(StartTicketSession, self).get_action_permission(
    #             ar, obj, state):
    #         return False
    #     Session = rt.models.working.Session
    #     qs = Session.objects.filter(
    #         user=user, ticket=obj.get_ticket(), end_time__isnull=True)
    #     if qs.count():
    #         return False
    #     return True

    def run_from_ui(self, ar, **kw):
        me = ar.get_user()
        for obj in ar.selected_rows:
            ses = rt.models.working.Session(
                ticket=obj.get_ticket(), user=me)
            ses.full_clean()
            ses.save()
        ar.set_response(refresh=True)


# if dd.is_installed('working'):  # Sphinx autodoc
#     dd.inject_action(
#         dd.plugins.working.ticket_model,
#         start_session=StartTicketSession())
#     dd.inject_action(
#         dd.plugins.working.ticket_model,
#         end_session=EndTicketSession())


class PrintActivityReport(DirectPrintAction):
    """Print an activity report.

    Not yet used. This is meant to be used as a list action on
    Session, but Lino does not yet support list actions with a
    parameter window.

    """
    select_rows = False
    # combo_group = "creacert"
    label = _("Activity report")
    tplname = "activity_report"
    build_method = "weasy2html"
    icon_name = None
    parameters = Monthly(
        show_remarks=models.BooleanField(
            _("Show remarks"), default=False),
        show_states=models.BooleanField(
            _("Show states"), default=True))
    params_layout = """
    start_date
    end_date
    show_remarks
    show_states
    """
    # keep_user_values = True
    # default_format = 'json'
    # http_method = 'POST'

class ShowMySessionsByDay(dd.Action):
    label = _("Day's work")
    show_in_bbar = True
    sort_index = 60
    icon_name = 'calendar'

    def __init__(self, date_field, **kw):
        self.date_field = date_field
        super(ShowMySessionsByDay, self).__init__(**kw)

    def run_from_ui(self, ar, **kw):
        obj = ar.selected_rows[0]
        today = getattr(obj, self.date_field)
        pv = dict(start_date=today)
        pv.update(end_date=today)
        sar = ar.spawn(rt.models.working.MySessionsByDate, param_values=pv)
        js = ar.renderer.request_handler(sar)
        ar.set_response(eval_js=js)
