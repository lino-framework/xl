# -*- coding: UTF-8 -*-
# Copyright 2015-2017 Rumma & Ko Ltd
# License: BSD (see file COPYING for details)



from lino.core.roles import UserRole


class AccountingReader(UserRole):
    pass


class VoucherSupervisor(UserRole):
    """
    Somebody who can edit vouchers which have been written by other
    users.

    This role is automatically inherited by LedgerStaff.

    """
    pass

class LedgerUser(AccountingReader):
    pass


class LedgerStaff(LedgerUser, VoucherSupervisor):
    pass


