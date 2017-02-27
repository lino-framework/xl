# -*- coding: UTF-8 -*-
# Copyright 2017 Luc Saffre
# License: BSD (see file COPYING for details)


from lino.core.roles import SiteUser


class ProductsUser(SiteUser):
    pass

class ProductsStaff(ProductsUser):
    pass

