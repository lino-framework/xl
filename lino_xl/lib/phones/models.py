# -*- coding: UTF-8 -*-
# Copyright 2017 Luc Saffre
#
# License: BSD (see file COPYING for details)


from __future__ import unicode_literals
from __future__ import print_function

from django.db import models
from django.utils.translation import ugettext_lazy as _

from lino.utils.xmlgen.html import E
from lino.utils import join_elems
from lino.core.diff import ChangeWatcher

from lino.api import dd
from lino.core.roles import SiteStaff

from .choicelists import ContactDetailTypes


@dd.python_2_unicode_compatible
class ContactDetail(dd.Model):
    class Meta:
        app_label = 'phones'
        verbose_name = _("Contact detail")
        verbose_name_plural = _("Contact details")

    detail_type = ContactDetailTypes.field(
        default=ContactDetailTypes.email.as_callable)
    partner = dd.ForeignKey(
        dd.plugins.phones.partner_model,
        related_name='phones_by_partner')
    value = dd.CharField(_("Value"), max_length=200, blank=True)
    remark = dd.CharField(_("Remark"), max_length=200, blank=True)
    primary = models.BooleanField(_("Primary"), default=False)

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
        if self.primary:
            for o in mi.phones_by_partner.exclude(id=self.id):
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
    required_roles = dd.login_required(dd.SiteStaff)
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
    column_names = 'detail_type:10 value:30 primary:5 remark:10 *'
    label = _("Contact details")
    auto_fit_column_widths = True
    stay_in_grid = True
    window_size = (80, 20)

    slave_grid_format = 'summary'

    @classmethod
    def get_slave_summary(self, obj, ar):
        sar = self.request_from(ar, master_instance=obj)
        html = []
        items = [o.detail_type.as_html(o, sar) for o in sar]
            
        if len(items) > 0:
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

        # html.append(' ')
        html.append(E.br())
        html.append(sar.as_button(_("Manage contact details")))
        # html.append(sar.as_button(u"⚙"))  # GEAR
        # html.append(sar.as_button(icon_name="wrench"))  # GEAR
        # html.append(sar.as_button(
        #     u"⚙", style="text-decoration:none; font-size:140%;"))  # GEAR
            
        return E.p(*html)
    


