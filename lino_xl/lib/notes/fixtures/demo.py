# coding: utf-8
# Copyright 2009-2015 Luc Saffre
#
# This file is part of Lino XL.
#
# Lino XL is free software: you can redistribute it and/or modify it
# under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.
#
# Lino XL is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public
# License along with Lino XL.  If not, see
# <http://www.gnu.org/licenses/>.

"""Generate some fictive notes.

"""

from django.conf import settings

from lino.utils.instantiator import Instantiator
from lino.utils import Cycler

from lino.api import rt, _

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
    User = rt.modules.users.User
    Note = rt.modules.notes.Note
    NoteType = rt.modules.notes.NoteType

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
