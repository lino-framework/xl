# -*- coding: UTF-8 -*-
# Copyright 2014-2021 Rumma & Ko Ltd
# License: GNU Affero General Public License v3 (see file COPYING for details)

from django.db import models
from django.conf import settings
from django.utils.translation import gettext_lazy as _
from django.utils.text import format_lazy

from lino_xl.lib.contacts.roles import ContactsStaff, ContactsUser
from lino_xl.lib.appypod.mixins import PrintLabelsAction
from lino.modlib.printing.mixins import Printable
from lino.utils.mldbc.mixins import BabelDesignated
from lino.core.utils import comma
from etgen.html import E, join_elems

from lino.api import dd
from lino import mixins

if dd.is_installed('lists'):
    partner_model = dd.plugins.lists.partner_model
else:
    partner_model = None


from lino.modlib.printing.mixins import DirectPrintAction
from lino.mixins.periods import Monthly

class PrintMembers(DirectPrintAction):
    # combo_group = "creacert"
    label = _("Members")
    tplname = "list_members"
    build_method = "weasy2pdf"
    icon_name = None
    show_in_bbar = False
    # parameters = Monthly(
    #     show_remarks=models.BooleanField(
    #         _("Show remarks"), default=False),
    #     show_states=models.BooleanField(
    #         _("Show states"), default=True))
    # params_layout = """
    # start_date
    # end_date
    # show_remarks
    # show_states
    # """
    # keep_user_values = True



#class ListType(mixins.BabelNamed):
class ListType(BabelDesignated):

    """Represents a possible choice for the `list_type` field of a
    :class:`List`.

    """

    class Meta:
        app_label = 'lists'
        abstract = dd.is_abstract_model(__name__, 'ListType')
        verbose_name = _("List Type")
        verbose_name_plural = _("List Types")


class ListTypes(dd.Table):
    required_roles = dd.login_required(ContactsStaff)
    model = 'lists.ListType'
    column_names = 'designation *'


#class List(mixins.BabelNamed, mixins.Referrable):
class List(BabelDesignated, mixins.Referrable, Printable):

    class Meta:
        app_label = 'lists'
        abstract = dd.is_abstract_model(__name__, 'List')
        verbose_name = _("Partner List")
        verbose_name_plural = _("Partner Lists")

    list_type = dd.ForeignKey('lists.ListType', blank=True, null=True)
    remarks = models.TextField(_("Remarks"), blank=True)

    print_labels = PrintLabelsAction()
    print_members = PrintMembers()
    print_members_html = PrintMembers(
        build_method='weasy2html',
        label=format_lazy(u"{}{}",_("Members"), _(" (HTML)")))

    @dd.displayfield(_("Print"))
    def print_actions(self, ar):
        if ar is None:
            return ''
        elems = []
        elems.append(ar.instance_action_button(
            self.print_labels))
        elems.append(ar.instance_action_button(
            self.print_members))
        elems.append(ar.instance_action_button(
            self.print_members_html))
        return E.p(*join_elems(elems, sep=", "))

    def get_overview_elems(self, ar):
        return [self.obj2href(ar)]


class Lists(dd.Table):
    required_roles = dd.login_required(ContactsUser)
    model = 'lists.List'
    # column_names = 'ref designation list_type *'
    column_names = 'ref overview list_type *'
    order_by = ['ref']

    insert_layout = dd.InsertLayout("""
    ref list_type
    designation
    remarks
    """, window_size=(60, 12))

    detail_layout = dd.DetailLayout("""
    id ref list_type print_actions
    designation
    remarks
    MembersByList
    """)


class Member(mixins.Sequenced):

    class Meta:
        app_label = 'lists'
        abstract = dd.is_abstract_model(__name__, 'Member')
        verbose_name = _("List membership")
        verbose_name_plural = _("List memberships")

    quick_search_fields = "partner__name remark"
    show_in_site_search = False
    allow_cascaded_delete = "list partner"

    list = dd.ForeignKey('lists.List', related_name="members")
    partner = dd.ForeignKey(partner_model, related_name="list_memberships")
    remark = models.CharField(_("Remark"), max_length=200, blank=True)

    def __str__(self):
        return _("{} is member of {}").format(self.partner, self.list)


class Members(dd.Table):
    required_roles = dd.login_required(ContactsUser)
    model = 'lists.Member'
    detail_layout = dd.DetailLayout("""
    list
    partner
    remark
    """, window_size=(60, 'auto'))


class MembersByList(Members):
    label = _("Members")
    master_key = 'list'
    order_by = ['seqno']
    if dd.is_installed("phones"):
        column_names = "seqno partner remark workflow_buttons partner__address_column partner__contact_details *"
    else:
        column_names = "seqno partner remark workflow_buttons partner__address_column partner__email partner__gsm *"


class MembersByPartner(Members):
    master_key = 'partner'
    column_names = "list remark *"
    order_by = ['list__ref']
    display_mode = "summary"
    summary_sep = comma
    insert_layout = """
    list
    remark
    """

    @classmethod
    def summary_row(cls, ar, obj, **kw):
        yield ar.obj2html(obj, str(obj.list))
        if obj.remark:
            yield obj.remark



class AllMembers(Members):
    required_roles = dd.login_required(ContactsStaff)
