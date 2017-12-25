# -*- coding: UTF-8 -*-
# Copyright 2017 Luc Saffre
# License: BSD (see file COPYING for details)


from lino.core.roles import UserRole


class ProductsUser(UserRole):
    pass

class ProductsStaff(ProductsUser):
    pass

