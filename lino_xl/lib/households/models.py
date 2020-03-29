# -*- coding: UTF-8 -*-
# Copyright 2012-2019 Rumma & Ko Ltd
# License: BSD (see file COPYING for details)

import six

import logging ; logger = logging.getLogger(__name__)

from django.db import models
from django.conf import settings

from lino.api import dd, rt, _, gettext
from lino import mixins

from lino.utils import join_words, join_elems
from etgen.html import E
from lino_xl.lib.contacts.roles import ContactsUser, ContactsStaff

from .choicelists import MemberRoles, MemberDependencies

contacts = dd.resolve_app('contacts')

config = dd.plugins.households

from .choicelists import child_roles, parent_roles

class Type(mixins.BabelNamed):
    class Meta:
        app_label = 'households'
        verbose_name = _("Household Type")
        verbose_name_plural = _("Household Types")


class Types(dd.Table):
    required_roles = dd.login_required(ContactsStaff)
    model = 'households.Type'
    column_names = "id name *"
    detail_layout = """
    name
    HouseholdsByType
    """


class PopulateMembers(dd.Action):
    # populate household members from data in humanlinks
    # show_in_bbar = False
    custom_handler = True
    label = _("Populate")
    icon_name = 'lightning'

    def run_from_ui(self, ar, **kw):
        if not dd.is_installed('humanlinks'):
            return
        today = dd.today()
        n = 0
        Member = rt.models.households.Member
        for hh in ar.selected_rows:
            known_children = set()
            for mbr in hh.member_set.filter(role__in=child_roles):
                if mbr.person:
                    known_children.add(mbr.person.id)

            new_children = dict()
            for parent in hh.member_set.filter(role__in=parent_roles):
                for childlnk in parent.person.humanlinks_children.all():
                    child = childlnk.child
                    if not child.id in known_children:
                        age = child.get_age(today)
                        if age is None or age <= dd.plugins.households.adult_age:
                            childmbr = new_children.get(child.id, None)
                            if childmbr is None:
                                cr = MemberRoles.child
                                # if parent.role == MemberRoles.head:
                                #     cr = MemberRoles.child_of_head
                                # else:
                                #     cr = MemberRoles.child_of_partner
                                childmbr = Member(
                                    household=hh,
                                    person=child,
                                    dependency=MemberDependencies.full,
                                    role=cr)
                                new_children[child.id] = childmbr
                                n += 1
                            else:
                                childmbr.role = MemberRoles.child
                            # if parent.role == MemberRoles.head:
                            #     childmbr.dependency = MemberDependencies.full
                            childmbr.full_clean()
                            childmbr.save()

        ar.success(
            _("Added %d children.") % n, refresh_all=True)



class Household(contacts.Partner):
    class Meta:
        app_label = 'households'
        abstract = dd.is_abstract_model(__name__, 'Household')
        verbose_name = _("Household")
        verbose_name_plural = _("Households")

    type = dd.ForeignKey(Type, blank=True, null=True)
    # head = dd.ForeignKey('contacts.Person', verbose_name=_("Chef")),

    populate_members = PopulateMembers()

    #~ dummy = models.CharField(max_length=1,blank=True)
    # workaround for https://code.djangoproject.com/ticket/13864

    def after_ui_save(self, ar, cw):
        super(Household, self).after_ui_save(ar, cw)
        self.populate_members.run_from_code(ar)

    def add_member(self, person, role=None):
        mbr = rt.models.households.Member(
            household=self, person=person, role=role)
        mbr.full_clean()
        mbr.save()
        return mbr

    def members_by_role(self, rolename):
        role = MemberRoles.get_by_name(rolename)
        # return rt.models.households.Member.objects.filter(
        #     household=self, role=role)
        return self.member_set.filter(role=role)

    def get_full_name(self, salutation=True, **salutation_options):
        """Overrides
        :meth:`lino_xl.lib.contacts.models.Partner.get_full_name`.

        """
        return join_words(self.prefix, self.name)
    full_name = property(get_full_name)

    def __str__(self):
        if self.type:
            return "{} ({})".format(self.get_full_name(), self.type)
        # return six.text_type(self.get_full_name())
        return str(self.get_full_name())

    def get_name_elems(self, ar):
        elems = []
        if self.prefix:
            elems += [self.prefix, ' ']
        elems += [E.b(self.name)]
        return elems

    @classmethod
    def create_household(cls, ar, head, partner, type):
        name = head.last_name
        prefix = head.first_name
        if partner:
            name += '-' + partner.last_name
            prefix += ' & ' + partner.first_name
        hh = cls(type=type, name=name, prefix=prefix)
        hh.full_clean()
        hh.save()
        # TODO: see 20140426
        # hh.add_member(head, Role.objects.get(pk=1))
        if head is not None:
            hh.add_member(head, MemberRoles.head)
        if partner is not None:
            hh.add_member(partner, MemberRoles.partner)
        hh.after_ui_save(ar, None)
        return hh


class HouseholdDetail(dd.DetailLayout):

    if dd.is_installed('addresses') and dd.is_installed('phones'):
        main = """
        address_box
        bottom_box
        """
        address_box = "overview:50 data_box:30"
        data_box = """
        type
        prefix
        name
        language id
        """
    else:
        main = """
        type prefix name language:10 id
        address_box
        bottom_box
        """

        address_box = "box3 contact_box"

        box3 = """
        country region
        city zip_code:10
        street_prefix street:25 street_no street_box
        addr2:40
        """

        contact_box = """
        phone
        gsm
        email:40
        url
        """

    bottom_box = "#remarks households.MembersByHousehold"


class Households(contacts.Partners):
    model = 'households.Household'
    required_roles = dd.login_required(ContactsUser)
    order_by = ["name"]
    column_names = "name type address_column *"
    detail_layout = 'households.HouseholdDetail'
    insert_layout = """
    type name
    language
    """


class HouseholdsByType(Households):
    #~ label = _("Households")
    master_key = 'type'
    #~ column_names = 'person role *'
    insert_layout = """
    name
    language
    """


# class Role(mixins.BabelNamed):
#     """
#     The role of a :class:`Member` in a :class:`Household`.
#     """
#     class Meta:
#         verbose_name = _("Household Role")
#         verbose_name_plural = _("Household Roles")

#     name_giving = models.BooleanField(
#         _("name-giving"),
#         default=False,
#         help_text=(
#             "Whether this role is name-giving for its household. "
#             "The name of a Household is computed by joining the "
#             "`Last Name` of all name-giving members with a dash (`-`)."
#         ))


# class Roles(dd.Table):
#     model = Role
#     required = dd.login_required(user_level='admin')
#     detail_layout = """
#     name name_giving
#     #male
#     #female
#     MembersByRole
#     """



class Member(mixins.DateRange, mixins.Human, mixins.Born):
    class Meta:
        app_label = 'households'
        abstract = dd.is_abstract_model(__name__, 'Member')
        verbose_name = _("Household Member")
        verbose_name_plural = _("Household Members")

    allow_cascaded_delete = 'household'

    role = MemberRoles.field(
        default=MemberRoles.as_callable('child'), blank=True, null=True)
    person = dd.ForeignKey(
        config.person_model, null=True, blank=True,
        related_name='household_members')
    household = dd.ForeignKey('households.Household')
    dependency = MemberDependencies.field(
        default=MemberDependencies.as_callable('none'))

    primary = models.BooleanField(_("Primary"), default=False)

    def full_clean(self):
        """Copy data fields from child"""
        if self.person_id:
            for k in person_fields:
                setattr(self, k, getattr(self.person, k))
        elif not settings.SITE.loading_from_dump:
            # create Person row if all fields are filled
            has_all_fields = True
            kw = dict()
            for k in person_fields:
                if getattr(self, k):
                    kw[k] = getattr(self, k)
                else:
                    has_all_fields = False
            if has_all_fields:
                # M = rt.models.pcsw.Client
                M = config.person_model
                try:
                    obj = M.objects.get(**kw)
                except M.DoesNotExist:
                    obj = M(**kw)
                    obj.full_clean()
                    obj.save()
                self.person = obj

        super(Member, self).full_clean()

        if not settings.SITE.loading_from_dump:
            # Auto-create human links between this member and other
            # household members.
            if self.person_id and self.role and self.household_id:
                if dd.is_installed('humanlinks'):
                    Link = rt.models.humanlinks.Link
                    ConcreteMember = rt.models.households.Member
                    if self.role in child_roles:
                        for pm in ConcreteMember.objects.filter(
                                household=self.household,
                                role__in=parent_roles):
                            Link.check_autocreate(pm.person, self.person)
                    elif self.role in parent_roles:
                        for cm in ConcreteMember.objects.filter(
                                household=self.household,
                                role__in=child_roles):
                            Link.check_autocreate(self.person, cm.person)

    def disabled_fields(self, ar):
        rv = super(Member, self).disabled_fields(ar)
        if self.person_id:
            rv |= person_fields
        #~ logger.info("20130808 pcsw %s", rv)
        return rv

    def after_ui_save(self, ar, cw):
        super(Member, self).after_ui_save(ar, cw)
        mi = self.person
        if mi is None:
            return
        if self.primary:
            for o in mi.household_members.exclude(id=self.id):
                if o.primary:
                    o.primary = False
                    o.save()
                    ar.set_response(refresh_all=True)

    def __str__(self):
        if self.person_id is None:
            # Avoid using super() in a __str__() method. See Luc's
            # blog 20160324
            return str('%s object' % self.__class__.__name__)
            # return models.Model.__str__(self)
            # return super(Member, self).__str__()
        if self.role is None:
            return str(self.person)
        return "%s (%s)" % (self.person, self.role)

    def get_address_lines(self):
        for ln in self.person.address_person_lines():
            yield ln
        if self.household:
            for ln in self.household.address_person_lines():
                yield ln
            for ln in self.household.address_location_lines():
                yield ln
        else:
            for ln in self.address_location_lines():
                yield ln

    @dd.action(help_text=_("Make this the primary household."))
    def set_primary(self, ar):
        self.primary = True
        self.full_clean()
        self.save()
        self.after_ui_save(ar, None)
        ar.success(refresh=True)

person_fields = dd.fields_list(
    Member, 'first_name last_name gender birth_date')

class Members(dd.Table):
    model = 'households.Member'
    required_roles = dd.login_required(ContactsStaff)
    order_by = ['start_date', 'end_date']


class MembersByHousehold(Members):
    required_roles = dd.login_required(ContactsUser)
    label = _("Household Members")
    master_key = 'household'
    column_names = "age:10 role dependency person \
    first_name last_name birth_date gender *"
    order_by = ['birth_date']
    auto_fit_column_widths = True


class SiblingsByPerson(Members):
    label = _("Household composition")
    required_roles = dd.login_required(ContactsUser)
    master = config.person_model
    column_names = "age:10 role dependency person \
    first_name last_name birth_date gender *"
    # column_names = 'person role start_date end_date *'
    order_by = ['birth_date']
    auto_fit_column_widths = True
    # display_mode = 'summary'
    window_size = (100, 20)

    @classmethod
    def setup_request(self, ar):
        ar.master_household = None
        mi = ar.master_instance  # a Person
        if mi is None:
            return
        M = rt.models.households.Member
        mbr = M.objects.filter(person=mi)
        if mbr.count() == 1:
            ar.master_household = mbr[0].household
        elif mbr.count() == 0:
            ar.no_data_text = _("%s is not member of any household") % mi
        else:  # more than 1 row
            mbr = mbr.filter(primary=True)
            if mbr.count() == 1:
                ar.master_household = mbr[0].household
            else:
                mbr = M.objects.filter(person=mi)
                mbr = dd.PeriodEvents.active.add_filter(mbr, dd.today())
                if mbr.count() == 1:
                    ar.master_household = mbr[0].household
                else:
                    ar.no_data_text = _(
                        "%s is member of multiple households") % mi

    @classmethod
    def get_filter_kw(self, ar, **kw):
        # hh = self.get_master_household(ar.master_instance)
        hh = ar.master_household
        if hh is None:
            return None
        kw.update(household=hh)
        return super(SiblingsByPerson, self).get_filter_kw(ar, **kw)

    @classmethod
    def get_table_summary(self, obj, ar):
        # For every child, we want to display its relationship to
        # every parent of this household.
        sar = self.request(master_instance=obj)
        if sar.master_household is None:
            return E.div(str(ar.no_data_text))
        # obj is the Person for which we display the household

        def format_item(m):
            elems = [str(m.role), ': ']
            if m.person:
                elems += [obj.format_family_member(ar, m.person)]
                hl = self.find_links(ar, m.person, obj)
                if len(hl):
                    elems += [' ('] + hl + [')']
            else:
                elems += [obj.format_family_member(ar, m)]
            return elems

        items = []
        for m in sar.data_iterator:
            items.append(E.li(*format_item(m)))
        elems = []
        if len(items) > 0:
            elems = []
            elems.append(E.ul(*items))
        return E.div(*elems)

    @classmethod
    def find_links(self, ar, child, parent):
        if not dd.is_installed('humanlinks'):
            return []
        types = {}  # mapping LinkType -> list of parents
        for lnk in rt.models.humanlinks.Link.objects.filter(child=child):
                # child=child, parent=p):
            tt = lnk.type.as_child(lnk.child)
            l = types.setdefault(tt, [])
            l.append(lnk.parent)
        elems = []
        for tt, parents in types.items():
            if len(elems):
                elems.append(', ')
            text = join_elems(
                [parent.format_family_member(ar, p) for p in parents],
                sep=" {} ".format(gettext("and")))
            elems += [tt, gettext(" of ")] + text
        return elems


class CreateHousehold(dd.Action):
    show_in_bbar = False
    custom_handler = True
    label = _("Create Household")
    parameters = dict(
        head=dd.ForeignKey(
            config.person_model, verbose_name=_("Head of household")),
        partner=dd.ForeignKey(
            config.person_model, verbose_name=_("Partner"),
            blank=True, null=True),
        type=dd.ForeignKey('households.Type', blank=True, null=True))
    params_layout = """
    head
    type
    partner
    """

    def action_param_defaults(self, ar, obj, **kw):
        # logger.info("20140426")
        kw = super(CreateHousehold, self).action_param_defaults(ar, obj, **kw)
        kw.update(head=obj)
        return kw

    def run_from_ui(self, ar, **kw):
        pv = ar.action_param_values
        rt.models.households.Household.create_household(
            ar, pv.head, pv.partner, pv.type)
        ar.success(
            _("Household has been created"),
            close_window=True, refresh_all=True)
        # ar.goto_instance(hh)

dd.inject_action(
    config.person_model,
    create_household=CreateHousehold())


class MembersByPerson(Members):
    required_roles = dd.login_required(ContactsUser)
    label = _("Household memberships")
    master_key = 'person'
    column_names = 'household role primary start_date end_date *'
    insert_layout = """
    person
    role
    household
    primary
    """
    # auto_fit_column_widths = True
    # hide_columns = 'id'
    display_mode = 'summary'
    stay_in_grid = True

    @classmethod
    def get_table_summary(self, obj, ar):
        sar = self.request(master_instance=obj)
        elems = []
        # n = sar.get_total_count()
        # if n == 0:
        #     elems += [_("Not member of any household."), E.br()]
        # else:

        items = []
        for m in sar.data_iterator:

            args = (str(m.role), gettext(" in "),
                    ar.obj2html(m.household))
            if m.primary:
                items.append(E.li(E.b("\u2611 ", *args)))
            else:
                btn = m.set_primary.as_button_elem(
                    ar, "\u2610 ", style="text-decoration:none;")
                items.append(E.li(btn, *args))
        if len(items) > 0:
            elems += [gettext("%s is") % obj]
            elems.append(E.ul(*items))

        if self.insert_action is not None:
            sar = self.insert_action.request_from(ar)
            if sar.get_permission():
                elems.append(E.br())
                sar.known_values.update(person=obj)
                # sar.known_values.pop('child', None)
                elems += [
                    sar.ar2button(
                        None, gettext("Join an existing household"), icon_name=None),
                    " ", gettext("or"), " ",
                    ar.instance_action_button(
                        obj.create_household,
                        gettext("create a new one")),
                    # " ",
                    # rt.models.households.Household._meta.verbose_name,
                    "."]

        return E.div(*elems)
