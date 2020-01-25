# -*- coding: UTF-8 -*-
# Copyright 2011-2020 Rumma & Ko Ltd
# License: BSD (see file COPYING for details)

from collections import OrderedDict

from django.conf import settings
from django.db import models

from lino.api import dd, rt, _, gettext
from lino.mixins import ObservedDateRange
from lino.core.roles import Explorer
from lino.core.fields import TableRow
from lino.core.tables import VentilatedColumns, AbstractTable
from lino.core import fields
from lino.utils.format_date import monthname
from lino.utils.format_date import day_and_month, day_and_weekday
from lino.modlib.users.mixins import My
from lino.modlib.office.roles import OfficeUser, OfficeStaff, OfficeOperator

from lino.utils import join_elems
from etgen.html import E, forcetext

from lino_xl.lib.cal.choicelists import PlannerColumns, Weekdays
from lino_xl.lib.cal.choicelists import DurationUnits, YearMonths
from lino_xl.lib.cal.utils import when_text

from calendar import Calendar as PythonCalendar
from datetime import timedelta, datetime


CALENDAR = PythonCalendar()


def date2pk(date):
    delta = date - dd.today()
    return delta.days

def weekname(date):
    year, week, day = date.isocalendar()
    text = (date + timedelta(days=-day+1)).strftime("%d %B")
    return _("Week {1} / {0} ({2})").format(year, week, text)

def gen_insert_button(actor,header_items, Event, ar, target_day):
    """Hackish solution to not having to recreate a new sub request when generating lots of insert buttons.
    Stores values in the actor as a cache, and uses id(ar) to check if it's a new request and needs updating.
    Works by replacing known unique value with the correct known value for the insert window."""
    if ar.get_user().authenticated:

        if (getattr(actor, "insert_button",None) is not None
                and actor.insert_button_ar_id == id(ar)):

            insert_button= actor.insert_button.__copy__()
        else:
            # print("Making button")
            sar = Event.get_default_table().insert_action.request_from(ar)
        # print(20170217, sar)
            sar.known_values = dict(
            start_date="PLACEHOLDER")
            actor.insert_button = sar.ar2button(None,
                                # _(" Reply "), icon_name=None
                                )
            actor.insert_button_ar_id = id(ar)
            insert_button = actor.insert_button.__copy__()


        insert_button.set("href", insert_button.get("href").replace("PLACEHOLDER", str(target_day)))
        insert_button = E.span(insert_button , style="float: right;")
        header_items.append(insert_button)
        # btn.set("style", "padding-left:10px")
    return header_items


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

class EventsParameters(dd.Actor):

    abstract = True

    @classmethod
    def class_init(cls):
        cls.params_layout = rt.models.cal.Events.params_layout
        super(EventsParameters, cls).class_init()

    @classmethod
    def setup_parameters(cls, params):
        super(EventsParameters, cls).setup_parameters(params)
        rt.models.cal.Event.setup_parameters(params)


class DailyPlannerRows(EventsParameters, dd.Table):
    model = 'calview.DailyPlannerRow'
    column_names = "seqno designation start_time end_time"
    required_roles = dd.login_required(OfficeStaff)

class Day(TableRow):

    def __init__(self, offset=0, ar=None, navigation_mode="day"):
        self.date = dd.today(offset)
        self.pk = offset
        self.ar = ar
        self.navigation_mode = navigation_mode

    def __str__(self):
        if self.navigation_mode == "day":
            return when_text(self.date)
        elif self.navigation_mode == "week":
            return weekname(self.date)
        else:
            return monthname(self.date.month) + " " + str(self.date.year)

    def skipmonth(self, n):
        return DurationUnits.months.add_duration(self.date, n)

class DayDetail(dd.DetailLayout):
    main = "body"
    body = "navigation_panel:15 calview.PlannerByDay:85"


def make_link_funcs(ar):
    sar_daily = ar.spawn(DailyView)
    sar_weekly = ar.spawn(WeeklyView)
    sar_monthly = ar.spawn(MonthlyView)
    sar_monthly.param_values = sar_weekly.param_values = sar_daily.param_values = ar.param_values
    rnd = settings.SITE.kernel.default_renderer

    def weekly(day, text):
        return rnd.ar2button(sar_weekly, day, text, style="", icon_name=None)

    def daily(day, text):
        return rnd.ar2button(sar_daily, day, text, style="", icon_name=None)

    def monthly(day, text):
        return rnd.ar2button(sar_monthly, day, text, style="", icon_name=None)

    return daily, weekly, monthly



class Days(dd.VirtualTable):
    # every row is a Day instance. Note that Day can be overridden.

    # required_roles = dd.login_required((OfficeUser, OfficeOperator))
    required_roles = dd.login_required(OfficeUser)
    column_names = "detail_link *"
    parameters = ObservedDateRange(
        user=dd.ForeignKey('users.User', null=True, blank=True))
    model = 'calview.Day'
    editable = False
    navigation_mode = "day"  # or "week" or "month"
    abstract = True

    @classmethod
    def get_navinfo(cls, ar, day):
        assert isinstance(day, Day)
        day.navigation_mode = ar.actor.navigation_mode  # so that str() gives the right formar
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

    @classmethod
    def get_row_by_pk(cls, ar, pk):
        """
        pk is the offset from beginning_of_time
        """
        #if pk is None:
        #    pk = "0"
        # return dd.today(int(pk))
        # if ar is None:
        #     return cls.model(int(pk))
        # return cls.model(int(pk), ar.actor.navigation_mode)
        return cls.model(int(pk), ar, cls.navigation_mode)

    @classmethod
    def get_request_queryset(cls, ar, **filter):
        home = cls.get_row_by_pk(ar, 0)
        ni = cls.get_navinfo(ar, home)

        pv = ar.param_values
        date = pv.start_date or dd.today(ni['first'])
        last = pv.end_date or dd.today(ni['last'])
        if cls.navigation_mode == "day":
            step = lambda x: x + timedelta(days=1)
        elif cls.navigation_mode == "week":
            step = lambda x: x + timedelta(days=7)
        else:
            step = lambda x: DurationUnits.months.add_duration(x, 1)

        while date <= last:
            yield cls.get_row_by_pk(ar, date2pk(date))
            date = step(date)

        # # return []  # not needed for detail view
        # days = []
        # pv = ar.param_values
        # sd = pv.start_date or dd.today()
        # ed = pv.end_date or sd
        # if sd > ed:
        #     return []
        # # while sd <= ed:
        # #     days.append(sd)
        # #     sd = sd + relativedelta(days=1)
        #
        # if cls.reverse_sort_order:
        #     step = -1
        #     pk = date2pk(ed)
        # else:
        #     pk = date2pk(sd)
        #     step = 1
        # while True:  # sd <= ed:
        #     # print(20181229, sd)
        #     d = cls.model(pk, ar)
        #     if d.date > ed or d.date < sd:
        #         return days
        #     days.append(d)
        #     pk += step

class CalPlannerTable(AbstractTable):
    # todo: rename to DaysSlave ?

    editable = False
    hide_top_toolbar = True # no selections no toolbar
    preview_limit = 0       # no paginator & all rows.
    use_detail_params_value = True # Get PV values from detail view.

    master = 'calview.Day'
    navigation_mode = "day"  # or "week" or "month"

    @classmethod
    def get_master_instance(cls, ar, model, pk):
        return model(int(pk), ar, cls.navigation_mode)

    @classmethod
    def get_request_queryset(cls, ar, **filter):
        mi = ar.master_instance
        if mi is None:
            return []
        # filter.update()
        ar.param_values.update(date=mi.date)
        return super(CalPlannerTable, cls).get_request_queryset(ar, **filter)


class CalendarView(Days):

    """
    Base class for the three calendar views.

    We want all calendar view actors to inherit params_layout from the
    cal.Events table as defined by the application. But *after* the
    custom_layout_module has been loaded.  So we override the class_init()
    method.

    """

    # parameters = Calendarparameters
    # params_layout = Calendarparams_layout
    # reverse_sort_order = False
    abstract = True
    use_detail_param_panel = True
    params_panel_hidden = False
    display_mode = "html"
    # hide_top_toolbar = True
    detail_layout = 'calview.DayDetail'

    @classmethod
    def get_default_action(cls):
        return dd.ShowDetail(cls.detail_layout)

    @dd.htmlbox()
    def navigation_panel(cls, obj, ar):

        day_view = bool(cls.navigation_mode == 'day')
        weekly_view = bool(cls.navigation_mode == 'week')
        month_view = bool(cls.navigation_mode == 'month')

        # todo ensure that the end of the month is always in the view.
        today = obj.date
        daily, weekly, monthly = make_link_funcs(ar)
        long_unit = DurationUnits.years if month_view else DurationUnits.months
        prev_month = Day(date2pk(long_unit.add_duration(today, -1)))
        next_month = Day(date2pk(long_unit.add_duration(today, 1)))
        next_unit = DurationUnits.weeks if weekly_view else DurationUnits.days if day_view else DurationUnits.months
        prev_view = Day(date2pk(next_unit.add_duration(today, -1)))
        next_view = Day(date2pk(next_unit.add_duration(today, 1)))
        # current_view = weekly if weekly_view else daily
        current_view = daily
        if not day_view:
            current_view = monthly if month_view else weekly

        elems = [] #cls.calender_header(ar)

        # Month div
        rows, cells = [], []
        for i, month in enumerate(YearMonths.get_list_items()):
            # each week is a list of seven datetime.date objects.
            pk = date2pk(DurationUnits.months.add_duration(today, int(month.value) - today.month))
            if today.month == int(month.value):
                if not month_view:
                    cells.append(E.td(E.b(monthly(Day(pk), str(month)))))
                else:
                    cells.append(E.td(E.b(str(month))))
            else:
                cells.append(E.td(monthly(Day(pk), str(month))))
            if (i+1) % 3 == 0:
                rows.append(E.tr(*cells, align="center"))
                cells = []
        monthly_div = E.div(E.table(
            *rows, align="center"), CLASS="cal-month-table")

        header = [
            current_view(prev_month, "<<"), " " , current_view(prev_view, "<"),
            E.span(E.span("{} {}".format(monthname(today.month), today.year), E.br(), monthly_div)),
            current_view(next_view, ">"), " ", current_view(next_month, ">>")]
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
                link = daily(Day(pk), str(day.day))
                if day == dd.today():
                    link = E.b(link, CLASS="cal-nav-today")
                if day == today and day_view:
                    cells.append(E.td(E.b(str(day.day))))
                else:
                    cells.append(E.td(link))
                if day.isocalendar()[1] == today.isocalendar()[1]:
                    this_week = True
            else:
                cells = [
                            E.td(E.b(str(current_week)) if this_week and weekly_view else weekly(Day(pk), str(current_week)),
                                 CLASS="cal-week")
                         ] + cells
            rows.append(E.tr(*cells, align="center"))

        elems.append(E.table(*rows, align="center"))
        elems.append(E.p(daily(Day(), gettext("Today")), align="center"))
        elems.append(E.p(weekly(Day(), gettext("This week")), align="center"))
        elems.append(E.p(monthly(Day(), gettext("This month")), align="center"))

        # for o in range(-10, 10):
        #     elems.append(ar.goto_pk(o, str(o)))
        #     elems.append(" ")
        return E.div(*elems, CLASS="lino-nav-cal")

    # @classmethod
    # def get_disabled_fields(cls, obj, ar):
    #     return set()

    # @dd.displayfield(_("Date"))
    # def detail_pointer(cls, obj, ar):
    #     # print("20181230 detail_pointer() {}".format(cls))
    #     a = cls.detail_action
    #     if ar is None:
    #         return None
    #     if a is None:
    #         return None
    #     if not a.get_view_permission(ar.get_user().user_type):
    #         return None
    #     text = (str(obj),)
    #     # url = ar.renderer.get_detail_url(cls, cls.date2pk(obj))
    #     # url = ar.renderer.get_detail_url(cls, obj.pk)
    #     url = settings.SITE.kernel.default_ui.renderer.get_detail_url(cls, obj.pk)
    #     return ar.href_button(url, text)

    # @dd.displayfield(_("Date"))
    # def long_date(cls, obj, ar=None):
    #     if obj is None:
    #         return ''
    #     return dd.fdl(obj.date)



class DailyView(EventsParameters, CalendarView):
    label = _("Daily view")
    # hide_top_toolbar = True
    insert_event = InsertEvent()



class DailyPlanner(CalPlannerTable, DailyPlannerRows):
    required_roles = dd.login_required((OfficeUser, OfficeOperator))
    label = _("Daily planner")

    @classmethod
    def setup_columns(self):
        names = ''
        for i, vf in enumerate(self.get_ventilated_columns()):
            self.add_virtual_field('vc' + str(i), vf)
            names += ' ' + vf.name + ':20'

        self.column_names = "overview:3 {}".format(names)

        # ~ logger.info("20131114 setup_columns() --> %s",self.column_names)

    @classmethod
    def get_ventilated_columns(cls):

        Event = rt.models.cal.Event

        def w(pc, verbose_name):
            def func(fld, obj, ar):
                # obj is the DailyPlannerRow instance
                pv = ar.param_values
                qs = Event.objects.filter(event_type__planner_column=pc)
                qs = Event.calendar_param_filter(qs, pv)
                current_day = pv.get('date',dd.today())
                if current_day:
                    qs = qs.filter(start_date=current_day)
                if obj.start_time:
                    qs = qs.filter(start_time__gte=obj.start_time,
                                   start_time__isnull=False)
                if obj.end_time:
                    qs = qs.filter(start_time__lt=obj.end_time,
                                   start_time__isnull=False)
                if not obj.start_time and not obj.end_time:
                    qs = qs.filter(start_time__isnull=True)
                qs = qs.order_by('start_time')
                chunks = [e.obj2href(ar, e.colored_calendar_fmt(pv)) for e in qs]
                return E.p(*join_elems(chunks))

            return dd.VirtualField(dd.HtmlBox(verbose_name), func)

        for pc in PlannerColumns.objects():
            yield w(pc, pc.text)


class PlannerByDay(DailyPlanner):
    # display_mode = "html"
    navigation_mode = 'day'


######################### Weekly ########################"

class WeeklyColumns(EventsParameters, CalPlannerTable, VentilatedColumns):
    abstract = True
    column_names_template = "overview:4 {vcolumns}"
    ventilated_column_suffix = ':20'
    navigation_mode = "week"

    @classmethod
    def get_weekday_field(cls, week_day):

        Event = rt.models.cal.Event

        def func(fld, obj, ar):
            # obj is a Plannable instance
            qs = Event.objects.all()
            qs = Event.calendar_param_filter(qs, ar.param_values)
            delta_days = int(ar.rqdata.get('mk', 0) or 0) if ar.rqdata else ar.master_instance.pk
            # current_day = dd.today() + timedelta(days=delta_days)
            current_day = dd.today(delta_days)
            current_week_day = current_day + \
                timedelta(days=int(week_day.value) - current_day.weekday() - 1)
            qs = qs.filter(start_date=current_week_day)
            qs = qs.order_by('start_time')
            chunks = obj.get_weekly_chunks(ar, qs, current_week_day)
            return E.table(E.tr(E.td(E.div(*join_elems(chunks)))),
                CLASS="fixed-table")

        return dd.VirtualField(dd.HtmlBox(week_day.text), func)


    @classmethod
    def get_ventilated_columns(cls):
        for wd in Weekdays.objects():
            yield cls.get_weekday_field(wd)


class WeeklyPlanner(WeeklyColumns, dd.Table):
    model = 'calview.DailyPlannerRow'
    # required_roles = dd.login_required(OfficeStaff)
    label = _("Weekly planner")

    @classmethod
    def param_defaults(cls, ar, **kw):
        kw = super(WeeklyPlanner, cls).param_defaults(ar, **kw)
        kw.update(user=ar.get_user())
        return kw

class WeeklyDetail(dd.DetailLayout):
    main = "body"
    body = dd.Panel("navigation_panel:15 calview.WeeklyPlanner:85", label=_("Planner"))

class WeeklyView(EventsParameters, CalendarView):
    label = _("Weekly view")
    detail_layout = 'calview.WeeklyDetail'
    navigation_mode = "week"


######################### Monthly ########################


class MonthlyPlanner(CalPlannerTable, EventsParameters, dd.VirtualTable):
    # required_roles = dd.login_required(OfficeStaff)
    label = _("Monthly planner")

    @classmethod
    def get_data_rows(self, ar):
        # every row in this table is a "week", i.e. a list of seven datetime.date objects
        delta_days = int(ar.rqdata.get('mk', 0) or 0) if ar.rqdata else ar.master_instance.pk
        current_day = dd.today() + timedelta(days=delta_days)
        # weeks = [week[0].isocalendar()[1] for week in CALENDAR.monthdatescalendar(current_day.year, current_day.month)]
        return CALENDAR.monthdatescalendar(current_day.year, current_day.month)
        # return weeks

    @dd.displayfield("Week")
    def week_number(cls, week, ar):
        label = str(week[0].isocalendar()[1])
        pk = date2pk(week[0])
        if ar.param_values is None:
            return None
        daily, weekly, monthly = make_link_funcs(ar)
        link = weekly(Day(pk), label)
        return E.div(*[link], align="center")

    @classmethod
    def param_defaults(cls, ar, **kw):
        kw = super(MonthlyPlanner, cls).param_defaults(ar, **kw)
        kw.update(user=ar.get_user())
        return kw

    @classmethod
    def setup_columns(self):
        names = ''
        for i, vf in enumerate(self.get_ventilated_columns()):
            self.add_virtual_field('vc' + str(i), vf)
            names += ' ' + vf.name + ':20'
            # names += ' ' + vf.name + (':20' if i != 0 else ":3")

        self.column_names = "week_number:2 {}".format(names)

    @classmethod
    def get_ventilated_columns(cls):

        Event = rt.models.cal.Event

        def w(pc):
            verbose_name = pc.text

            def func(fld, week, ar):
                pv = ar.param_values
                if pv is None:
                    return
                qs = Event.objects.all()
                qs = Event.calendar_param_filter(qs, pv)
                offset = int(ar.rqdata.get('mk', 0) or 0) if ar.rqdata else ar.master_instance.pk
                today = dd.today()
                current_date = dd.today(offset)
                target_day = week[int(pc.value)-1]
                qs = qs.filter(start_date=target_day)
                qs = qs.order_by('start_time')
                chunks = [E.p(e.obj2href(ar, e.colored_calendar_fmt(pv))) for e in qs]

                pk = date2pk(target_day)
                daily, weekly, monthly = make_link_funcs(ar)
                daily_link = daily(Day(pk),str(target_day.day))
                if target_day == today:
                    daily_link = E.b(daily_link)

                header_items = [daily_link]
                header_items = gen_insert_button(cls, header_items, Event, ar, target_day)

                header = E.div(*header_items, align="center",CLASS="header" )
                return E.table(E.tr(E.td(*[header,E.div(*join_elems(chunks))])),
                               CLASS="fixed-table cal-month-cell {} {} {}".format(
                                 "current-month" if current_date.month == target_day.month else "other-month",
                                 "current-day" if target_day == today else "",
                                 "cal-in-past" if target_day < today else ""
                             ))

            return dd.VirtualField(dd.HtmlBox(verbose_name), func)

        for pc in Weekdays.get_list_items():
            yield w(pc)



class MonthlyDetail(dd.DetailLayout):
    main = "body"
    body = "navigation_panel:15 calview.MonthlyPlanner:85"


class MonthlyView(EventsParameters, CalendarView):
    label = _("Monthly view")
    detail_layout = 'calview.MonthlyDetail'
    navigation_mode = "month"
