# -*- coding: UTF-8 -*-
# Copyright 2019 Rumma & Ko Ltd
# License: GNU Affero General Public License v3 (see file COPYING for details)

from lino.core.roles import UserRole


class OrdersUser(UserRole):
    "Can use orders."
    pass


class OrdersStaff(OrdersUser):
    "Can use and configure orders."
    pass

