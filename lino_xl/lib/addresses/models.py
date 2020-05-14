# Copyright 2014-2019 Rumma & Ko Ltd
# License: BSD (see file COPYING for details)


from django.db import models
from lino.api import dd, rt, _
from lino.modlib.checkdata.choicelists import Checker
from lino_xl.lib.countries.mixins import AddressLocation
from lino.core.roles import SiteStaff

from .choicelists import AddressTypes, DataSources
from .mixins import AddressOwner


class Address(AddressLocation):

    class Meta:
        app_label = 'addresses'
        verbose_name = _("Address")
        verbose_name_plural = _("Addresses")

    quick_search_fields = "partner__name city__name street"

    data_source = DataSources.field(editable=False, default='manually')
    # address_type = AddressTypes.field(blank=True, null=True)
    address_type = AddressTypes.field(default='official')
    partner = dd.ForeignKey(
        dd.plugins.addresses.partner_model,
        related_name='addresses_by_partner')
    remark = dd.CharField(_("Remark"), max_length=50, blank=True)

    primary = models.BooleanField(_("Primary"), default=False)

    allow_cascaded_delete = ['partner']

    def __str__(self):
        return self.address_location(', ')

    def after_ui_save(self, ar, cw):
        super(Address, self).after_ui_save(ar, cw)
        mi = self.partner
        if mi is None:
            return
        if self.primary:
            for o in mi.addresses_by_partner.exclude(id=self.id):
                if o.primary:
                    o.primary = False
                    o.save()
                    ar.set_response(refresh_all=True)
        mi.sync_primary_address(ar.request)

    def living_at_text(self):
        lines = list(self.address_location_lines())
        return self.address_type.living_text + ' ' + ', '.join(lines)

    @classmethod
    def setup_parameters(cls, fields):
        fields.update(
            place=dd.ForeignKey('countries.Place', blank=True, null=True))
        super(Address, cls).setup_parameters(fields)

    @classmethod
    def get_request_queryset(cls, ar, **filter):
        qs = super(Address, cls).get_request_queryset(ar, **filter)
        pv = ar.param_values
        if pv.place:
            qs = qs.filter(city=pv.place)
        return qs

    @classmethod
    def get_title_tags(self, ar):
        for t in super(Address, self).get_title_tags(ar):
            yield t
        pv = ar.param_values
        if pv.place:
            yield str(pv.place)

    @classmethod
    def get_simple_parameters(cls):
        for p in  super(Address, cls).get_simple_parameters():
            yield p
        yield 'partner'
        yield 'address_type'



Address.ADDRESS_FIELDS = dd.fields_list(
    Address,
    'street street_no street_box addr1 addr2 zip_code city region country')


@dd.receiver(dd.pre_ui_delete, sender=Address)
def clear_partner_on_delete(sender=None, request=None, **kw):
    self = sender
    mi = self.partner
    if mi:
        mi.sync_primary_address(request)


class Addresses(dd.Table):
    model = 'addresses.Address'
    required_roles = dd.login_required(SiteStaff)
    params_layout = "place partner address_type"
    column_names = (
        "partner address_type:10 remark:10 "
        "address_column:30 primary data_source *")

    insert_layout = """
    country city
    street street_no street_box
    address_type remark
    """

    detail_layout = dd.DetailLayout("""
    country city zip_code
    addr1
    street street_no street_box
    addr2
    address_type remark
    data_source partner
    """, window_size=(60, 'auto'))


class AddressesByPartner(Addresses):
    required_roles = dd.login_required()
    master_key = 'partner'
    column_names = 'address_type:10 remark:10 address_column:30 primary:5 *'
    label = _("Addresses")
    auto_fit_column_widths = True
    stay_in_grid = True
    window_size = (80, 20)

    # display_mode = 'summary'

    # @classmethod
    # def get_table_summary(self, obj, ar):
    #     return obj.get_overview_elems(ar)



class AddressesByCity(Addresses):
    required_roles = dd.login_required()
    master_key = 'city'
    column_names = 'address_type:10 partner remark:10 street primary:5 *'
    stay_in_grid = True
    window_size = (80, 20)


class AddressOwnerChecker(Checker):
    verbose_name = _("Check for missing or non-primary address records")
    model = AddressOwner
    messages = dict(
        no_address=_("Owner with address, but no address record."),
        unique_not_primary=_("Unique address is not marked primary."),
        no_primary=_("Multiple addresses, but none is primary."),
        # invalid_partner_model=_("Invalid partner model."),
        multiple_primary=_("Multiple primary addresses."),
        primary_differs=_("Primary address differs from owner address ({0})."),
    )

    def get_checkdata_problems(self, obj, fix=False):
        if not isinstance(obj, dd.plugins.addresses.partner_model):
            return
        Address = rt.models.addresses.Address
        qs = Address.objects.filter(partner=obj)
        num = qs.count()
        if num == 0:
            kw = dict()
            for fldname in Address.ADDRESS_FIELDS:
                value = getattr(obj, fldname)
                if value:
                    kw[fldname] = value
            if kw:
                yield (True, self.messages['no_address'])
                if fix:
                    kw.update(partner=obj, primary=True)
                    kw.update(address_type=AddressTypes.official)
                    addr = Address(**kw)
                    addr.full_clean()
                    addr.save()
            return

        def getdiffs(obj, addr):
            diffs = {}
            for k in Address.ADDRESS_FIELDS:
                my = getattr(addr, k)
                other = getattr(obj, k)
                if my != other:
                    diffs[k] = (my, other)
            return diffs

        if num == 1:
            addr = qs[0]
            # check whether it is the same address than the one
            # specified on AddressOwner
            diffs = getdiffs(obj, addr)
            if not diffs:
                if not addr.primary:
                    yield (True, self.messages['unique_not_primary'])
                    if fix:
                        addr.primary = True
                        addr.full_clean()
                        addr.save()
                return
        else:
            addr = None
            qs = qs.filter(primary=True)
            num = qs.count()
            if num == 0:
                yield (False, self.messages['no_primary'])
            elif num == 1:
                addr = qs[0]
                diffs = getdiffs(obj, addr)
            else:
                yield (False, self.messages['multiple_primary'])
        if addr and diffs:
            diffstext = [
                _("{0}:{1}->{2}").format(k, *v) for k, v in sorted(diffs.items())]
            msg = self.messages['primary_differs'].format(', '.join(diffstext))
            yield (False, msg)

AddressOwnerChecker.activate()
