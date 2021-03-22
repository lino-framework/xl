from lino.api import rt, dd, _

def objects():
    Company = rt.models.contacts.Company
    obj = Company(name=_("Webshop customers without contact data"))
    yield obj

    sls = rt.models.ledger.Journal.get_by_ref("SLS")
    sls.partner = obj
    yield sls

    DeliveryMethod = rt.models.shopping.DeliveryMethod

    def delivery_method(designation, price, **kwargs):
        if dd.is_installed("products"):
            prod = rt.models.products.Product(**dd.str2kw('name', designation, sales_price=price))
            yield prod
            kwargs.update(product=prod)
        yield DeliveryMethod(**dd.str2kw('designation', designation, **kwargs))

    yield delivery_method(_("Parcel center"), 2)
    yield delivery_method(_("Home using UPS"), 5)
    yield delivery_method(_("Take away"), 0)
