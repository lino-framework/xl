# -*- coding: UTF-8 -*-
# Copyright 2021 Rumma & Ko Ltd
# License: GNU Affero General Public License v3 (see file COPYING for details)

from django.db import models
from django.utils import translation

from lino.api import dd, rt, _
from lino.utils.mldbc.mixins import BabelDesignated
from lino.modlib.users.mixins import UserAuthored, UserPlan, My
# from lino_xl.lib.contacts.mixins import PartnerDocument
from lino_xl.lib.ledger.roles import LedgerUser, LedgerStaff
from lino_xl.lib.countries.mixins import AddressLocation

class DeliveryMethod(BabelDesignated):

    class Meta:
        app_label = 'shopping'
        verbose_name = _("Delivery method")
        verbose_name_plural = _("Delivery methods")

    product = dd.ForeignKey('products.Product')


class Address(UserAuthored, AddressLocation):
    # user, person ,company
    class Meta:
        app_label = 'shopping'
        abstract = dd.is_abstract_model(__name__, 'Cart')
        verbose_name = _("Address")
        verbose_name_plural = _("Addresses")

    nickname = models.CharField(_("Nickname"), max_length=250, blank=True)

    def __str__(self):
        return self.address_location(', ')


class StartOrder(dd.Action):
    label = _("Start order")
    icon_name = 'money'
    sort_index = 53

    def run_from_ui(self, ar, **kw):
        # for plan in ar.selected_rows:
        plan = ar.selected_rows[0]
        plan.run_start_order(ar)
        ar.success(refresh=True)



class Cart(UserPlan):
    class Meta:
        app_label = 'shopping'
        abstract = dd.is_abstract_model(__name__, 'Cart')
        verbose_name = _("Shopping cart")
        verbose_name_plural = _("Shopping carts")

    start_order = StartOrder()

    invoicing_address = dd.ForeignKey('shopping.Address',
        blank=True, null=True,
        verbose_name=_("Invoicing address"),
        related_name="carts_by_invoicing_address")
    delivery_address = dd.ForeignKey('shopping.Address',
        blank=True, null=True,
        verbose_name=_("Delivery address"),
        related_name="carts_by_delivery_address")
    delivery_method = dd.ForeignKey('shopping.DeliveryMethod', blank=True, null=True)
    invoice = dd.ForeignKey(
        'sales.VatProductInvoice',
        verbose_name=_("Invoice"),
        null=True, blank=True,
        on_delete=models.SET_NULL)

    def __str__(self):
        return str(self.user)

    @dd.chooser()
    def invoicing_address_choices(self, user):
        return rt.models.shopping.Address.objects.filter(user=user)

    @dd.chooser()
    def delivery_address_choices(self, user):
        return rt.models.shopping.Address.objects.filter(user=user)

    @dd.displayfield(_("Invoice"))
    def invoice_button(self, ar):
        if ar is not None:
            if self.invoice_id:
                return self.invoice.obj2href(ar)
            ba = ar.actor.get_action_by_name('create_invoice')
            if ar.actor.get_row_permission(self, ar, None, ba):
                return ar.action_button(ba, self)
        return ''

    def run_start_order(self, ar):
        self.create_invoice(ar)

    def create_invoice(self,  ar):
        if dd.plugins.shopping.journal_ref is None:
            raise Warning(_("No journal configured for shopping"))
        jnl = rt.models.ledger.Journal.get_by_ref(dd.plugins.shopping.journal_ref)
        partner = ar.get_user().partner or jnl.partner
        invoice = jnl.create_voucher(partner=partner, user=ar.get_user())
        lng = invoice.get_print_language()
        items = []
        with translation.override(lng):
            for ci in self.cart_items.all():
                kwargs = dict(product=ci.product, qty=ci.qty)
                items.append(invoice.add_voucher_item(**kwargs))
            if self.delivery_method and self.delivery_method.product:
                kwargs = dict(product=self.delivery_method.product)
                items.append(invoice.add_voucher_item(**kwargs))

        if len(items) == 0:
            raise Warning(_("Your cart is empty."))

        invoice.full_clean()
        invoice.save()

        for i in items:
            # assign voucher after it has been saved
            i.voucher = invoice
            i.discount_changed()
            i.full_clean()
            i.save()

        self.invoice = invoice
        self.full_clean()
        self.save()

        invoice.compute_totals()
        invoice.full_clean()
        invoice.save()
        invoice.register(ar)
        return ar.goto_instance(invoice)


class CartItem(dd.Model):
    class Meta:
        app_label = 'shopping'
        abstract = dd.is_abstract_model(__name__, 'Cart')
        verbose_name = _("Shopping cart item")
        verbose_name_plural = _("Shopping cart items")

    allow_cascaded_delete = "cart product"

    cart = dd.ForeignKey('shopping.Cart', related_name="cart_items")
    product = dd.ForeignKey('products.Product', blank=True, null=True)
    qty = dd.QuantityField(_("Quantity"), blank=True, null=True)

    def __str__(self):
        return "{0} {1}".format(self.cart, self.product)



class DeliveryMethods(dd.Table):
    required_roles = dd.login_required(LedgerStaff)
    model = "shopping.DeliveryMethod"


class Addresses(dd.Table):
    model = 'shopping.Address'
    insert_layout = """
    addr1
    street street_no street_box
    addr2
    country region city zip_code
    """
    detail_layout = dd.DetailLayout("""
    id nickname user
    addr1
    street street_no street_box
    addr2
    country region city zip_code
    """, window_size=(60, 'auto'))

class AllAddresses(Addresses):
    required_roles = dd.login_required(LedgerStaff)

class MyAddresses(My, Addresses):
    pass


class Carts(dd.Table):
    model = "shopping.Cart"
    detail_layout = """user today delivery_method
    invoicing_address delivery_address invoice
    shopping.ItemsByCart
    """

class MyCart(My, Carts):
    hide_navigator = True
    # hide_top_toolbar = True
    # default_list_action_name = 'detail'
    #
    # @classmethod
    # def get_default_action(cls):
    #     return cls.detail_action

class AllCarts(Carts):
    required_roles = dd.login_required(LedgerStaff)


class CartItems(dd.Table):
    required_roles = dd.login_required(LedgerUser)
    model = "shopping.CartItem"


class ItemsByCart(CartItems):
    master_key = 'cart'
    column_names = "product qty *"


class AddToCart(dd.Action):
    label = _('Add to cart')
    button_text = " 🛒 " # (U+1F6D2)
    # icon_name = 'lightning'

    def run_from_ui(self, ar):
        my_cart = rt.models.shopping.Cart.run_start_plan(ar.get_user())
        texts = []
        CartItem = rt.models.shopping.CartItem
        for obj in ar.selected_rows:
            texts.append(str(obj))
            qs = CartItem.objects.filter(cart=my_cart, product=obj)
            if qs.count() == 0:
                cart_item = CartItem(cart=my_cart, product=obj, qty=1)
            else:
                cart_item = qs.first()
                cart_item.qty += 1
            cart_item.full_clean()
            if not ar.xcallback_answers: # because this is called again after confirm
                cart_item.save()

        def ok(ar2):
            ar2.goto_instance(my_cart)
        msg = _("{} has been placed to your shopping cart. Proceed to payment now?")
        ar.confirm(ok, msg.format(", ".join(texts)))


dd.inject_action('products.Product', add_to_cart=AddToCart())
