# -*- coding: UTF-8 -*-
# Copyright 2008-2018 Rumma 6 Ko Ltd
# License: BSD (see file COPYING for details)


from django.db import models
from django.utils.translation import ugettext_lazy as _

from lino.api import dd
from lino import mixins

from .choicelists import DeliveryUnits, ProductTypes
from .roles import ProductsUser, ProductsStaff

vat = dd.resolve_app('vat')


class ProductCat(mixins.BabelNamed):

    class Meta:
        app_label = 'products'
        verbose_name = _("Product Category")
        verbose_name_plural = _("Product Categories")
        abstract = dd.is_abstract_model(__name__, 'ProductCat')

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


class Product(mixins.BabelNamed):

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
    product_type = ProductTypes.field(default='default')

    if vat:
        vat_class = vat.VatClasses.field(blank=True)
    else:
        vat_class = dd.DummyField()


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
    order_by = ["id"]
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



