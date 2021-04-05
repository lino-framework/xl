# -*- coding: UTF-8 -*-
# Copyright 2014-2020 Rumma & Ko Ltd
# License: GNU Affero General Public License v3 (see file COPYING for details)

from django.db.models import Q
from lino.api import dd, _

from lino.modlib.uploads.models import *
from lino_xl.lib.contacts.mixins import ContactRelated
from lino_xl.lib.cal.utils import update_reminder
from lino_xl.lib.cal.choicelists import Recurrencies
from lino_xl.lib.contacts.roles import ContactsUser
from lino_xl.lib.clients.mixins import ClientBase

# add = UploadAreas.add_item
# add('10', _("Job search uploads"), 'job_search')
# add('20', _("Medical uploads"), 'medical')
# add('30', _("Career uploads"), 'career')


class UploadType(UploadType):
    """Extends the library model by adding `warn_expiry` info.

    """
    warn_expiry_unit = Recurrencies.field(
        _("Expiry warning (unit)"),
        default=Recurrencies.as_callable('monthly'),
        blank=True)  # iCal:DURATION
    warn_expiry_value = models.IntegerField(
        _("Expiry warning (value)"),
        default=2)

# dd.update_field(
#     'uploads.UploadType', 'upload_area', default=UploadAreas.job_search.as_callable)


class UploadTypes(UploadTypes):
    column_names = "id name wanted upload_area max_number \
    warn_expiry_unit warn_expiry_value shortcut *"

    detail_layout = """
    id upload_area shortcut
    name
    warn_expiry_unit warn_expiry_value wanted max_number
    uploads.UploadsByType
    """

    insert_layout = """
    upload_area
    name
    warn_expiry_unit warn_expiry_value
    # company contact_person contact_role
    """


class Upload(Upload, mixins.ProjectRelated, ContactRelated,
             mixins.DateRange):
    """Extends the library model by adding the `ContactRelated`,
    `ProjectRelated` and `DateRange` mixins and two fields.

    .. attribute:: remark

        A remark about this document.

    .. attribute:: needed

        Whether this particular upload is a needed document. Default value
        is `True` if the new Upload has an UploadType with a nonempty
        `warn_expiry_unit`.

    """
    # valid_from = models.DateField(_("Valid from"), blank=True, null=True)
    # valid_until = models.DateField(_("Valid until"), blank=True, null=True)

    remark = models.TextField(_("Remark"), blank=True)
    needed = models.BooleanField(_("Needed"), default=True)

    @classmethod
    def setup_parameters(cls, params):
        super(Upload, cls).setup_parameters(params)
        params.update(coached_by=dd.ForeignKey(
            'users.User',
            blank=True, null=True,
            verbose_name=_("Coached by"),
            help_text=_("Show only uploads for clients coached by this user.")))
        # if issubclass(settings.SITE.project_model, ClientBase):
        #     params.update(coached_by=dd.ForeignKey(
        #         'users.User',
        #         blank=True, null=True,
        #         verbose_name=_("Coached by"),
        #         help_text=_("Show only uploads for clients coached by this user.")))
        # else:
        #     params.update(coached_by=dd.DummyField())

    @classmethod
    def get_simple_parameters(cls):
        lst = list(super(Upload, cls).get_simple_parameters())
        lst.append('coached_by')
        return lst

    @classmethod
    def add_param_filter(cls, qs, lookup_prefix='', coached_by=None, **kwargs):
        if issubclass(settings.SITE.project_model, ClientBase):
            # print("20200619 coached_by={}, kw={}".format(coached_by, kwargs))
            if coached_by:
                qs = settings.SITE.project_model.add_param_filter(qs, "project__", coached_by=coached_by)
                # # MyExpiringUploads wants only needed uploads
                # but its irritating to link the condition to coached_by
                # qs = qs.filter(needed=True)
        return super(Upload, cls).add_param_filter(qs, lookup_prefix, **kwargs)

    def on_create(self, ar):
        super(Upload, self).on_create(ar)
        if self.type and self.type.warn_expiry_unit:
            self.needed = True
        else:
            self.needed = False

    def save(self, *args, **kw):
        super(Upload, self).save(*args, **kw)
        self.update_reminders()

    def update_reminders(self):
        """Overrides :meth:`lino.core.model.Model.update_reminders`.

        """
        ut = self.type
        if not ut or not ut.warn_expiry_unit:
            return
        if not self.needed:
            return
        update_reminder(
            1, self, self.user,
            self.end_date,
            _("%s expires") % str(ut),
            ut.warn_expiry_value,
            ut.warn_expiry_unit)


dd.update_field(
    Upload, 'company', verbose_name=_("Issued by (Organization)"))
dd.update_field(
    Upload, 'contact_person',
    verbose_name=_("Issued by (Person)"))
dd.update_field(Upload, 'start_date', verbose_name=_("Valid from"))
dd.update_field(Upload, 'end_date', verbose_name=_("Valid until"))
# dd.update_field(
#     Upload, 'upload_area', default=UploadAreas.job_search.as_callable)


class UploadDetail(dd.DetailLayout):

    main = """
    user project id
    type description start_date end_date needed
    company contact_person contact_role
    file owner
    remark cal.TasksByController
    """

LibraryUploads = Uploads


class Uploads(Uploads):
    column_names = 'user project type file start_date end_date needed ' \
                   'description_link *'

    detail_layout = UploadDetail()

    insert_layout = """
    file
    type project
    start_date end_date needed
    description
    """

    parameters = mixins.ObservedDateRange(
        # puser=dd.ForeignKey(
        #     'users.User', blank=True, null=True,
        #     verbose_name=_("Uploaded by")),
        upload_type=dd.ForeignKey(
            'uploads.UploadType', blank=True, null=True),
        observed_event=dd.PeriodEvents.field(
            _("Validity"),
            blank=True, default=dd.PeriodEvents.as_callable('active')))
    params_layout = "observed_event:20 start_date end_date \
    coached_by user upload_type"

    auto_fit_column_widths = True

    @classmethod
    def get_request_queryset(cls, ar, **kwargs):
        # (why was this?) use inherited method from grandparent (not
        # direct parent)
        # qs = super(LibraryUploads, cls).get_request_queryset(ar)
        qs = super(Uploads, cls).get_request_queryset(ar, **kwargs)
        pv = ar.param_values

        ce = pv.observed_event
        if ce is not None:
            qs = ce.add_filter(qs, pv)

        return qs

    @classmethod
    def get_title_tags(self, ar):
        for t in super(Uploads, self).get_title_tags(ar):
            yield t

        pv = ar.param_values

        if pv.observed_event:
            yield str(pv.observed_event)

        if pv.coached_by:
            yield str(self.parameters['coached_by'].verbose_name) + \
                ' ' + str(pv.coached_by)

        if pv.user:
            yield str(self.parameters['user'].verbose_name) + \
                ' ' + str(pv.user)


class UploadsByType(Uploads, UploadsByType):
    pass


class MyUploads(My, Uploads):
    required_roles = dd.login_required((OfficeUser, OfficeOperator))
    column_names = "id project type start_date end_date \
    needed description_link file *"


class MyExpiringUploads(MyUploads):
    "Expiring uploads for client coached by me"
    required_roles = dd.login_required((OfficeUser, OfficeOperator))
    label = _("My expiring upload files")
    help_text = _("Show needed files whose validity expires soon")
    column_names = "project type description_link user \
    start_date end_date needed *"
    order_by = ['end_date']
    filter = Q(needed=True)

    @classmethod
    def param_defaults(self, ar, **kw):
        kw = super(MyExpiringUploads, self).param_defaults(ar, **kw)
        if issubclass(settings.SITE.project_model, ClientBase):
            kw['user'] = None
            kw['coached_by'] = ar.get_user()
        kw.update(observed_event=dd.PeriodEvents.ended)
        kw.update(start_date=dd.today(dd.plugins.uploads.expiring_start))
        kw.update(end_date=dd.today(dd.plugins.uploads.expiring_end))
        return kw

class AreaUploads(Uploads, AreaUploads):
    pass


class UploadsByController(Uploads, UploadsByController):
    insert_layout = """
    file
    type end_date needed
    description
    """


class UploadsByProject(AreaUploads, UploadsByController):
    # master = dd.plugins.clients.client_model  # 'pcsw.Client'
    master = settings.SITE.project_model
    master_key = 'project'
    column_names = "type end_date needed description_link user *"
    required_roles = dd.login_required(ContactsUser, (OfficeUser, OfficeOperator))
    # auto_fit_column_widths = True
    # debug_sql = "20140519"

    # insert_layout = """
    # file
    # type end_date needed
    # description
    # """

    @classmethod
    def create_instance(self, ar, **kw):
        obj = super(UploadsByProject, self).create_instance(ar, **kw)
        obj.owner = obj.project
        return obj

    # 20200731 uploads with an end_date before today were being filtered from
    # the summary. i don't remember why it is here. deactivated this because it
    # disturbs in avanti.
    # @classmethod
    # def format_row_in_slave_summary(self, ar, obj):
    #     if obj.end_date and obj.end_date < settings.SITE.today():
    #         return None
    #     return super(UploadsByProject, self).format_row_in_slave_summary(
    #         ar, obj)
