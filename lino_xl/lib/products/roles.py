# -*- coding: UTF-8 -*-
# Copyright 2017 Rumma & Ko Ltd
# License: GNU Affero General Public License v3 (see file COPYING for details)


from lino.core.roles import UserRole


class ProductsUser(UserRole):
    pass

class ProductsStaff(ProductsUser):
    pass

