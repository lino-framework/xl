# Copyright 2015-2018 Rumma & Ko Ltd
# License: BSD (see file COPYING for details)
"""User roles for `lino_xl.lib.tickets`.

"""

from lino.core.roles import UserRole

class TicketsReader(UserRole):
    pass

class Searcher(UserRole):    
    """Can see all tickets.

    """

class Triager(UserRole):
    """Is responsible for triaging new tickets.

    """

class Reporter(UserRole):
    """Can create new tickets and edit their own tickets.

    """


class TicketsStaff(UserRole):
    """Can configure tickets functionality.

    """

