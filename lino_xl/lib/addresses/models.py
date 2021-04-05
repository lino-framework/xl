# Copyright 2014-2020 Rumma & Ko Ltd
# License: GNU Affero General Public License v3 (see file COPYING for details)


from django.db import models
from django.db.models import Q
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
            for o in mi.addresses_by_partner.exclude(id=self.id).filter(primary=True):
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
        unique_not_primary=_("Unique address is not marked primary."),
        sync_to_addr=_("Must sync owner to address."),
        sync_to_owner=_("Must sync address to owner."),
        new_primary=_("Must create missing primary address."),
    )

    # def getdiffs(self, owner, addr):
    #     diffs = {}
    #     for k in owner.ADDRESS_FIELDS:
    #         av = getattr(addr, k)
    #         ov = getattr(owner, k)
    #         if av != ov:
    #             diffs[k] = (av, ov)
    #     return diffs
    #
    # def can_sync_to_addr(self, diffs):
    #     for f, v in diffs.items():
    #         av, ov = v
    #         if av:
    #             return False
    #     return True
    #
    # def can_sync_to_owner(self, diffs):
    #     for f, v in diffs.items():
    #         av, ov = v
    #         if ov:
    #             return False
    #     return True
    #
    def get_checkdata_problems(self, obj, fix=False):
        if not isinstance(obj, dd.plugins.addresses.partner_model):
            return
        Address = rt.models.addresses.Address
        qs = obj.addresses_by_partner.all()
        qs_marked_primary = qs.filter(primary=True)

        # Having no primary address is okay when the partner's address is empty.
        if not obj.has_address():
            if qs_marked_primary.count() == 0:
                return

        num_addresses = qs.count()
        if num_addresses == 1:
            addr = qs[0]
            # check whether it is the same address than the one
            # specified on AddressOwner
            diffs = obj.get_diffs(addr)
            if diffs:
                if addr.can_sync_from(diffs):
                    yield (True, self.messages['sync_to_addr'])
                    if fix:
                        addr.primary = True
                        for k, v in diffs.items():
                            setattr(addr, k, getattr(obj, k))
                        addr.full_clean()
                        addr.save()
                    return
                if obj.can_sync_from(diffs):
                    yield (True, self.messages['sync_to_owner'])
                    if fix:
                        addr.primary = True
                        addr.full_clean()
                        addr.save()
                        for k, v in diffs.items():
                            setattr(obj, k, v)
                        # obj.sync_from_address(addr)
                        obj.full_clean()
                        obj.save()
                    return
            elif not addr.primary:
                yield (True, self.messages['unique_not_primary'])
                if fix:
                    addr.primary = True
                    addr.full_clean()
                    addr.save()
                return
            # continue below if there are diffs

        # how many addresses match the owner close enough to become primary?
        filters = []
        for k in obj.ADDRESS_FIELDS:
            v = getattr(obj, k, None)
            if v:
                fld = obj._meta.get_field(k)
                filters.append(Q(**{k: fld.get_default()}) | Q(**{k: v}))
        qs_matching = qs.filter(*filters)
        num_matching = qs_matching.count()
        if num_matching == 1:
            addr = qs_matching[0]
            if len(addr.get_diffs(obj)):
                yield (True, _("Primary address is not complete"))
                if fix:
                    addr.sync_from_address(obj)
                    addr.full_clean()
                    addr.save()
            if addr.primary:
                other_primaries = obj.addresses_by_partner.exclude(id=addr.id).filter(primary=True)
                if other_primaries.count():
                    yield (True, _("Multiple primary addresses."))
                    if fix:
                        other_primaries.update(primary=False)
            else:
                yield (True, _("Matching address is not marked primary."))
                if fix:
                    addr.primary = True
                    addr.full_clean()
                    addr.save()
                    # unmark previous primary
                    other_primaries = obj.addresses_by_partner.exclude(id=addr.id).filter(primary=True)
                    other_primaries.update(primary=False)
            return


        addr = None
        num_primary = qs_marked_primary.count()
        if num_primary == 0:
            if num_matching == 0:
                yield (True, _("Primary address is missing."))
                if fix:
                    addr = Address(partner=obj, primary=True, address_type=AddressTypes.official)
                    addr.sync_from_address(obj)
                    addr.full_clean()
                    addr.save()
            else:
                yield (False, _("No primary address, but matching addresses exist."))
            return

        elif num_primary == 1:
            addr = qs_marked_primary[0]
            diffs = obj.get_diffs(addr)
            if not diffs:
                return  # everything ok
        else:
            yield (False, _("Multiple primary addresses."))
        if addr and diffs:
            diffstext = [
                _("{0}:{1}->{2}").format(
                k, getattr(obj, k), v) for k, v in sorted(diffs.items())]
            msg = _("Primary address differs from owner address ({0}).").format(
                ', '.join(diffstext))
            yield (False, msg)
            # if len(diffs) > 1:  # at least two differences
            #     msg = self.messages['new_primary'].format(', '.join(diffstext))
            #     yield (True, msg)
            #     if fix:
            #         raise NotImplementedError()

AddressOwnerChecker.activate()
