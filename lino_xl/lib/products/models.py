# -*- coding: UTF-8 -*-
# Copyright 2008-2019 Rumma 6 Ko Ltd
# License: BSD (see file COPYING for details)


from django.db import models
from django.utils.translation import ugettext_lazy as _

from lino.api import dd, rt
from lino import mixins
from lino.mixins import Sequenced
from lino.mixins.duplicable import Duplicable

from lino_xl.lib.vat.choicelists import VatClasses

from .choicelists import DeliveryUnits, ProductTypes, PriceFactors
from .roles import ProductsUser, ProductsStaff

# vat = dd.resolve_app('vat')


class ProductCat(mixins.BabelNamed):

    class Meta:
        app_label = 'products'
        verbose_name = _("Product Category")
        verbose_name_plural = _("Product Categories")
        abstract = dd.is_abstract_model(__name__, 'ProductCat')

    product_type = ProductTypes.field(default='default')
    description = models.TextField(blank=True)


class ProductCats(dd.Table):
    model = 'products.ProductCat'
    required_roles = dd.login_required(ProductsStaff)
    order_by = ["id"]
    detail_layout = """
    id name
    description
    ProductsByCategory
    """


class Product(mixins.BabelNamed, Duplicable):

    class Meta:
        app_label = 'products'
        verbose_name = _("Product")
        verbose_name_plural = _("Products")
        abstract = dd.is_abstract_model(__name__, 'Product')

    description = dd.BabelTextField(
        verbose_name=_("Long description"),
        blank=True, null=True)
    cat = dd.ForeignKey(
        ProductCat, verbose_name=_("Category"),
        blank=True, null=True)

    delivery_unit = DeliveryUnits.field(default='piece')
    product_type = ProductTypes.field()
    vat_class = VatClasses.field(blank=True)

    @dd.chooser()
    def cat_choices(self, product_type):
        qs = rt.models.products.ProductCats.request().data_iterator
        if product_type is not None:
            qs = qs.filter(product_type=product_type)
        return qs

    @classmethod
    def get_product_choices(cls, partner):
        """Return a list of products that are allowed for the specified partner.
        """
        Product = cls
        qs = Product.objects.filter(product_type=ProductTypes.default)
        qs = qs.order_by('name')
        rules = PriceRule.objects.all()
        for pf in PriceFactors.get_list_items():
            rules = rules.filter(
                Q(**{pf.field_name: getattr(partner, pf.field_name)}) |
                Q(**{pf.field_name + '__isnull': True}))
        return [p for p in qs if rules.filter(product=p).count() > 0]
        # TODO: add rules condition as subquery to qs and return the query, not
        # the list

    @classmethod
    def get_ruled_price(cls, partner, selector):
        if partner is None:
            return
        for rule in rt.models.products.PriceRule.objects.order_by('seqno'):
            ok = True
            for pf in PriceFactors.get_list_items():
                rv = getattr(rule, pf.field_name)
                if rv:
                    pv = getattr(partner, pf.field_name)
                    if pv != rv:
                        # print("20181128a {} != {}".format(rv, pv))
                        ok = False
            # if rule.tariff and rule.tariff != tariff:
            #     # print("20181128b {} != {}".format(rule.tariff, tariff))
            #     ok = False
            if rule.selector and rule.selector != selector:
                # print("20181128c {} != {}".format(rule.event_type, event_type))
                ok = False

            if ok and rule.product is not None:
                return rule.product

    def full_clean(self):
        # print("20191210", self.name, self.vat_class)
        if self.product_type is None:
            if self.cat_id:
                self.product_type = self.cat.product_type or ProductTypes.default
            else:
                self.product_type = ProductTypes.default
        super(Product, self).full_clean()


class ProductDetail(dd.DetailLayout):

    main = """
    id cat #sales_price vat_class delivery_unit
    name
    description
    """


class Products(dd.Table):
    _product_type = None
    required_roles = dd.login_required(ProductsUser)
    model = 'products.Product'
    order_by = ["name"]
    column_names = "id name cat vat_class *"

    insert_layout = """
    cat
    name
    """
    detail_layout = "products.ProductDetail"

    @classmethod
    def get_actor_label(cls):
        pt = cls._product_type or ProductTypes.default
        return pt.text

    @classmethod
    def create_instance(cls, ar, **kwargs):
        kwargs.update(product_type=cls._product_type or ProductTypes.default)
        return super(Products, cls).create_instance(ar, **kwargs)

    @classmethod
    def get_queryset(cls, ar, **filter):
        filter.update(product_type=cls._product_type or ProductTypes.default)
        return super(Products, cls).get_queryset(ar, **filter)


class ProductsByCategory(Products):
    master_key = 'cat'


class PriceRule(Sequenced):
    class Meta(object):
        app_label = 'products'
        abstract = dd.is_abstract_model(__name__, 'PriceRule')
        verbose_name = _("Price rule")
        verbose_name_plural = _("Price rules")

    # allow_cascaded_delete = ["selector"]
    selector = dd.ForeignKey(dd.plugins.products.price_selector, blank=True, null=True)
    product = dd.ForeignKey('products.Product', blank=True, null=True)


class PriceRules(dd.Table):
    model = "products.PriceRule"
    column_names_tpl = "seqno {factors} selector product *"
    order_by = ['seqno']

    @classmethod
    def get_column_names(cls, ar):
        factors = ' '.join([pf.field_name for pf in PriceFactors.get_list_items()])
        return cls.column_names_tpl.format(factors=factors)


@dd.receiver(dd.pre_analyze)
def inject_pricefactor_fields(sender, **kw):
    for pf in PriceFactors.get_list_items():
        dd.inject_field(
            'products.PriceRule', pf.field_name,
            pf.field_cls.field(blank=True))
        dd.inject_field(
            'contacts.Partner', pf.field_name,
            pf.field_cls.field(blank=True))
