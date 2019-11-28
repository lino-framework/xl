# -*- coding: UTF-8 -*-
# Copyright 2009-2018 Rumma & Ko Ltd
# License: BSD (see file COPYING for details)

from builtins import str

from django.conf import settings
from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.utils.translation import pgettext_lazy
from django.utils import timezone

from etgen.html import E
from lino.api import dd, rt, gettext
from lino import mixins
from lino.utils import join_elems

from lino.modlib.printing.mixins import PrintableType, TypedPrintable
from lino.modlib.gfks.mixins import Controllable
from lino_xl.lib.skills.mixins import Feasible
from lino.modlib.users.mixins import My, UserAuthored
from lino.modlib.notify.mixins import ChangeNotifier
from lino.modlib.uploads.mixins import UploadController
from lino_xl.lib.outbox.mixins import MailableType, Mailable
from lino_xl.lib.contacts.mixins import ContactRelated
# from lino.modlib.office.roles import OfficeUser, OfficeStaff, OfficeOperator
from lino.modlib.office.roles import OfficeStaff

from .roles import NotesUser, NotesStaff

from lino.modlib.notify.choicelists import MessageTypes
MessageTypes.add_item('notes', dd.plugins.notes.verbose_name)


from .choicelists import SpecialTypes


class NoteType(mixins.BabelNamed, PrintableType, MailableType):
    templates_group = 'notes/Note'

    class Meta:
        app_label = 'notes'
        verbose_name = _("Note Type")
        verbose_name_plural = _("Note Types")

    important = models.BooleanField(
        verbose_name=_("important"),
        default=False)
    remark = models.TextField(verbose_name=_("Remark"), blank=True)
    special_type = SpecialTypes.field(blank=True)


class NoteTypes(dd.Table):

    model = 'notes.NoteType'
    required_roles = dd.login_required(OfficeStaff)
    #~ label = _("Note types")
    column_names = 'name build_method template special_type *'
    order_by = ["name"]

    insert_layout = """
    name
    build_method
    """

    detail_layout = """
    id name
    build_method template special_type email_template attach_to_email
    remark:60x5
    notes.NotesByType
    """


class EventType(mixins.BabelNamed):

    class Meta:
        app_label = 'notes'
        verbose_name = pgettext_lazy(u"notes", u"Event Type")
        verbose_name_plural = _("Event Types")
    remark = models.TextField(verbose_name=_("Remark"), blank=True)
    body = dd.BabelTextField(_("Body"), blank=True, format='html')


class EventTypes(dd.Table):

    model = 'notes.EventType'
    required_roles = dd.login_required(OfficeStaff)
    column_names = 'name *'
    order_by = ["name"]

    detail_layout = """
    id name
    remark:60x3
    notes.NotesByEventType:60x6
    """



class Note(TypedPrintable,
           UserAuthored,
           Controllable,
           Feasible,
           ContactRelated,
           mixins.ProjectRelated,
           ChangeNotifier,
           UploadController,
           Mailable):

    manager_roles_required = dd.login_required(OfficeStaff)

    class Meta:
        app_label = 'notes'
        abstract = dd.is_abstract_model(__name__, 'Note')
        verbose_name = _("Note")
        verbose_name_plural = _("Notes")

    date = models.DateField(
        verbose_name=_('Date'), default=dd.today)
    time = dd.TimeField(
        blank=True, null=True,
        verbose_name=_("Time"),
        default=timezone.now)
    type = dd.ForeignKey(
        'notes.NoteType',
        blank=True, null=True,
        verbose_name=_('Note Type (Content)'))
    event_type = dd.ForeignKey(
        'notes.EventType',
        blank=True, null=True,
        verbose_name=_('Event Type (Form)'))
    subject = models.CharField(_("Subject"), max_length=200, blank=True)
    body = dd.RichTextField(_("Body"), blank=True, format='html')

    language = dd.LanguageField()

    def __str__(self):
        if self.event_type_id:
            return u'%s #%s' % (self.event_type, self.pk)
        return u'%s #%s' % (self._meta.verbose_name, self.pk)

    def summary_row(self, ar, **kw):
        #~ s = super(Note,self).summary_row(ui,rr)
        s = super(Note, self).summary_row(ar)
        #~ s = contacts.ContactDocument.summary_row(self,ui,rr)
        if self.subject:
            s += [' ', self.subject]
        return s

    def get_mailable_type(self):
        return self.type

    def get_print_language(self):
        return self.language

    def get_change_owner(self):
        return self.project
    
    # def get_change_observers(self, ar=None):
    #     # in lino_welfare the project is pcsw.Client
    #     prj = self.project
    #     if isinstance(prj, ChangeNotifier):
    #         for u in prj.get_change_observers(ar):
    #             yield u

    def get_change_info(self, ar, cw):
        yield E.p(
            gettext("Subject"), ': ', self.subject,
            E.br(), gettext("Client"), ': ', ar.obj2memo(self.project))
        
    

if dd.is_installed('contacts'):
    
    dd.update_field(
        Note, 'company', verbose_name=_("Recipient (Organization)"))
    dd.update_field(
        Note, 'contact_person', verbose_name=_("Recipient (Person)"))


class NoteDetail(dd.DetailLayout):
    main = """
    date:10 time event_type:25 type:25
    subject project
    company contact_person contact_role
    id user:10 language:8 build_time
    body:40 #outbox.MailsByController:40
    """


class Notes(dd.Table):
    #required_roles = dd.login_required((OfficeUser, OfficeOperator))
    required_roles = dd.login_required((NotesUser))
    model = 'notes.Note'
    detail_layout = 'notes.NoteDetail'
    column_names = "date time id user event_type type project subject * body"
    order_by = ["date", "time"]


class AllNotes(Notes):
    required_roles = dd.login_required(NotesStaff)


class MyNotes(My, Notes):
    column_names = "date time event_type type subject project body *"
    order_by = ["date", "time"]


class NotesByType(Notes):
    master_key = 'type'
    column_names = "date time event_type subject user *"
    order_by = ["date", "time"]


class NotesByEventType(Notes):
    master_key = 'event_type'
    column_names = "date time type subject user *"
    order_by = ["date", "time"]


class NotesByX(Notes):
    abstract = True
    column_names = "date time event_type type subject user *"
    order_by = ["-date", "-time"]
    display_mode = 'summary'
    insert_layout = """
    event_type:25 type:25
    subject
    project #company
    """

    @classmethod
    def summary_row(cls, ar, obj, **kwargs):
        # s = super(NotesByX, cls).summary_row(ar, obj)
        s = [dd.fds(obj.date)]
        if obj.time is not None:
            s += [" ", obj.time.strftime(
                settings.SITE.time_format_strftime)]
        s+= [" ", obj.obj2href(ar)]
        if obj.user != ar.get_user():
            s += [' (', obj.user.initials or str(obj.user), ")"]
        if obj.subject:
            s += [' ', obj.subject]
        return s

if settings.SITE.project_model is not None:

    class NotesByProject(NotesByX):
        master_key = 'project'
        # stay_in_grid = True


class NotesByOwner(NotesByX):
    master_key = 'owner'


class NotesByCompany(NotesByX):
    master_key = 'company'


class NotesByPerson(NotesByX):
    master_key = 'contact_person'



dd.inject_field(
    'system.SiteConfig',
    'system_note_type',
    dd.ForeignKey(
        'notes.EventType',
        blank=True, null=True,
        verbose_name=_("Default system note type"),
        help_text=_("""\
Note Type used by system notes.
If this is empty, then system notes won't create any entry to the Notes table.""")))


