# -*- coding: UTF-8 -*-
# Copyright 2011-2017 Rumma & Ko Ltd
#
# License: BSD (see file COPYING for details)


from __future__ import unicode_literals

from django.conf import settings
from lino.api import dd, rt, _
from lino.core.gfks import gfk2lookup
from .choicelists import EntryStates, GuestStates



class ShowEntriesByDay(dd.Action):
    label = _("Today")
    show_in_bbar = True
    sort_index = 60
    icon_name = 'calendar'

    def __init__(self, date_field, **kw):
        self.date_field = date_field
        super(ShowEntriesByDay, self).__init__(**kw)

    def run_from_ui(self, ar, **kw):
        obj = ar.selected_rows[0]
        today = getattr(obj, self.date_field)
        pv = dict(start_date=today)
        pv.update(end_date=today)
        sar = ar.spawn(rt.models.cal.EntriesByDay, param_values=pv)
        js = ar.renderer.request_handler(sar)
        ar.set_response(eval_js=js)


class UpdateGuests(dd.Action):

    label = _('Update presences')
    # icon_name = 'lightning'
    button_text = ' ☷ '  # 2637
    custom_handler = True

    def run_from_ui(self, ar, **kw):
        if settings.SITE.loading_from_dump:
            return 0
        for obj in ar.selected_rows:
            self.run_on_event(ar, obj)
            
    def run_on_event(self, ar, obj):

        if not obj.state.edit_guests:
            # ar.info("not state.edit_guests")
            return
        if not obj.event_type or not obj.event_type.fill_presences:
            return

        c = u = d = 0
        # existing = set([g.partner.pk for g in obj.guest_set.all()])
        existing = {g.partner.pk : g for g in obj.guest_set.all()}
        #print("20190328 existing: {}".format(existing))
        # create suggested guest that don't exist
        for sg in obj.suggest_guests():
            #print("20190328 suggested {}".format(sg))
            eg = existing.pop(sg.partner.pk, None)
            if eg is None:
                sg.save()
                c += 1
            else:
                u += 1

        # remove unwanted participants
        for pk, g in existing.items():
            if g.state == GuestStates.invited:
                g.delete()
                d += 1
        msg = _("Update presences for {} : "
                "{} created, {} unchanged, {} deleted.").format(
                    obj, c, u, d)
        ar.info(msg)


class UpdateAllGuests(UpdateGuests):
    
    def run_from_ui(self, ar, **kw):
        Event = rt.models.cal.Event
        gfk = Event._meta.get_field('owner')
        states = EntryStates.filter(fixed=False)
        
        for obj in ar.selected_rows:
            qs = Event.objects.filter(
                **gfk2lookup(gfk, obj, state__in=states))
            def ok(ar2):
                for e in qs:
                    self.run_on_event(ar, e)

            fmt = obj.get_date_formatter()
            txt = ', '.join([fmt(e.start_date) for e in qs])
            ar.confirm(ok, _("Update presences for {} events: {}").format(
                qs.count(), txt))
