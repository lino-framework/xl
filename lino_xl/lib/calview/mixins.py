# -*- coding: UTF-8 -*-
# Copyright 2017-2020 Rumma & Ko Ltd
# License: BSD (see file COPYING for details)

from django.conf import settings
from etgen.html import E

from lino.api import dd, rt, _
from lino.core.fields import TableRow

def button_func(ar, actor):
    if actor is None:
        def func(day, text):
            return str(text)
    else:
        sar = ar.spawn_request(actor=actor, param_values=ar.param_values)
        rnd = settings.SITE.kernel.default_renderer
        def func(day, text):
            # day.navigation_mode = actor.navigation_mode
            return rnd.ar2button(sar, day, text, style="", icon_name=None, title=str(day))
    return func

class Planner(dd.Choice):
    daily_view = None
    weekly_view = None
    monthly_view = None
    default_view = None

    def __init__(self, value_and_name, text, dv, wv, mv, **kwargs):
        super(Planner, self).__init__(value_and_name, text, value_and_name, **kwargs)
        self.daily_view = dv
        self.weekly_view = wv
        self.monthly_view = mv

    def on_class_init(self):
        self.daily_view = rt.models.resolve(self.daily_view)
        self.weekly_view = rt.models.resolve(self.weekly_view)
        self.monthly_view = rt.models.resolve(self.monthly_view)
        self.default_view = self.weekly_view
        for a in (self.daily_view, self.weekly_view, self.monthly_view):
            if a is None:
                continue
            if a.planner is not None:
                raise Exception(
                    "Cannot use {} for planner {} as it is already used for {}".format(
                    a, self, a.planner))
            a.planner = self

    def daily_button_func(self, ar):
        return button_func(ar, self.daily_view)

    def weekly_button_func(self, ar):
        return button_func(ar, self.weekly_view)

    def monthly_button_func(self, ar):
        return button_func(ar, self.monthly_view)


class Planners(dd.ChoiceList):
    item_class = Planner

    @classmethod
    def class_init(cls):
        super(Planners, cls).class_init()
        for nav in cls.get_list_items():
            nav.on_class_init()

add = Planners.add_item
add("default", _("Calendar"), "calview.DailyView", "calview.WeeklyView", "calview.MonthlyView")


class Plannable(dd.Model):
    class Meta:
        abstract = True

    plannable_header_row_label = _("All day")

    @classmethod
    def on_analyze(cls, site):
        super(Plannable, cls).on_analyze(site)
        cls.HEADER_ROW = HeaderRow(cls)

    @classmethod
    def get_plannable_entries(cls, obj, qs, ar):
        """

        Modify the given queryset of cal.Event objects to be shown in this
        calendar view for the given plannable object `obj`, which is either an
        instance of cls or a HeaderRow instance.

        Date and time filter will be applied later.

        Default implementation does not modify the queryset.

        """
        return qs
        # return rt.models.cal.Event.objects.none()

    def get_my_plannable_entries(self, qs, ar):
        return self.get_plannable_entries(self, qs, ar)

    def get_header_chunks(obj, ar, entries, today):
        if not isinstance(obj, HeaderRow):
            raise Exception("{} is not a header row".format(obj))
        entries = entries.filter(start_time__isnull=True)
        txt = str(today.day)
        if today == dd.today():
            txt = E.b(txt)

        btn = ar.gen_insert_button(rt.models.cal.Events, start_date=today)
        if btn is None:
            yield E.p(txt, align="center")
        else:
            yield E.p(txt, btn, align="center")
        # yield E.p(*obj.model.gen_insert_button(ar.actor, [txt], ar, today), align="center")

        for e in entries:
            yield e.obj2href(ar, ar.actor.get_calview_div(e, ar))

    def get_weekly_chunks(obj, ar, entries, today):
        if isinstance(obj, HeaderRow):
            raise Exception("{} is a header row".format(obj))
        return [e.obj2href(ar, ar.actor.get_calview_div(e, ar))
            for e in entries]

    @classmethod
    def unused_gen_insert_button(cls, actor, header_items, ar, target_day):
        """Hackish solution to not having to recreate a new sub request when generating lots of insert buttons.
        Stores values in the actor as a cache, and uses id(ar) to check if it's a new request and needs updating.
        Works by replacing known unique value with the correct known value for the insert window."""
        # print(20200227, cls)
        insert_action = rt.models.cal.Events.insert_action
        # if ar.get_user().authenticated:
        if insert_action.get_view_permission(ar.get_user().user_type):

            if (getattr(actor, "insert_button", None) is not None
                    and actor.insert_button_ar_id == id(ar)):
                insert_button = actor.insert_button.__copy__()
            else:
                # print("Making button")
                sar = insert_action.request_from(ar)
            # print(20170217, sar)
                sar.known_values = dict(start_date="PLACEHOLDER")
                actor.insert_button = sar.ar2button(style="float: right;")
                actor.insert_button_ar_id = id(ar)
                insert_button = actor.insert_button.__copy__()

            insert_button.set("href", insert_button.get("href").replace("PLACEHOLDER", str(target_day)))
            # insert_button = E.span(insert_button , style="float: right;")
            header_items.append(insert_button)
            # btn.set("style", "padding-left:10px")
        return header_items



class HeaderRow(TableRow):

    def __init__(self, model):
        self.model = model

    def __getattr__(self, name):
        return None

    def __str__(self):
        return str(self.model.plannable_header_row_label)

    def get_header_chunks(self, *args):
        return self.model.get_header_chunks(self, *args)

    def get_weekly_chunks(self, *args):
        return self.model.get_weekly_chunks(self, *args)

    def get_my_plannable_entries(self, *args):
        return self.model.get_plannable_entries(self, *args)

Plannable.django2lino(HeaderRow)
