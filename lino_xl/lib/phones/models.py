# -*- coding: UTF-8 -*-
# Copyright 2017 Rumma & Ko Ltd
#
# License: BSD (see file COPYING for details)


from __future__ import unicode_literals
from __future__ import print_function

from django.db import models

from etgen.html import E
from lino.utils import join_elems
from lino.core.diff import ChangeWatcher
from lino.modlib.checkdata.choicelists import Checker

from lino.api import dd, rt, _
from lino.core.roles import SiteStaff

from .choicelists import ContactDetailTypes
from .mixins import ContactDetailsOwner


@dd.python_2_unicode_compatible
class ContactDetail(dd.Model):
    class Meta:
        app_label = 'phones'
        verbose_name = _("Contact detail")
        verbose_name_plural = _("Contact details")

    detail_type = ContactDetailTypes.field(
        default=ContactDetailTypes.as_callable('email'))
    partner = dd.ForeignKey(
        dd.plugins.phones.partner_model,
        related_name='phones_by_partner')
    value = dd.CharField(_("Value"), max_length=200, blank=True)
    remark = dd.CharField(_("Remark"), max_length=200, blank=True)
    primary = models.BooleanField(_("Primary"), default=False)
    end_date = models.DateField(_("Until"), blank=True, null=True)

    allow_cascaded_delete = ['partner']

    def __str__(self):
        return self.detail_type.format(self.value)

    def full_clean(self):
        super(ContactDetail, self).full_clean()
        self.detail_type.validate(self.value)

    def after_ui_save(self, ar, cw):
        super(ContactDetail, self).after_ui_save(ar, cw)
        mi = self.partner
        if mi is None:
            return
        if self.primary and self.detail_type:
            for o in mi.phones_by_partner.exclude(id=self.id).filter(
                    detail_type=self.detail_type):
                if o.primary:
                    o.primary = False
                    o.save()
                    ar.set_response(refresh_all=True)
        k = self.detail_type.field_name
        if k:
            watcher = ChangeWatcher(mi)
            setattr(mi, k, self.value)
            watcher.send_update(ar)
            mi.save()

    @classmethod
    def get_simple_parameters(cls):
        return ['partner', 'detail_type']

@dd.receiver(dd.pre_ui_delete, sender=ContactDetail)
def clear_partner_on_delete(sender=None, request=None, **kw):
    self = sender
    mi = self.partner
    if mi:
        mi.propagate_contact_detail(self.detail_type)


class ContactDetails(dd.Table):
    model = 'phones.ContactDetail'
    required_roles = dd.login_required(SiteStaff)
    column_names = (
        "value:30 detail_type:10 remark:10 partner id "
        "primary *")
    insert_layout = """
    detail_type 
    value
    remark
    """
    detail_layout = dd.DetailLayout("""
    partner
    detail_type 
    value
    remark
    """, window_size=(60, 'auto'))


class ContactDetailsByPartner(ContactDetails):
    required_roles = dd.login_required()
    master_key = 'partner'
    column_names = 'detail_type:10 value:30 primary:5 end_date remark:10 *'
    label = _("Contact details")
    auto_fit_column_widths = True
    stay_in_grid = True
    window_size = (80, 20)

    display_mode = 'summary'

    @classmethod
    def get_table_summary(self, obj, ar):
        sar = self.request_from(ar, master_instance=obj)
        items = [o.detail_type.as_html(o, sar)
                 for o in sar if not o.end_date]
            
        html = []
        if len(items) == 0:
            html += _("No contact details")
        else:
            html += join_elems(items, sep=', ')
            
        ins = self.insert_action.request_from(sar)
        if ins.get_permission():
            # kw = dict(label=u"⊕") # 2295 circled plus
            # kw.update(icon_name=None)
            # # kw.update(
            # #     style="text-decoration:none; font-size:120%;")  
            # btn = ins.ar2button(**kw)
            btn = ins.ar2button()
                
            # if len(items) > 0:
            #     html.append(E.br())
            html.append(' ')
            html.append(btn)

        if True:
            html.append(' ')
            html.append(sar.as_button(icon_name="wrench"))  # GEAR
            # html.append(sar.as_button(u"⚙"))  # GEAR
            # html.append(sar.as_button(
            #     u"⚙", style="text-decoration:none; font-size:140%;"))  # GEAR
        else:
            html.append(E.br())
            html.append(sar.as_button(_("Manage contact details")))
            
        return E.p(*html)
    


class ContactDetailsOwnerChecker(Checker):
    verbose_name = _("Check for mismatches between contact details and owner")
    model = ContactDetailsOwner
    msg_mismatch = _("Field differs from primary item")
    msg_empty = _("Field is empty but primary item exists")
    msg_missing = _("Missing primary item")

    def get_checkdata_problems(self, obj, fix=False):
        # dd.logger.info("20171013 Checking {}", obj)
        ContactDetailTypes = rt.models.phones.ContactDetailTypes
        ContactDetail = rt.models.phones.ContactDetail
        for cdt in ContactDetailTypes.get_list_items():
            k = cdt.field_name
            if k:
                value = getattr(obj, k)
                kw = dict(partner=obj, primary=True, detail_type=cdt)
                try:
                    cd = ContactDetail.objects.get(**kw)
                    if value:
                        if cd.value != value:
                            yield (False, self.msg_mismatch)
                    else:
                        yield (False, self.msg_empty)
                except ContactDetail.DoesNotExist:
                    if value:
                        yield (True, self.msg_missing)
                        if fix:
                            kw.update(value=value)
                            cd = ContactDetail(**kw)
                            cd.save()

ContactDetailsOwnerChecker.activate()
