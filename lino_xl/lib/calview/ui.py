# -*- coding: UTF-8 -*-
# Copyright 2011-2020 Rumma & Ko Ltd
# License: BSD (see file COPYING for details)

import datetime
from collections import OrderedDict
from calendar import Calendar as PythonCalendar

from django.conf import settings
from django.db import models

from lino.api import dd, rt, _, gettext
from lino.mixins import ObservedDateRange
from lino.core.roles import Explorer
from lino.core.fields import TableRow
from lino.core.tables import VentilatedColumns, AbstractTable
from lino.core import fields
from lino.core.utils import dbfield2params_field
from lino.utils.format_date import monthname
from lino.utils.format_date import day_and_month, day_and_weekday
from lino.modlib.users.mixins import My
from lino.modlib.office.roles import OfficeUser, OfficeStaff, OfficeOperator

from lino.utils import join_elems, ONE_DAY, ONE_WEEK
from etgen.html import E, forcetext

from lino_xl.lib.cal.choicelists import PlannerColumns, Weekdays
from lino_xl.lib.cal.choicelists import DurationUnits, YearMonths
from lino_xl.lib.cal.utils import when_text

from .mixins import Plannable, Planner

CALENDAR = PythonCalendar()


def date2pk(date):
    delta = date - dd.today()
    return delta.days

def weekname(date):
    year, week, day = date.isocalendar()
    text = (date + datetime.timedelta(days=-day+1)).strftime("%d %B")
    return _("Week {1} / {0} ({2})").format(year, week, text)


class InsertEvent(dd.Action):
    """Wrapper to insert an event in the daily view cal table.
    Returns a js to eval which equates to running the insert window action for Events with the correct known values."""
    label = _("Create new Event")
    icon_name = 'add'  # if action rendered as toolbar button
    help_text = _("Create a new Event")
    show_in_bbar = True

    def run_from_ui(self, ar, **kw):
        Event = rt.models.cal.Event
        sar = Event.get_default_table().insert_action.request_from(ar)
        sar.known_values = dict(
            start_date=str(ar.selected_rows[0].date))
        ar.set_response(eval_js=ar.renderer.ar2js(sar, None))


class DailyPlannerRows(dd.Table):
    # used for configuring the planner rows
    model = 'calview.DailyPlannerRow'
    column_names = "seqno designation start_time end_time"
    required_roles = dd.login_required(OfficeStaff)

class ParameterClone(dd.Actor):
    abstract = True
    clone_from = 'cal.Events'
    # clone_from = None
    # """subclasses must set this"""

    @classmethod
    def class_init(cls):
        super(ParameterClone, cls).class_init()
        if isinstance(cls.clone_from, str):
            cls.clone_from = rt.models.resolve(cls.clone_from)

    @classmethod
    def init_layouts(cls):
        super(ParameterClone, cls).init_layouts()
        # cls.params_layout = rt.models.cal.Events.params_layout
        cls.params_layout = dd.plugins.calview.params_layout

    # @classmethod
    # def init_layouts(cls):
    #     super(ParameterClone, cls).init_layouts()
    #     if cls.abstract:
    #         return
    #     cls.params_layout = cls.clone_from.params_layout

    @classmethod
    def setup_parameters(cls, params):
        super(ParameterClone, cls).setup_parameters(params)
        if cls.abstract:
            return
        cls.clone_from.setup_parameters(params)

    @classmethod
    def get_data_elem(cls, name):
        # return cls.clone_from.get_data_elem(name)
        e = super(ParameterClone, cls).get_data_elem(name)
        if e is None:
            e = cls.clone_from.get_data_elem(name)
        return e

    @classmethod
    def get_simple_parameters(cls):
        for p in super(ParameterClone, cls).get_simple_parameters():
            yield p
        for p in cls.clone_from.get_simple_parameters():
            yield p

    @classmethod
    def param_defaults(cls, ar, **kwargs):
        kwargs = super(ParameterClone, cls).param_defaults(ar, **kwargs)
        return cls.clone_from.param_defaults(ar, **kwargs)

    # @classmethod
    # def get_calendar_entries(cls, ar, obj):
    #     qs = cls.clone_from.get_request_queryset(ar)
    #     if obj is not None:
    #         qs = obj.get_my_plannable_entries(qs, ar)
    #     # qs = Event.objects.all()
    #     # qs = Event.calendar_param_filter(qs, ar.param_values)
    #     # print("20200430", ar.master_instance, obj, qs.query)
    #     return qs


class EventsParameters(ParameterClone):
    """

    Mixin for actors that inherit parameters and params_layout from the
    cal.Events table as defined by the application.

    The takeover must happen *after* the custom_layout_module has been loaded.
    So we override the class_init() method.

    """
    abstract = True
    # clone_from = 'cal.Events'
    # clone_from = 'cal.EntriesByDay'

    # @classmethod
    # def setup_parameters(cls, params):
    #     super(EventsParameters, cls).setup_parameters(params)
    #     rt.models.cal.Events.setup_parameters(params)
    #
    # @classmethod
    # def get_simple_parameters(cls):
    #     for p in super(EventsParameters, cls).get_simple_parameters():
    #         yield p
    #     for p in rt.models.cal.Events.get_simple_parameters():
    #         yield p
    #
    # @classmethod
    # def param_defaults(self, ar, **kwargs):
    #     kwargs = super(EventsParameters, cls).param_defaults(ar, **kwargs)
    #     return rt.models.cal.Events.param_defaults(ar, **kwargs)
    #
    # @classmethod
    # def get_calendar_entries(cls, ar, obj):
    #     qs = rt.models.cal.Events.get_request_queryset(ar)
    #     if obj is not None:
    #         qs = obj.get_my_plannable_entries(qs, ar)
    #     # qs = Event.objects.all()
    #     # qs = Event.calendar_param_filter(qs, ar.param_values)
    #     # print("20200430", ar.master_instance, obj, qs.query)
    #     return qs
    #


# class TableWithHeaderRow(dd.Table):
#     """
#
#     Mixin for tables that insert a virtual header row where all-day events are
#     shown.  Used in daily and weekly view but not in monthly view.
#
#     """
#     abstract = True
#
#     @classmethod
#     def get_request_queryset(cls, ar):
#     # def get_data_rows(cls, ar):
#         yield cls.model.HEADER_ROW
#         for obj in super(TableWithHeaderRow, cls).get_request_queryset(ar):
#             yield obj


class Day(TableRow):

    navigation_mode = None
    planner = None

    def __init__(self, offset=0, ar=None, navigation_mode=None, planner=None):
        self.date = dd.today(offset)
        self.pk = offset
        self.ar = ar
        self.navigation_mode = navigation_mode
        if planner is not None:
            assert isinstance(planner, Planner)
            self.planner = planner

    def __str__(self):
        if self.navigation_mode == "day":
            return when_text(self.date)
        elif self.navigation_mode == "week":
            return weekname(self.date)
        elif self.navigation_mode == "month":
            return monthname(self.date.month) + " " + str(self.date.year)
        else:
            raise Exception(
                "Invalid navigation_mode {} ({})".format(
                    self.navigation_mode, self.ar))

    def skipmonth(self, n):
        return DurationUnits.months.add_duration(self.date, n)

    @classmethod
    def setup_parameters(cls, params):
        super(Day, cls).setup_parameters(params)
        Event = rt.models.cal.Event
        Event.setup_parameters(params)

        # simulate for get_simple_parameters
        # event_fields = ['user', 'event_type', 'room']
        # if settings.SITE.project_model:
        #     event_fields.append('project')
        # for k in event_fields:
        for k in ('user', 'event_type', 'room', 'project'):
            params[k] = dbfield2params_field(Event.get_data_elem(k))
            # params[k] = dbfield2params_field(Event._meta.get_field(k))



class DaysTable(dd.VirtualTable):
    abstract = True
    model = 'calview.Day'
    # navigation_mode = None  # "day" or "week" or "month"
    navigation_mode = "day"  # "day" or "week" or "month"

    @classmethod
    def get_planner(cls):
        pass

    @classmethod
    def get_row_by_pk(cls, ar, pk):
        """
        pk is the offset from today in days
        """
        return cls.model(int(pk), ar, cls.navigation_mode, cls.get_planner())

    # @classmethod
    # def get_request_queryset(cls, ar, **filter):
    @classmethod
    def get_data_rows(cls, ar):
        home = cls.get_row_by_pk(ar, 0)
        # ni = cls.get_navinfo(ar, home)

        pv = ar.param_values
        # date = pv.start_date or dd.today(ni['first'])
        # last = pv.end_date or dd.today(ni['last'])
        # start_date = dd.plugins.cal.beginning_of_time
        # end_date = dd.plugins.cal.ignore_dates_after

        if cls.navigation_mode == "day":
            step = lambda x: x + ONE_DAY
            delta = 7
        elif cls.navigation_mode == "week":
            step = lambda x: x + ONE_WEEK
            delta = 7*2
        elif cls.navigation_mode == "month":
            step = lambda x: DurationUnits.months.add_duration(x, 1)
            delta = 40
        else:
            step = lambda x: DurationUnits.years.add_duration(x, 1)
            delta = 40

        date = pv.start_date or dd.today(-delta)
        last = pv.end_date or dd.today(delta)

        while date <= last:
            yield cls.get_row_by_pk(ar, date2pk(date))
            date = step(date)



class DayNavigator(DaysTable):
    """

    Base class for the three calendar views, but also used for independent
    tables like working.WorkedHours. A virtual table whose rows are calview.Day
    instances.  Subclasses must set navigation_mode.

    """

    # every row is a Day instance. Note that Day can be overridden.

    abstract = True
    editable = False
    # required_roles = dd.login_required((OfficeUser, OfficeOperator))
    required_roles = dd.login_required(OfficeUser)
    parameters = ObservedDateRange(
        user=dd.ForeignKey('users.User', null=True, blank=True))
    column_names = "detail_link *"
    params_panel_hidden = False
    display_mode = "html"
    # hide_top_toolbar = True
    planner = None  # must be set for concrete subclasses

    @classmethod
    def get_navinfo(cls, ar, day):
        assert isinstance(day, Day)
        day.navigation_mode = cls.navigation_mode  # so that str() gives the right format
        ni = dict(recno=day.pk, message=str(day))

        if cls.navigation_mode == "month":
            ni.update(next=date2pk(day.skipmonth(1)))
            ni.update(prev=date2pk(day.skipmonth(-1)))
            ni.update(first=day.pk - 365)
            ni.update(last=day.pk + 365)
        elif cls.navigation_mode == "week":
            ni.update(next=day.pk + 7)
            ni.update(prev=day.pk - 7)
            ni.update(first=date2pk(day.skipmonth(-1)))
            ni.update(last=date2pk(day.skipmonth(1)))
        elif cls.navigation_mode == "day":
            ni.update(next=day.pk + 1)
            ni.update(prev=day.pk - 1)
            ni.update(first=date2pk(day.skipmonth(-1)))
            ni.update(last=date2pk(day.skipmonth(1)))
        else:
            raise Exception("Invalid navigation_mode {}".format(
                cls.navigation_mode))
        return ni

    @dd.virtualfield(models.IntegerField(_("Day number")))
    def day_number(cls, obj, ar):
        return obj.pk

    @classmethod
    def get_pk_field(cls):
        # return pk_field
        # return PK_FIELD
        # return cls.get_data_elem('day_number')
        return cls.day_number.return_type

class CalendarView(DayNavigator):
    """
    A calendar view opens in detail view by default, the grid view is useless.

    The detail of a calendar view usually has a calendar navigator panel at the
    left side.  The right side varies, but it usually shows at least one slave
    table which is usually a subclass of DaySlave.

    """
    abstract = True
    use_detail_param_panel = True
    # plannable_model = None  # must be set for concrete subclasses

    @classmethod
    def get_planner(cls):
        return cls.planner

    @classmethod
    def get_default_action(cls):
        return dd.ShowDetail(cls.detail_layout)

    @dd.htmlbox()
    def navigation_panel(cls, obj, ar):
        if ar is None:
            return None
        # if ar.actor.navigator is None:
        #     # raise Exception("Oops, {} has no navigator".format(cls))
        #     print("Oops, {} has no navigator".format(cls))
        #     return None

        today = obj.date
        # daily, weekly, monthly = obj.cal_view.navigator.make_link_funcs(ar)

        daily = obj.planner.daily_button_func(ar)
        weekly = obj.planner.weekly_button_func(ar)
        monthly = obj.planner.monthly_button_func(ar)

        if obj.navigation_mode == 'day':
            long_unit = DurationUnits.months
            short_unit = DurationUnits.days
            current_view = daily
        elif obj.navigation_mode == 'week':
            long_unit = DurationUnits.months
            short_unit = DurationUnits.weeks
            current_view = weekly
        elif obj.navigation_mode == 'month':
            long_unit = DurationUnits.years
            short_unit = DurationUnits.months
            current_view = monthly
        else:
            raise Exception("20200224")

        daily_mode = bool(obj.navigation_mode == 'day')
        weekly_view = bool(obj.navigation_mode == 'week')
        month_view = bool(obj.navigation_mode == 'month')

        # todo ensure that the end of the month is always in the view.
        # long_unit = DurationUnits.years if month_view else DurationUnits.months
        long_prev = cls.get_row_by_pk(ar, date2pk(long_unit.add_duration(today, -1)))
        long_next = cls.get_row_by_pk(ar, date2pk(long_unit.add_duration(today, 1)))
        # next_unit = DurationUnits.weeks if weekly_view else DurationUnits.days if day_view else DurationUnits.months
        short_prev = cls.get_row_by_pk(ar, date2pk(short_unit.add_duration(today, -1)))
        short_next = cls.get_row_by_pk(ar, date2pk(short_unit.add_duration(today, 1)))
        # current_view = weekly if weekly_view else daily
        # current_view = daily
        # if not day_view:
        #     current_view = monthly if month_view else weekly

        elems = [] #cls.calender_header(ar)

        # Month div
        rows, cells = [], []
        for i, month in enumerate(YearMonths.get_list_items()):
            pk = date2pk(DurationUnits.months.add_duration(today, i+1 - today.month))
            if today.month == i+1:
                if not month_view:
                    cells.append(E.td(E.b(monthly(cls.get_row_by_pk(ar, pk), str(month)))))
                else:
                    cells.append(E.td(E.b(str(month))))
            else:
                cells.append(E.td(monthly(cls.get_row_by_pk(ar, pk), str(month))))
            if (i+1) % 3 == 0:
                rows.append(E.tr(*cells, align="center"))
                cells = []
        monthly_div = E.div(E.table(
            *rows, align="center"), CLASS="cal-month-table")

        header = [
            current_view(long_prev, "<<"), " " , current_view(short_prev, "<"),
            E.span(E.span("{} {}".format(monthname(today.month), today.year), E.br(), monthly_div)),
            current_view(short_next, ">"), " ", current_view(long_next, ">>")]
        elems.append(E.h2(*header, align="center"))
        weekdaysFirstLetter = " " + "".join([gettext(week.text)[0] for week in Weekdays.objects()])
        rows = [E.tr(*[E.td(E.b(day_of_week)) for day_of_week in weekdaysFirstLetter], align='center')]
        for week in CALENDAR.monthdatescalendar(today.year, today.month):
            # each week is a list of seven datetime.date objects.
            cells = []
            current_week = week[0].isocalendar()[1]
            this_week = False
            for day in week:
                pk = date2pk(day)
                link = daily(cls.get_row_by_pk(ar, pk), str(day.day))
                if day == dd.today():
                    link = E.b(link, CLASS="cal-nav-today")
                if day == today and daily_mode:
                    cells.append(E.td(E.b(str(day.day))))
                else:
                    cells.append(E.td(link))
                if day.isocalendar()[1] == today.isocalendar()[1]:
                    this_week = True
            else:
                cells = [
                    E.td(E.b(str(current_week)) if this_week and weekly_view else weekly(cls.get_row_by_pk(ar, pk), str(current_week)),
                         CLASS="cal-week")
                         ] + cells
            rows.append(E.tr(*cells, align="center"))

        today = cls.get_row_by_pk(ar, 0)
        elems.append(E.table(*rows, align="center"))
        elems.append(E.p(daily(today, gettext("Today")), align="center"))
        elems.append(E.p(weekly(today, gettext("This week")), align="center"))
        elems.append(E.p(monthly(today, gettext("This month")), align="center"))

        # for o in range(-10, 10):
        #     elems.append(ar.goto_pk(o, str(o)))
        #     elems.append(" ")
        return E.div(*elems, CLASS="lino-nav-cal")



class DaySlave(AbstractTable):

    """
    Table mixin for slave tables of tables on calview.Day.

    Used by both database and virtual tables.
    """

    abstract = True
    editable = False
    hide_top_toolbar = True # no selections no toolbar
    preview_limit = 0       # no paginator & all rows.
    use_detail_params_value = True # Get parameter values from detail view.
    master = 'calview.Day'
    # navigation_mode = "day"  # or "week" or "month"
    calendar_view = None
    with_header_row = True

    @classmethod
    def class_init(cls):
        super(DaySlave, cls).class_init()
        if isinstance(cls.calendar_view, str):
            cls.calendar_view = rt.models.resolve(cls.calendar_view)

    @classmethod
    def get_master_instance(cls, ar, model, pk):
        return model(int(pk), ar, cls.calendar_view.navigation_mode, cls.calendar_view.planner)

    @classmethod
    def get_calendar_entries(cls, ar, obj):
        qs = rt.models.cal.Events.get_request_queryset(ar)
        if obj is not None:
            qs = obj.get_my_plannable_entries(qs, ar)
        return qs

    @classmethod
    def get_dayslave_rows(cls, ar):
        # subclasses must implement this. they must not use the default
        # get_request_queryset() because we are cloning filter parameters.
        return []

    @classmethod
    def get_data_rows(cls, ar):
        if cls.with_header_row:
            yield cls.model.HEADER_ROW
        for obj in cls.get_dayslave_rows(ar):
            yield obj

        # if issubclass(cls, dd.Table):
        #     # print("20200307 {}".format(super(DaySlave, cls).get_request_queryset))
        #     try:
        #         get_request_queryset = super(DaySlave, cls).get_request_queryset
        #     except AttributeError:
        #         raise Exception("{} has no get_request_queryset() method".format(cls))
        #         # when inheriting from DaySlave and a model-based table, model-based
        #         # table must come before DaySlave in the MRO
        #
        #     for obj in get_request_queryset(ar):
        #         yield obj
        # else:
        #     get_data_rows = super(DaySlave, cls).get_data_rows
        #     if get_data_rows is None:
        #         raise Exception("{} has no get_data_rows() method".format(cls))
        #     for obj in get_data_rows(ar):
        #         yield obj
        # return super(DaySlave, cls).get_request_queryset(ar, **filter)

    @classmethod
    def unused_get_calview_chunks(cls, self, ar):
        """

        Yield a series of HTML elements or strings that represent the given
        calendar entry as a paragraph.

        """
        pv = ar.param_values
        if self.start_time:
            yield str(self.start_time)[:5]

        # elif not pv.start_date:
            # t.append(str(self.start_date))
        if not pv.user and self.user:
            yield str(self.user)
        if self.summary:
            yield self.summary
        if not pv.event_type and self.event_type:
            yield str(self.event_type)
        if not pv.room and self.room:
            yield str(self.room)
        if settings.SITE.project_model is not None and not pv.project and self.project:
            yield str(self.project)

    @classmethod
    def get_calview_div(cls, obj, ar):
        """Return a <div> for this calendar entry in the view given by ar.

        """
        time_text = ""
        if obj.start_time:
            time_text = "{} ".format(obj.start_time)[:5]

        # text = E.span(*cls.get_calview_chunks(obj, ar))
        text = E.span(time_text, " ", *obj.get_event_summary(ar))
        color = obj.get_diplay_color()
        if color:
            dot  = E.span("\u00A0", CLASS="dot",
                style="background-color: {};".format(color))
            # ele.attrib['style'] = "color: white;background-color: {};".format(data_color)
            # dot.attrib['style'] = "background-color: {};".format(data_color)
            return E.div(dot, text)
        else:
            return E.div(text)

class DailySlaveBase(DaySlave, VentilatedColumns):
    abstract = True
    label = _("Daily planner")
    column_names_template = "overview:12 {vcolumns}"
    ventilated_column_suffix = ':20'
    required_roles = dd.login_required((OfficeUser, OfficeOperator))
    calendar_view = "calview.DailyView"
    details_of_master_template = _("%(details)s on %(master)s")

    @classmethod
    def get_dayslave_rows(cls, ar):
        return rt.models.calview.DailyPlannerRow.objects.all()

    @classmethod
    def get_ventilated_columns(cls):
        for pc in PlannerColumns.objects():
            yield cls.get_daily_field(pc)

    @classmethod
    def get_daily_field(cls, pc):
        Event = rt.models.cal.Event
        def func(fld, obj, ar):
            # obj is a DailyPlannerRow instance
            mi = ar.master_instance
            if mi is None:  # e.g. when using DailySlave from dashboard.
                mi = cls.calendar_view.get_row_by_pk(ar, 0)
            qs = cls.get_calendar_entries(ar, obj)
            qs = qs.filter(event_type__planner_column=pc)
            qs = qs.filter(start_date=mi.date)
            # pv = ar.param_values
            # qs = Event.calendar_param_filter(qs, pv)
            # current_day = pv.get('date', dd.today())
            # if current_day:
            #     qs = qs.filter(start_date=current_day)
            # if obj is cls.model.HEADER_ROW:
            #     qs = qs.filter(start_time__isnull=True)
            # else:
            #     get_plannable_entries
            #     if obj.start_time:
            #         qs = qs.filter(start_time__gte=obj.start_time,
            #                        start_time__isnull=False)
            #     if obj.end_time:
            #         qs = qs.filter(start_time__lt=obj.end_time,
            #                        start_time__isnull=False)
            qs = qs.order_by('start_time')
            chunks = [e.obj2href(ar, cls.get_calview_div(e, ar)) for e in qs]
            return E.p(*join_elems(chunks))

        return dd.VirtualField(dd.HtmlBox(pc.text), func)


class WeeklySlaveBase(DaySlave, VentilatedColumns):

    """subclassed by WeeklySlave, but also in Presto where we define a custom
    weekly Slave as a class WorkersByWeek(Workers, WeeklySlaveBase)"""

    abstract = True
    label = _("Weekly planner")
    column_names_template = "overview:12 {vcolumns}"
    ventilated_column_suffix = ':20'
    # navigation_mode = "week"
    calendar_view = "calview.WeeklyView"
    details_of_master_template = _("%(details)s in %(master)s")

    @classmethod
    def get_dayslave_rows(cls, ar):
        return rt.models.calview.DailyPlannerRow.objects.all()

    @classmethod
    def get_ventilated_columns(cls):
        for wd in Weekdays.objects():
            yield cls.get_weekly_field(wd)

    @classmethod
    def get_weekly_field(cls, week_day):
        def func(fld, obj, ar):
            # obj is a Plannable instance
            qs = cls.get_calendar_entries(ar, obj)
            delta_days = int(ar.rqdata.get('mk', 0) or 0) if ar.rqdata else ar.master_instance.pk
            # current_day = dd.today() + timedelta(days=delta_days)
            delta_days += int(week_day.value) - dd.today().weekday() - 1
            today = dd.today(delta_days)
            # current_week_day = current_day + \
            #     timedelta(days=int(week_day.value) - current_day.weekday() - 1)
            qs = qs.filter(start_date=today)
            qs = qs.order_by('start_time')
            if obj is cls.model.HEADER_ROW:
                chunks = obj.get_header_chunks(ar, qs, today)
            else:
                chunks = obj.get_weekly_chunks(ar, qs, today)
            return E.table(E.tr(E.td(E.div(*join_elems(chunks)))),
                CLASS="fixed-table")

        return dd.VirtualField(dd.HtmlBox(week_day.text), func)


class MonthlySlaveBase(DaySlave, VentilatedColumns):
    abstract = True
    label = _("Monthly planner")
    column_names_template = "week_number:2 {vcolumns}"
    ventilated_column_suffix = ':20'
    # navigation_mode = "week"
    calendar_view = "calview.MonthlyView"
    details_of_master_template = _("%(details)s in %(master)s")

    @classmethod
    def get_ventilated_columns(cls):
        for wd in Weekdays.get_list_items():
            yield cls.get_monthly_field(wd)

    @classmethod
    def get_monthly_field(cls, wd):
        Events = rt.models.cal.Events
        def func(fld, obj, ar):
            # obj is the first day of the week to show
            # pv = ar.param_values
            today = dd.today()
            # if pv is None:
            #     return
            qs = cls.get_calendar_entries(ar, None)
            # qs = Event.objects.all()
            # qs = Event.calendar_param_filter(qs, pv)
            mi = ar.master_instance
            if mi is None:
                return
            target_day = cls.get_row_by_pk(ar, obj.pk + int(wd.value) - 1)
            current_month = mi.date.month
            nav = mi.planner

            # offset = ar.master_instance.pk
            # offset = int(ar.rqdata.get('mk', 0) or 0) if ar.rqdata else ar.master_instance.pk
            # current_date = dd.today(offset)
            # pk = offset + int(wd.value) - 1
            # target_day = cls.get_row_by_pk(ar, pk)
            # if target_day is None:
            #     return
            # target_day = week[int(wd.value)-1]
            qs = qs.filter(start_date=target_day.date)
            qs = qs.order_by('start_time')
            chunks = [E.p(e.obj2href(ar, cls.get_calview_div(e, ar))) for e in qs]

            # pk = date2pk(target_day)


            # nav.daily_view
            # sar = ar.spawn_request(actor=actor, param_values=ar.param_values)
            # rnd = settings.SITE.kernel.default_renderer
            # def func(day, text):
            #     # day.navigation_mode = actor.navigation_mode
            #     return rnd.ar2button(sar, day, text, style="", icon_name=None, title=str(day))
            #

            daily = nav.daily_button_func(ar)
            daily_link = daily(target_day, str(target_day.date.day))
            if target_day.date == today:
                daily_link = E.b(daily_link)

            # header_items = [daily_link]
            # header_items = Event.gen_insert_button(cls, header_items, ar, target_day)
            header_items = [daily_link]
            btn = ar.gen_insert_button(Events, start_date=target_day.date)
            if btn:
                header_items.append(btn)

            header = E.div(*header_items, align="center", CLASS="header" )
            return E.table(E.tr(E.td(*[header, E.div(*join_elems(chunks))])),
                           CLASS="fixed-table cal-month-cell {} {} {}".format(
                             "current-month" if current_month == target_day.date.month else "other-month",
                             "current-day" if target_day.date == today else "",
                             "cal-in-past" if target_day.date < today else ""
                         ))

        return dd.VirtualField(dd.HtmlBox(wd.text), func)


class DailyPlanner(EventsParameters, DailySlaveBase, DailyPlannerRows):
# 20200430 class DailyPlanner(DailySlaveBase, DailyPlannerRows):
    # display_mode = "html"
    navigation_mode = 'day'

class DailySlave(DailyPlanner):
    # label = None
    @classmethod
    def get_actor_label(self): return None

class WeeklySlave(EventsParameters, WeeklySlaveBase, DailyPlannerRows):
# 20200430 class WeeklySlave(WeeklySlaveBase, DailyPlannerRows):
    # model = 'calview.DailyPlannerRow'
    # required_roles = dd.login_required(OfficeStaff)
    # display_mode = "html"

    # label = None
    @classmethod
    def get_actor_label(self): return None

    # @classmethod
    # def param_defaults(cls, ar, **kw):
    #     kw = super(WeeklySlave, cls).param_defaults(ar, **kw)
    #     kw.update(user=ar.get_user())  # TODO: not sure whether we want this
    #     return kw

class MonthlySlave(EventsParameters, MonthlySlaveBase, DaysTable):
# 20200430 class MonthlySlave(MonthlySlaveBase, DaysTable):
    # required_roles = dd.login_required(OfficeStaff)
    with_header_row = False
    navigation_mode = "month"

    label = None
    @classmethod
    def get_actor_label(self): return None

    @classmethod
    def get_planner(cls):
        return cls.calendar_view.planner

    @classmethod
    def get_data_rows(cls, ar):
        mi = ar.master_instance  # a Day instance
        if mi is None:
            return

        year, month = mi.date.year, mi.date.month
        # inspired by calendar.Calendar.itermonthdates
        date = datetime.date(year, month, 1)
        # Go back to the beginning of the week
        days = (date.weekday() - CALENDAR.firstweekday) % 7
        date -= datetime.timedelta(days=days)
        # date = CALENDAR.itermonthdates(year, month).next()
        while True:
            yield cls.get_row_by_pk(ar, date2pk(date))
            try:
                date += ONE_WEEK
            except OverflowError:
                # Adding could fail after datetime.MAXYEAR
                break
            if date.month != month and date.weekday() == CALENDAR.firstweekday:
                break

    @dd.displayfield("Week")
    def week_number(cls, obj, ar):
        # obj is the first day of the week
        if not isinstance(obj, Day):
            raise Exception("{} is not a Day".format(obj))
        if ar.param_values is None:
            return None
        label = str(obj.date.isocalendar()[1])
        # label = str(week[0].isocalendar()[1])
        # pk = date2pk(week[0])
        # nav = ar.master_instance.ar.actor.planner  # 20200224
        # daily, weekly, monthly = nav.make_link_funcs(ar)
        # weekly = nav.weekly_button_func(ar)
        # link = weekly(Day(pk), label)
        link = label
        return E.div(*[link], align="center")

    @classmethod
    def param_defaults(cls, ar, **kw):
        kw = super(MonthlySlave, cls).param_defaults(ar, **kw)
        kw.update(user=ar.get_user())
        return kw


class DayDetail(dd.DetailLayout):
    main = "body"
    body = "navigation_panel:15 calview.DailySlave:85"

class WeekDetail(dd.DetailLayout):
    main = "body"
    # body = dd.Panel("navigation_panel:15 calview.WeeklySlave:85", label=_("Planner"))
    body = "navigation_panel:15 calview.WeeklySlave:85"

class MonthDetail(dd.DetailLayout):
    main = "body"
    body = "navigation_panel:15 calview.MonthlySlave:85"

class DailyView(EventsParameters, CalendarView):
# 20200430 class DailyView(CalendarView):
    label = _("Daily view")
    detail_layout = 'calview.DayDetail'
    navigation_mode = "day"
    insert_event = InsertEvent()

class WeeklyView(EventsParameters, CalendarView):
# 20200430 class WeeklyView(CalendarView):
    label = _("Weekly view")
    detail_layout = 'calview.WeekDetail'
    navigation_mode = "week"

class MonthlyView(EventsParameters, CalendarView):
# 20200430 class MonthlyView(CalendarView):
    label = _("Monthly view")
    detail_layout = 'calview.MonthDetail'
    navigation_mode = "month"
