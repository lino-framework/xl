# -*- coding: UTF-8 -*-
# Copyright 2017-2020 Rumma & Ko Ltd
# License: BSD (see file COPYING for details)

from etgen.html import E

from lino.api import dd, rt, _
from lino.core.fields import TableRow

def gen_insert_button(actor, header_items, Event, ar, target_day):
    """Hackish solution to not having to recreate a new sub request when generating lots of insert buttons.
    Stores values in the actor as a cache, and uses id(ar) to check if it's a new request and needs updating.
    Works by replacing known unique value with the correct known value for the insert window."""
    if ar.get_user().authenticated:

        if (getattr(actor, "insert_button", None) is not None
                and actor.insert_button_ar_id == id(ar)):
            insert_button= actor.insert_button.__copy__()
        else:
            # print("Making button")
            sar = Event.get_default_table().insert_action.request_from(ar)
        # print(20170217, sar)
            sar.known_values = dict(start_date="PLACEHOLDER")
            actor.insert_button = sar.ar2button(None)
            actor.insert_button_ar_id = id(ar)
            insert_button = actor.insert_button.__copy__()

        insert_button.set("href", insert_button.get("href").replace("PLACEHOLDER", str(target_day)))
        insert_button = E.span(insert_button , style="float: right;")
        header_items.append(insert_button)
        # btn.set("style", "padding-left:10px")
    return header_items



class Plannable(dd.Model):
    class Meta:
        abstract = True

    @classmethod
    def get_plannable_header_row(cls):
        # class WrappedHeaderRow(cls):
        #     class Meta:
        #         proxy = True
        #     def __str__(self):
        #         return str(_("All day"))
        #
        # return cls()
        return HeaderRow()

    def get_header_chunks(obj, ar, qs, today):
        qs = qs.filter(start_time__isnull=True)
        txt = str(today.day) \
            if today != dd.today() \
            else E.b(str(today.day))

        yield E.p(*gen_insert_button(
            ar.actor, [txt], rt.models.cal.Event, ar, today),
               align="center")
        for e in qs:
            yield e.obj2href(ar, e.colored_calendar_fmt(ar.param_values))


    def get_weekly_chunks(obj, ar, qs, today):
        return [e.obj2href(ar, e.colored_calendar_fmt(ar.param_values)) for e in qs]

# class HeaderRow(Plannable):
#     def __str__(self):
#         return str(_("All day"))
#
# HEADER_ROW = HeaderRow()


class HeaderRow(Plannable):
    class Meta:
        abstract = True
    show_in_site_search = False

    def __getattr__(self, name):
        return None

    def __str__(self):
        return str(_("All day"))
