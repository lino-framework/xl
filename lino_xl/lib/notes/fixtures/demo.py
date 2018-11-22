# coding: utf-8
# Copyright 2009-2016 Rumma & Ko Ltd
#
# License: BSD (see file COPYING for details)

"""Generate some fictive notes.

"""

from django.conf import settings

from lino.utils.instantiator import Instantiator
from lino.utils import Cycler

from lino.api import _, dd, rt

SUBJECTS = Cycler((
    _("Get acquaintaned"),
    _("Ideas"),
    _("Feedback after first working day"),
    _("More ideas"),
    _("Tried to explain"),
    _("Appointment with RCycle"),
    _("Cancelled"),
    _("Apologized via SMS"),
))


def objects():
    User = rt.models.users.User
    Note = rt.models.notes.Note
    NoteType = rt.models.notes.NoteType

    USERS = Cycler(User.objects.all())
    if settings.SITE.project_model is not None:
        Project = settings.SITE.project_model
        qs = Project.objects.all()
        if qs.count() > 10:
            qs = qs[:10]
        PROJECTS = Cycler(qs)
    NTYPES = Cycler(NoteType.objects.all())

    notetype = Instantiator('notes.NoteType').build
    tel = notetype(name="phone report")
    yield tel
    yield notetype(name="todo")

    for i in range(100):
        kw = dict(user=USERS.pop(),
                  date=settings.SITE.demo_date(days=i-400),
                  subject=SUBJECTS.pop(),  # "Important note %d" % i,
                  type=NTYPES.pop())
        if settings.SITE.project_model is not None:
            kw.update(project=PROJECTS.pop())
        yield Note(**kw)

    EventType = rt.models.notes.EventType
    system_note = EventType(**dd.str2kw('name', _("System note")))
    yield system_note
    # print("20180502 notes.fixtures.demo calls update")
    settings.SITE.site_config.update(system_note_type=system_note)
