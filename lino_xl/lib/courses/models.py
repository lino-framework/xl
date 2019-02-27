# -*- coding: UTF-8 -*-
# Copyright 2012-2018 Rumma & Ko Ltd
# License: BSD (see file COPYING for details)

from __future__ import unicode_literals
from __future__ import print_function
from builtins import str

# from decimal import Decimal
from lino_xl.lib.ledger.utils import ZERO, ONE

from django.db import models
from django.db.models import Q
from django.conf import settings
from django.core.exceptions import ValidationError
from django.utils.translation import ugettext_lazy as _
from django.utils.translation import pgettext_lazy as pgettext
from django.utils.text import format_lazy

from lino.api import dd, rt
from lino import mixins

from etgen.html import E, join_elems, tostring
from lino.mixins import Referrable
from lino.mixins.human import parse_name
from lino.mixins.duplicable import Duplicable
from lino.mixins.periods import DateRange
from lino_xl.lib.excerpts.mixins import Certifiable
from lino_xl.lib.excerpts.mixins import ExcerptTitle
from lino.modlib.users.mixins import UserAuthored
from lino.modlib.printing.mixins import Printable
# from lino.modlib.printing.utils import PrintableObject
from lino_xl.lib.cal.mixins import Reservation
from lino_xl.lib.cal.choicelists import Recurrencies
from lino_xl.lib.cal.utils import day_and_month
from lino_xl.lib.contacts.mixins import ContactRelated

from lino.utils.dates import DateRangeValue

from .choicelists import EnrolmentStates, CourseStates, CourseAreas
from .actions import PrintPresenceSheet

cal = dd.resolve_app('cal')

try:
    teacher_model = dd.plugins.courses.teacher_model
    teacher_label = dd.plugins.courses.teacher_label
    pupil_model = dd.plugins.courses.pupil_model
    pupil_name_fields = dd.plugins.courses.pupil_name_fields
except AttributeError:
    # Happens only when Sphinx autodoc imports it and this module is
    # not installed.
    teacher_label = _("Instructor")
    teacher_model = 'foo.Bar'
    pupil_model = 'foo.Bar'
    pupil_name_fields = 'foo bar'

FILL_EVENT_GUESTS = False


class StartEndTime(dd.Model):

    class Meta:
        abstract = True
    start_time = dd.TimeField(
        blank=True, null=True,
        verbose_name=_("Start Time"))
    end_time = dd.TimeField(
        blank=True, null=True,
        verbose_name=_("End Time"))


@dd.python_2_unicode_compatible
class Slot(mixins.Sequenced, StartEndTime):

    class Meta:
        app_label = 'courses'
        app_label = 'courses'
        verbose_name = _("Timetable Slot")  # Zeitnische
        verbose_name_plural = _('Timetable Slots')

    name = models.CharField(max_length=200,
                            blank=True,
                            verbose_name=_("Name"))

    def __str__(self):
        return self.name or "%s-%s" % (self.start_time, self.end_time)


class Topic(mixins.BabelNamed, Printable, Duplicable):

    class Meta:
        app_label = 'courses'
        verbose_name = _("Topic")
        verbose_name_plural = _('Topics')


@dd.python_2_unicode_compatible
class Line(Referrable, Duplicable, ExcerptTitle, ContactRelated):
    class Meta:
        app_label = 'courses'
        abstract = dd.is_abstract_model(__name__, 'Line')
        verbose_name = pgettext("singular form", "Activity line")
        verbose_name_plural = pgettext("plural form", 'Activity lines')

    course_area = CourseAreas.field(default='default')
    # default=CourseAreas.get_lazy('default')
    topic = dd.ForeignKey(Topic, blank=True, null=True)
    description = dd.BabelTextField(_("Description"), blank=True)

    every_unit = Recurrencies.field(
        _("Recurrency"),
        default=Recurrencies.as_callable('weekly'),
        blank=True)  # iCal:DURATION
    every = models.IntegerField(_("Repeat every"), default=1)

    event_type = dd.ForeignKey(
        'cal.EventType', null=True, blank=True,
        help_text=_(
            "The type of calendar entries to be generated. "
            "If this is empty, no calendar entries will be generated."))

    fee = dd.ForeignKey(
        'products.Product',
        blank=True, null=True,
        verbose_name=_("Attendance fee"),
        related_name='lines_by_fee')

    guest_role = dd.ForeignKey(
        "cal.GuestRole", blank=True, null=True,
        verbose_name=_("Manage presences as"),
        help_text=_(
            "The default guest role for particpants of "
            "calendar entries for activities in this series. "
            "Leave empty if you don't want any presences management."))

    options_cat = dd.ForeignKey(
        'products.ProductCat',
        verbose_name=_("Options category"),
        related_name="courses_lines_by_options_cat",
        blank=True, null=True)

    fees_cat = dd.ForeignKey(
        'products.ProductCat',
        verbose_name=_("Fees category"),
        related_name="courses_lines_by_fees_cat",
        blank=True, null=True)

    body_template = models.CharField(
        max_length=200,
        verbose_name=_("Body template"),
        blank=True, help_text="The body template to use when "
        "printing a course of this series. "
        "Leave empty to use the site's default.")

    def __str__(self):
        name = dd.babelattr(self, 'name')
        if self.ref:
            return "{0} ({1})".format(self.ref, name)
        return name
        # return "{0} #{1}".format(self._meta.verbose_name, self.pk)

    @dd.chooser()
    def fee_choices(cls, fees_cat):
        Product = rt.models.products.Product
        if not fees_cat:
            return Product.objects.none()
        return Product.objects.filter(cat=fees_cat)

    @dd.chooser(simple_values=True)
    def body_template_choices(cls):
        return dd.plugins.jinja.list_templates(
            '.body.html',
            rt.models.courses.Enrolment.get_template_group(),
            'excerpts')


@dd.python_2_unicode_compatible
class Course(Reservation, Duplicable, Printable):

    class Meta:
        app_label = 'courses'
        abstract = dd.is_abstract_model(__name__, 'Course')
        verbose_name = _("Activity")
        verbose_name_plural = _('Activities')
        # verbose_name = _("Event")
        # verbose_name_plural = _('Events')


    site_field_name = 'room'

    # line = dd.ForeignKey('courses.Line', null=True, blank=True)
    line = dd.ForeignKey('courses.Line')

    teacher = dd.ForeignKey(
        teacher_model,
        verbose_name=teacher_label,
        blank=True, null=True)

    #~ room = dd.ForeignKey(Room,blank=True,null=True)
    slot = dd.ForeignKey(Slot, blank=True, null=True)
    description = dd.BabelTextField(_("Description"), blank=True)
    remark = models.TextField(_("Remark"), blank=True)

    quick_search_fields = 'name line__name line__topic__name'

    state = CourseStates.field(default='draft')

    max_places = models.PositiveIntegerField(
        pgettext("in a course", "Available places"),
        help_text=("Maximum number of participants"),
        blank=True, null=True)

    name = models.CharField(_("Designation"), max_length=100, blank=True)
    enrolments_until = models.DateField(
        _("Enrolments until"), blank=True, null=True)

    print_presence_sheet = PrintPresenceSheet(show_in_bbar=False)
    print_presence_sheet_html = PrintPresenceSheet(
        show_in_bbar=False,
        build_method='weasy2html',
        label=format_lazy(u"{}{}",_("Presence sheet"), _(" (HTML)")))

    @dd.displayfield(_("Print"))
    def print_actions(self, ar):
        if ar is None:
            return ''
        elems = []
        elems.append(ar.instance_action_button(
            self.print_presence_sheet))
        elems.append(ar.instance_action_button(
            self.print_presence_sheet_html))
        return E.p(*join_elems(elems, sep=", "))

    def on_duplicate(self, ar, master):
        self.state = CourseStates.draft
        super(Course, self).on_duplicate(ar, master)


    @classmethod
    def add_param_filter(
            cls, qs, lookup_prefix='', show_exposed=None, **kwargs):
        qs = super(Course, cls).add_param_filter(qs, **kwargs)
        exposed_states = CourseStates.filter(is_exposed=True)
        fkw = dict()
        fkw[lookup_prefix + 'state__in'] = exposed_states
        if show_exposed == dd.YesNo.no:
            qs = qs.exclude(**fkw)
        elif show_exposed == dd.YesNo.yes:
            qs = qs.filter(**fkw)
        return qs
        

    @classmethod
    def get_registrable_fields(cls, site):
        for f in super(Course, cls).get_registrable_fields(site):
            yield f
        yield 'line'
        yield 'teacher'
        yield 'name'
        yield 'enrolments_until'

    def __str__(self):
        if self.name:
            return self.name
        if self.line_id is None:
            line = self._meta.verbose_name
        else:
            line = self.line

        if self.room is None:
            return "%s (%s)" % (line, dd.fds(self.start_date))
        # Note that we cannot use super() with
        # python_2_unicode_compatible
        return "%s (%s %s)" % (line, dd.fds(self.start_date),self.room)

    def get_detail_action(self, ar):
        """Custom :meth:`get_detail_action
        <lino.core.model.Model.get_detail_action>` because the
        detail_layout to use depends on the course's line's
        `course_area`.

        """
        if self.line_id:
            area = self.line.course_area
            if area:
                table = rt.models.resolve(area.courses_table)
                ba = table.detail_action
                ba = ba.action.defining_actor.detail_action
                # if ar is None or ba.get_row_permission(ar, self, None):
                #     return ba
                if ar is None or ba.get_view_permission(ar.get_user().user_type):
                    return ba
                return None
        return super(Course, self).get_detail_action(ar)
            
    def update_cal_from(self, ar):
        """Note: if recurrency is weekly or per_weekday, actual start may be
        later than self.start_date

        """
        # if self.state in (CourseStates.draft, CourseStates.cancelled):
        # if self.state == CourseStates.cancelled:
        #     ar.info("No start date because state is %s", self.state)
        #     return None
        return self.start_date

    def update_cal_event_type(self):
        return self.line.event_type

    def update_cal_summary(self, et, i):
        if self.every_unit == Recurrencies.once:
            return self.name or str(self.line)
        return "%s %s" % (dd.babelattr(et, 'event_label'), i)

    def get_events_user(self):
        """The user of generated events is not the course manager (author) but
        the teacher.

        """
        if self.teacher:
            return self.teacher.get_as_user() or self.user
        return self.user

    def suggest_cal_guests(self, event):
        """Look up enrolments of this course and suggest them as guests."""
        # logger.info("20140314 suggest_guests")
        Enrolment = rt.models.courses.Enrolment
        if self.line is None:
            return
        gr = self.line.guest_role
        if gr is None:
            return
        # fkw = dict(course=self)
        # states = (EnrolmentStates.requested, EnrolmentStates.confirmed)
        # fkw.update(state__in=states)
        qs = Enrolment.objects.filter(course=self).order_by(
            *[f.name for f in Enrolment.quick_search_fields])
        for obj in qs:
            # if obj.is_guest_for(event):
            g = obj.make_guest_for(event)
            if g is not None:
                yield g
                
    def full_clean(self, *args, **kw):
        if self.line_id is not None:
            if self.id is None:
                descs = dd.field2kw(self.line, 'description')
                descs = dd.babelkw('description', **descs)
                for k, v in descs.items():
                    setattr(self, k, v)
            if self.every_unit is None:
                self.every_unit = self.line.every_unit
            if self.every is None:
                self.every = self.line.every
            # if self.room is None:
            #     self.room = self.line.room
        # if self.enrolments_until is None:
        #     self.enrolments_until = self.start_date
        # if self.id is not None:
        #     if self.enrolments_until is None:
        #         qs = self.get_existing_auto_events()
        #         if qs.count():
        #             self.enrolments_until = qs[0].start_date
        super(Course, self).full_clean(*args, **kw)

    def before_auto_event_save(self, event):
        """
        Set room and start_time/end_time for automatic events.
        """
        assert not settings.SITE.loading_from_dump
        assert event.owner == self
        event.course = self
        event.room = self.room
        if self.slot:
            event.start_time = self.slot.start_time
            event.end_time = self.slot.end_time
        else:
            event.start_time = self.start_time
            event.end_time = self.end_time

        super(Course, self).before_auto_event_save(event)

    # @dd.displayfield(_("Info"))
    # def info(self, ar):
    #     if ar is None:
    #         return ''
    #     return ar.obj2html(self)

    def get_overview_elems(self, ar):
        elems = []
        # elems.append(ar.obj2html(self))
        elems.append(self.obj2href(ar))
        if self.teacher_id:
            elems.append(" / ")
            # elems.append(ar.obj2html(self.teacher))
            elems.append(self.teacher.obj2href(ar))
        return elems

    # @classmethod
    # def on_analyze(cls, site):
    #     super(Course, cls).on_analyze(site)
    #     dd.update_field(Course, 'detail_link',
    #                     default=site.models.courses.Course._meta.verbose_name)

    #~ @dd.displayfield(_("Where"))
    #~ def where_text(self,ar):
        # ~ return unicode(self.room) # .company.city or self.company)

    @dd.displayfield(_("Calendar entries"))
    def events_text(self, ar=None):
        return ', '.join([
            day_and_month(e.start_date)
            for e in self.events_by_course().order_by('start_date')])

    def events_by_course(self, **kwargs):
        ct = rt.models.contenttypes.ContentType.objects.get_for_model(
            self.__class__)
        kwargs.update(owner_type=ct, owner_id=self.id)
        return rt.models.cal.Event.objects.filter(**kwargs)

    def get_places_sum(self, today=None, **flt):
        Enrolment = rt.models.courses.Enrolment
        PeriodEvents = rt.models.system.PeriodEvents
        qs = Enrolment.objects.filter(course=self, **flt)
        # see voga.projects.roger.tests.test_max_places
        if today is None:
            rng = DateRangeValue(dd.today(), None)
            qs = PeriodEvents.active.add_filter(qs, rng)
        else:
            qs = PeriodEvents.active.add_filter(qs, today)
        # logger.info("20160502 %s", qs.query)
        res = qs.aggregate(models.Sum('places'))
        # logger.info("20140819 %s", res)
        return res['places__sum'] or 0

    def get_free_places(self, today=None):
        if not self.max_places:
            return None  # _("Unlimited")
        return self.max_places - self.get_used_places(today)

    def get_used_places(self, today=None):
        states = EnrolmentStates.filter(uses_a_place=True)
        return self.get_places_sum(today, state__in=states)

    # @dd.displayfield(_("Free places"), max_length=5)
    @dd.virtualfield(models.IntegerField(_("Free places")))
    def free_places(self, ar=None):
        # if not self.max_places:
        #     return None  # _("Unlimited")
        return self.get_free_places()

    @dd.virtualfield(models.IntegerField(_("Requested")))
    def requested(self, ar):
        return self.get_places_sum(state=EnrolmentStates.requested)
        # pv = dict(start_date=dd.today())
        # pv.update(state=EnrolmentStates.requested)
        # return rt.models.courses.EnrolmentsByCourse.request(
        #     self, param_values=pv)

    @dd.virtualfield(models.IntegerField(_("Confirmed")))
    def confirmed(self, ar):
        return self.get_places_sum(state=EnrolmentStates.confirmed)
        # pv = dict(start_date=dd.today())
        # pv.update(state=EnrolmentStates.confirmed)
        # return rt.models.courses.EnrolmentsByCourse.request(
        #     self, param_values=pv)

    @dd.virtualfield(models.IntegerField(_("Trying")))
    def trying(self, ar):
        return self.get_places_sum(state=EnrolmentStates.trying)
    
    @dd.requestfield(_("Enrolments"))
    def enrolments(self, ar):
        return self.get_enrolments(start_date=dd.today())

    def get_enrolments(self, **pv):
        # pv = dict(start_date=sd, end_date=dd.today())
        return rt.models.courses.EnrolmentsByCourse.request(
            self, param_values=pv)

    @dd.virtualfield(dd.HtmlBox(_("Presences")))
    def presences_box(self, ar):
        # not finished
        if ar is None:
            return ''
        pv = ar.param_values
        # if not pv.start_date or not pv.end_date:
        #     return ''
        events = self.events_by_course().order_by('start_date')
        events = rt.models.system.PeriodEvents.started.add_filter(events, pv)
        return "TODO: copy logic from presence_sheet.wk.html"



# customize fields coming from mixins to override their inherited
# default verbose_names
dd.update_field(Course, 'every_unit', default=models.NOT_PROVIDED)
dd.update_field(Course, 'every', default=models.NOT_PROVIDED)


if FILL_EVENT_GUESTS:

    @dd.receiver(dd.post_save, sender=cal.Event,
                 dispatch_uid="fill_event_guests_from_course")
    def fill_event_guests_from_course(sender=None, instance=None, **kw):
        #~ logger.info("20130528 fill_event_guests_from_course")
        if settings.SITE.loading_from_dump:
            return
        event = instance
        if event.is_user_modified():
            return
        if event.is_fixed_state():
            return
        if not isinstance(event.owner, Course):
            return
        course = event.owner
        if event.guest_set.count() > 0:
            return
        for e in course.enrolment_set.all():
            cal.Guest(partner=e.pupil, event=event).save()


# ENROLMENT


class ConfirmedSubmitInsert(dd.SubmitInsert):
    def run_from_ui(self, ar, **kw):
        obj = ar.create_instance_from_request()
        msg = obj.get_confirm_veto(ar)
        if msg is None:
            obj.state = EnrolmentStates.confirmed
        self.save_new_instance(ar, obj)
        ar.set_response(close_window=True)


@dd.python_2_unicode_compatible
class Enrolment(UserAuthored, Certifiable, DateRange):
    # invoiceable_date_field = 'request_date'
    workflow_state_field = 'state'
    allow_cascaded_copy = 'course'
    manager_roles_required = dd.login_required()

    class Meta:
        app_label = 'courses'
        abstract = dd.is_abstract_model(__name__, 'Enrolment')
        verbose_name = _("Enrolment")
        verbose_name_plural = _('Enrolments')
        unique_together = ('course', 'pupil')

    course_area = CourseAreas.field(blank=True, editable=False)

    quick_search_fields = pupil_name_fields

    #~ teacher = dd.ForeignKey(Teacher)
    course = dd.ForeignKey('courses.Course')
    pupil = dd.ForeignKey(
        pupil_model, related_name="enrolments_by_pupil")
    request_date = models.DateField(
        _("Date of request"), default=dd.today)
    state = EnrolmentStates.field(default='requested')
    places = models.PositiveIntegerField(
        pgettext("in a course", "Places used"),
        help_text=("The number of participants in this enrolment."),
        default=1)

    option = dd.ForeignKey(
        'products.Product', verbose_name=_("Option"),
        related_name='enrolments_by_option',
        blank=True, null=True)

    remark = models.CharField(_("Remark"), max_length=200, blank=True)
    confirmation_details = dd.RichTextField(
        _("Confirmation details"), blank=True,
        # format="html"
    )

    submit_insert = ConfirmedSubmitInsert()

    @dd.chooser()
    def course_choices(cls, course_area, request_date):
        # dd.logger.info("20160714 course_choices %s", course_area)
        if request_date is None:
            request_date = dd.today()
        flt = Q(enrolments_until__isnull=True)
        flt |= Q(enrolments_until__gte=request_date)
        qs = rt.models.courses.Course.objects.filter(flt)
        flt = Q(max_date__isnull=True)
        flt |= Q(max_date__gte=request_date)
        qs = qs.filter(flt)
        if course_area:
            qs = qs.filter(line__course_area=course_area)
        enrollable_states = CourseStates.filter(is_exposed=True)
        qs = qs.filter(state__in=enrollable_states)
        return qs

    @dd.chooser()
    def pupil_choices(cls, course):
        Pupil = dd.resolve_model(pupil_model)
        return Pupil.objects.all()

    def create_pupil_choice(self, text):
        """
        Called when an unknown pupil name was given.
        Try to auto-create it.
        """
        Pupil = dd.resolve_model(pupil_model)
        kw = parse_name(text)
        if len(kw) != 2:
            raise ValidationError(
                "Cannot find first and last names in %r to \
                auto-create pupil", text)
        p = Pupil(**kw)
        p.full_clean()
        p.save()
        return p

    @dd.chooser()
    def option_choices(cls, course):
        if not course.line or not course.line.options_cat:
            return []
        Product = rt.models.products.Product
        return Product.objects.filter(cat=course.line.options_cat)

    def get_overview_elems(self, ar):
        if self.course_id:
            return [self.course.obj2href(ar)]
        return [self.obj2href(ar)]

    def get_confirm_veto(self, ar):
        """Called from :class:`ConfirmEnrolment
        <lino_xl.lib.courses.workflows.ConfirmEnrolment>`.  If this
        returns something else than `None`, then the enrolment won't
        be confirmed and the return value will be displayed to the
        user.

        """
        if self.course_id is None or self.course.max_places is None:
            return  # no veto. unlimited places.
        free = self.course.get_free_places(self.request_date)
        if free <= 0:
            return _("No places left in %s") % self.course
        #~ return _("Confirmation not implemented")

    def get_guest_role(self):
        if self.course.line:
            return self.course.line.guest_role
    
    def make_guest_for(self, event):
        if not self.state.uses_a_place:
            return 
        gr = self.get_guest_role()
        if gr is not None:
            return rt.models.cal.Guest(
                        event=event,
                        partner=self.pupil,
                        role=gr)

    # def is_guest_for(self, event):
    #     """Return `True` if the pupil of this enrolment should be invited to
    #     the given event.

    #     """
    #     return self.state.uses_a_place

    def full_clean(self, *args, **kwargs):
        if self.course_id and self.course.line:
            self.course_area = self.course.line.course_area
        super(Enrolment, self).full_clean(*args, **kwargs)

    def get_print_templates(self, bm, action):
        return [self.state.name + bm.template_ext]

    def __str__(self):
        return "%s / %s" % (self.course, self.pupil)

    def get_print_language(self):
        return self.pupil.language

    def get_body_template(self):
        """Overrides :meth:`lino.core.model.Model.get_body_template`."""
        return self.course.line.body_template

    def get_excerpt_title(self):
        return self.course.line.get_excerpt_title()

    @dd.virtualfield(dd.HtmlBox(_("Participant")))
    def pupil_info(self, ar):
        txt = self.pupil.get_full_name(nominative=True)
        if ar is None:
            elems = [txt]
        else:
            elems = [ar.obj2html(self.pupil, txt)]
        elems += [', ']
        elems += join_elems(
            list(self.pupil.address_location_lines()),
            sep=', ')
        return E.p(*elems)

dd.update_field(
    Enrolment, 'overview',
    verbose_name=Course._meta.verbose_name)    

dd.update_field(Enrolment, 'course', blank=True)

@dd.receiver(dd.post_startup)
def setup_memo_commands(sender=None, **kwargs):
    # See :doc:`/specs/memo`

    Course = sender.models.courses.Course

    def cmd(parser, s):

        pk = s
        txt = None

        ar = parser.context['ar']
        kw = dict()
        # dd.logger.info("20161019 %s", ar.renderer)
        pk = int(pk)
        obj = Course.objects.get(pk=pk)
        # try:
        # except model.DoesNotExist:
        #     return "[{} {}]".format(name, s)
        if txt is None:
            txt = "{0}".format(obj.name)
            kw.update(title=obj.name)
        e = ar.obj2html(obj, txt, **kw)
        # return str(ar)
        return tostring(e)

    sender.kernel.memo_parser.register_django_model(
        'course', Course,
        cmd=cmd,
        # title=lambda obj: obj.name
    )

