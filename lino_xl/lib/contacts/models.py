# -*- coding: UTF-8 -*-
# Copyright 2008-2020 Rumma & Ko Ltd
# License: BSD (see file COPYING for details)

import os

from etgen.html import E, join_elems, forcetext
from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models
from django.db.models import Q

from lino import mixins
from lino.api import dd, rt, _
from lino.mixins.duplicable import Duplicable
from lino.mixins.human import name2kw, Human, Born, parse_name
from lino.mixins.sequenced import Sequenced
# from lino.mixins.periods import ObservedDateRange
from lino.mixins.periods import DateRangeObservable
from lino.modlib.printing.mixins import Printable
from lino.modlib.uploads.mixins import UploadController
from lino.utils import join_words
from lino.utils.addressable import Addressable
from lino.utils.media import TmpMediaFile
from lino_xl.lib.addresses.mixins import AddressOwner
from lino_xl.lib.phones.mixins import ContactDetailsOwner
from lino_xl.lib.skills.mixins import Feasible

from .choicelists import CivilStates
from .roles import SimpleContactsUser, ContactsStaff
from .choicelists import PartnerEvents

if dd.plugins.contacts.use_vcard_export:
    try:
        import vobject
    except ImportError:
        # silently ignore it because we don't want `inv install` to fail.
        # raise Exception(
        #     "use_vcard_export is True but vobject is not installed")
        vobject = None

with_roles_history = dd.plugins.contacts.with_roles_history


PARTNER_NUMBERS_START_AT = 100  # used for generating demo data and tests

class ExportVCardFile(dd.Action):
    label = _("Export as vCard")
    icon_name = 'vcard'
    sort_index = -10
    select_rows = False
    default_format = 'ajax'
    show_in_bbar = True
    # combo_group = 'pdf'

    # def is_callable_from(self, caller):
    #     return isinstance(caller, actions.ShowTable)

    def run_from_ui(self, ar, **kw):
        #~ print 20130912
        #~ obj = ar.selected_rows[0]
        mf = TmpMediaFile(ar, 'vcf')
        settings.SITE.makedirs_if_missing(os.path.dirname(mf.name))
        with open(mf.name, 'w') as wf:
            for obj in ar.selected_rows:
                j = vobject.vCard()
                obj.fill_vcard(j)
                wf.write(j.serialize())

        ar.set_response(success=True)
        ar.set_response(open_url=mf.get_url(ar.request))



class Partner(Duplicable, ContactDetailsOwner, mixins.Polymorphic,
              AddressOwner, UploadController, Feasible, Printable, DateRangeObservable):
    preferred_foreignkey_width = 20
    # preferred width for ForeignKey fields to a Partner

    class Meta(object):
        app_label = 'contacts'  # avoid RemovedInDjango19Warning
        abstract = dd.is_abstract_model(__name__, 'Partner')
        verbose_name = _("Partner")
        verbose_name_plural = _("Partners")

    if dd.plugins.contacts.use_vcard_export:
        export_vcf = ExportVCardFile()

    prefix = models.CharField(
        _("Name prefix"), max_length=200, blank=True)

    name = models.CharField(max_length=200, verbose_name=_('Name'))

    remarks = models.TextField(_("Remarks"), blank=True)  # ,null=True)

    quick_search_fields = "prefix name phone gsm"

    # print_labels = dd.PrintLabelsAction()

    allow_merge_action = True

    def on_create(self, ar):
        self.language = ar.get_user().language
        if not self.country:
            sc = settings.SITE.site_config
            if sc.site_company:
                self.country = sc.site_company.country
        super(Partner, self).on_create(ar)

    def save(self, *args, **kw):
        if self.id is None:
            sc = settings.SITE.site_config
            if sc.next_partner_id is not None:
                try:
                    rt.models.contacts.Partner.objects.get(id=sc.next_partner_id)
                    raise ValidationError(
                        "Cannot create partner with id={0}. "
                        "Check your next_partner_id in SiteConfig!".format(
                            sc.next_partner_id))
                except rt.models.contacts.Partner.DoesNotExist:
                    self.id = sc.next_partner_id
                    sc.next_partner_id += 1
                    sc.save()
        #~ dd.logger.info("20120327 Partner.save(%s,%s)",args,kw)
        # if self.name.startswith("Auto "):
        #     print("20190408 saving {} with vat_id {!r}".format(self, self.vat_id))
        super(Partner, self).save(*args, **kw)

    def get_last_name_prefix(self):
        # overrides lino.mixins.humans.Human
        return self.prefix

    def __str__(self):
        #~ return self.name
        return self.get_full_name()

    def address_person_lines(self):
        #~ yield self.name
        yield self.get_full_name()

    def get_full_name(self, *args, **kwargs):
        """Return a one-line string representing this Partner.  The default
        returns simply the `name`, optionally prefixed by the
        :attr:`prefix`, ignoring any arguments, but
        e.g. :class:`Human` overrides this.

        """
        return join_words(self.prefix, self.name)
    full_name = property(get_full_name)

    def get_partner_instance(self):
        return self  # compatibility with lino.modlib.partners

    def get_overview_elems(self, ar):
        elems = []
        buttons = self.get_mti_buttons(ar)
        if len(buttons) > 1:
            # buttons = join_elems(buttons, ', ')
            elems.append(E.p(str(_("See as ")), *buttons,
                             style="font-size:8px;text-align:right;padding:3pt;"))
        elems += self.get_name_elems(ar)
        elems.append(E.br())
        elems += join_elems(list(self.address_location_lines()), sep=E.br)
        elems = [
            E.div(*forcetext(elems),
                  style="font-size:18px;font-weigth:bold;"
                  "vertical-align:bottom;text-align:middle")]
        elems += AddressOwner.get_overview_elems(self, ar)
        elems += ContactDetailsOwner.get_overview_elems(self, ar)
        return elems

    def get_name_elems(self, ar):
        elems = []
        if self.prefix:
            elems += [self.prefix, ' ']
        elems.append(E.b(self.name))
        return elems

    def get_print_language(self):
        return self.language

    @classmethod
    def setup_parameters(cls, fields):
        fields.setdefault(
            'observed_event', PartnerEvents.field(
                blank=True,
                help_text=_("Extended filter criteria")))
        super(Partner, cls).setup_parameters(fields)

    @classmethod
    def get_request_queryset(self, ar, **filter):
        qs = super(Partner, self).get_request_queryset(ar, **filter)

        pv = ar.param_values
        oe = pv.observed_event
        if oe:
            qs = oe.add_filter(qs, pv)
        return qs

    @classmethod
    def get_title_tags(self, ar):
        for t in super(Partner, self).get_title_tags(ar):
            yield t
        pv = ar.param_values

        if pv.observed_event:
            yield str(pv.observed_event)


    def get_as_user(self):
        """Return the user object that corresponds to this partner.

        If the application's User model inherits from Partner, then


        """
        User = rt.models.users.User
        try:
            if issubclass(User, self.__class__):
                return User.objects.get(partner_ptr=self)
            else:
                return User.objects.get(partner=self)
        except User.DoesNotExist:
            pass
        except User.MultipleObjectsReturned:
            pass

    def fill_vcard(self, j):
        j.add('n')
        j.n.value = vobject.vcard.Name(family=self.name)
        j.add('fn')
        j.fn.value = self.name
        if self.city:
            j.add('adr')
            j.adr.street = self.street
            j.adr.box = (self.street_no + " " + self.street_box).strip()
            j.adr.city = str(self.city)
            j.adr.region = str(self.region)
            j.adr.country = str(self.country)
            j.adr.code = self.zip_code
        if self.email:
            j.add('email')
            j.email.value = self.email
            j.email.type_param = 'INTERNET'
        if self.phone:
            j.add('tel')
            j.tel.value = self.phone
            j.tel.type_param = 'HOME'
        if self.gsm:
            j.add('tel')
            j.tel.value = self.gsm
            j.tel.type_param = 'CELL'
        if self.url:
            j.add('url')
            j.url.value = self.url


class PartnerDetail(dd.DetailLayout):

    main = """
    address_box:60 contact_box:30 overview
    bottom_box
    """

    address_box = dd.Panel("""
    name_box
    country region city zip_code:10
    addr1
    #street_prefix street:25 street_no street_box
    addr2
    """, label=_("Address"))

    contact_box = dd.Panel("""
    info_box
    email:40
    url
    phone
    gsm fax
    """, label=_("Contact"))

    bottom_box = """
    remarks
    """

    name_box = "#prefix name"
    info_box = "id:6 language:6"


class Partners(dd.Table):
    required_roles = dd.login_required(SimpleContactsUser)
    model = 'contacts.Partner'
    column_names = "name id mti_navigator email * "
    order_by = ['name', 'id']
    # parameters = ObservedDateRange()
    # detail_layout = 'contacts.PartnerDetail'
    # removed for #2777 ()
    # insert_layout = """
    # name
    # #language email
    # """

    @classmethod
    def get_queryset(self, ar):
        qs = super(Partners, self).get_queryset(ar)
        return qs.select_related('country', 'city')
        # return self.model.objects.select_related('country', 'city')


#~ class AllPartners(Partners):

    #~ @classmethod
    #~ def get_actor_label(self):
        #~ return _("All %s") % self.model._meta.verbose_name_plural

class PartnersByCity(Partners):
    master_key = 'city'
    order_by = 'street street_no street_box addr2'.split()
    column_names = "address_column #street #street_no #street_box #addr2 name *"


class PartnersByCountry(Partners):
    master_key = 'country'
    column_names = "city street street_no name language *"
    order_by = "city street street_no".split()

class Person(Human, Born, Partner):
    class Meta(object):
        app_label = 'contacts'
        abstract = dd.is_abstract_model(__name__, 'Person')
        verbose_name = _("Person")
        verbose_name_plural = _("Persons")
        ordering = ['last_name', 'first_name']

    def get_after_salutation_words(self):
        if self.prefix:
            yield self.prefix

    def full_clean(self, *args, **kw):
        """Set the `name` field of this person.  This field is visible in the
        Partner's detail but not in the Person's detail and serves for
        sorting when selecting a Partner.  It also serves for quick
        search on Persons.

        """
        name = join_words(self.last_name, self.first_name)
        if name:
            self.name = name
        else:
            for k, v in list(name2kw(self.name).items()):
                setattr(self, k, v)
            # self.last_name = self.name
        super(Person, self).full_clean(*args, **kw)

    def address_person_lines(self, *args, **kw):
        "Deserves more documentation."
        # if self.title:
        #     yield join_words(self.get_salutation(), self.title)
        #     kw.update(salutation=False)
        yield self.get_full_name(*args, **kw)

    def get_name_elems(self, ar):
        elems = [self.get_salutation(nominative=True), ' ',
                 self.prefix, E.br()]
        elems += [self.first_name, ' ', E.b(self.last_name)]
        return elems

    def fill_vcard(self, j):
        super(Person, self).fill_vcard(j)
        j.n.value = vobject.vcard.Name(
            family=self.last_name, given=self.first_name )

    @classmethod
    def parse_to_dict(cls, text):
        return parse_name(text)

class PersonDetail(PartnerDetail):

    name_box = "last_name first_name:15 gender #prefix:10"
    info_box = "id:5 language:10"
    bottom_box = "remarks contacts.RolesByPerson"


class Persons(Partners):
    required_roles = dd.login_required(SimpleContactsUser)
    model = "contacts.Person"
    order_by = ["last_name", "first_name", "id"]
    column_names = (
        "name_column:20 address_column email "
        "phone:10 gsm:10 id language:10 *")
    detail_layout = 'contacts.PersonDetail'

    insert_layout = """
    first_name last_name
    gender email #language
    """


class CompanyType(mixins.BabelNamed):
    class Meta(object):
        app_label = 'contacts'  # avoid RemovedInDjango19Warning
        abstract = dd.is_abstract_model(__name__, 'CompanyType')
        verbose_name = _("Organization type")
        verbose_name_plural = _("Organization types")

    abbr = dd.BabelCharField(_("Abbreviation"), max_length=30, blank=True)


class CompanyTypes(dd.Table):
    required_roles = dd.login_required(ContactsStaff)
    model = 'contacts.CompanyType'
    column_names = 'name *'
    #~ label = _("Company types")


class Company(Partner):
    class Meta(object):
        abstract = dd.is_abstract_model(__name__, 'Company')
        app_label = 'contacts'
        verbose_name = _("Organization")
        verbose_name_plural = _("Organizations")

    type = dd.ForeignKey('contacts.CompanyType', blank=True, null=True)

    def get_full_name(self, salutation=True, **salutation_options):
        """Deserves more documentation."""
        #~ print '20120729 Company.get_full_name`'
        if self.type:
            return join_words(self.prefix, self.type.abbr, self.name)
        return join_words(self.prefix, self.name)
    full_name = property(get_full_name)

    def get_signers(self, today=None):
        if today is None:
            today = dd.today()
        qs = rt.models.contacts.Role.objects.filter(company=self).order_by('type')
        qs = qs.filter(type__can_sign=True)
        if with_roles_history:
            qs = qs.filter(Q(start_date__isnull) | Q(start_date__lte=today))
            qs = qs.filter(Q(end_date__isnull) | Q(end_date__gte=today))
        return qs


class CompanyDetail(PartnerDetail):

    bottom_box = """
    remarks contacts.RolesByCompany
    """

    name_box = "#prefix:10 name:40 type:20"


class Companies(Partners):
    required_roles = dd.login_required(SimpleContactsUser)
    model = "contacts.Company"
    order_by = ["name"]
    column_names = (
        "name_column:20 address_column email "
        "phone:10 gsm:10 id language:10 *")
    detail_layout = 'contacts.CompanyDetail'
    insert_layout = """
    name
    #language:20 email:40
    type #id
    """

#~ class List(Partner):
    #~ pass

#~ class Lists(Partners):
    #~ model = List
    #~ order_by = ["name"]
    #~ detail_layout = """
    #~ id name
    #~ language email
    #~ MembersByList
    #~ """
    #~ insert_layout = dd.FormLayout("""
    #~ name
    #~ language email
    #~ """,window_size=(40,'auto'))


# class ContactType(mixins.BabelNamed):
class RoleType(mixins.BabelNamed):

    class Meta(object):
        app_label = 'contacts'  # avoid RemovedInDjango19Warning
        abstract = dd.is_abstract_model(__name__, 'RoleType')
        verbose_name = _("Function")
        verbose_name_plural = _("Functions")

    can_sign = models.BooleanField(_("Authorized to sign"), default=False)


class RoleTypes(dd.Table):
    required_roles = dd.login_required(ContactsStaff)
    model = 'contacts.RoleType'



class Role(dd.Model, Addressable):

    class Meta(object):
        app_label = 'contacts'  # avoid RemovedInDjango19Warning
        abstract = dd.is_abstract_model(__name__, 'Role')
        verbose_name = _("Contact person")
        verbose_name_plural = _("Contact persons")

    type = dd.ForeignKey(
        'contacts.RoleType',
        blank=True, null=True)
    person = dd.ForeignKey(
        "contacts.Person", related_name='rolesbyperson')
    company = dd.ForeignKey(
        "contacts.Company", related_name='rolesbycompany')

    if with_roles_history:
        start_date = models.DateField(
            verbose_name=_("Start date"), blank=True, null=True)
        end_date = models.DateField(
            verbose_name=_("End date"), blank=True, null=True)
    else:
        start_date = dd.DummyField()
        end_date = dd.DummyField()


    def __str__(self):
        if self.person_id is None:
            return super(Role, self).__str__()
        if self.type is None:
            return str(self.person)
        return "%s (%s)" % (self.person, self.type)

    def address_person_lines(self):
        if self.company:
            for ln in self.company.address_person_lines():
                yield ln
        for ln in self.person.address_person_lines():
            yield ln

    def address_location_lines(self):
        if self.company_id:
            return self.company.address_location_lines()
        if self.person_id:
            return self.person.address_location_lines()
        return super(Role, self).__str__()

    def get_print_language(self):
        if self.company_id:
            return self.company.language
        if self.person_id:
            return self.person.language
        return super(Role, self).get_print_language()

    @dd.chooser()
    def person_choices(cls):
        # needed to activate create_person_choice
        return rt.models.contacts.Person.objects.all()

    def create_person_choice(self, text):
        """
        Called when an unknown person name was given.
        If the given text looks like a full name of a person, create it.
        """
        person_model = rt.models.contacts.Person
        if person_model.disable_create_choice:
            return
        try:
            values = person_model.parse_to_dict(text)
        except Exception as e:
            raise ValidationError(
                _("Could not create {person} from '{text}'").format(
                person=person_model._meta.verbose_name, text=text))
        obj = person_model(**values)
        obj.full_clean()
        obj.save()
        return obj




class Roles(dd.Table):
    required_roles = dd.login_required(ContactsStaff)
    model = 'contacts.Role'


class RolesByCompany(Roles):
    required_roles = dd.login_required(SimpleContactsUser)
    auto_fit_column_widths = True
    #~ required_user_level = None
    label = _("Contact persons")
    master_key = 'company'
    column_names = 'person type start_date end_date *'
    hidden_columns = 'id'


class RolesByPerson(Roles):
    """Shows all roles of a person."""
    required_roles = dd.login_required(SimpleContactsUser)
    #~ required_user_level = None
    label = _("Contact for")
    master_key = 'person'
    column_names = 'company type start_date end_date *'
    auto_fit_column_widths = True
    hidden_columns = 'id'

dd.inject_field(
    'system.SiteConfig',
    'next_partner_id',
    models.IntegerField(
        default=PARTNER_NUMBERS_START_AT,
        blank=True, null=True,
        verbose_name=_("Next partner id"),
        help_text=_("The next automatic id for any new partner.")))



@dd.receiver(dd.pre_analyze)
def company_model_alias(sender, **kw):
    """
    prepare ticket #72 which will rename Company to Organisation
    """
    sender.modules.contacts.Organisation = sender.modules.contacts.Company


@dd.receiver(dd.post_analyze)
def company_tables_alias(sender, **kw):
    """
    prepare ticket #72 which will rename Company to Organisation
    """
    sender.modules.contacts.Organisations = sender.modules.contacts.Companies


def PartnerField(**kw):
    return dd.ForeignKey(Partner, **kw)


# class Signer(Sequenced):
#
#     class Meta(object):
#         app_label = 'contacts'  # avoid RemovedInDjango19Warning
#         abstract = dd.is_abstract_model(__name__, 'Signer')
#         verbose_name = _("Signer")
#         verbose_name_plural = _("Signers")
#
#     signer = dd.ForeignKey("contacts.Role")
#
#     @dd.chooser()
#     def signer_choices(cls):
#         return rt.models.contacts.Role.objects.filter(
#             company=settings.SITE.site_config.site_company)
#
#
# class Signers(dd.Table):
#     model = "contacts.Signer"
#     column_names = "seqno signer *"  # signer__person signer__type *"
