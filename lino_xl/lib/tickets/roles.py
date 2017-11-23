# Copyright 2015-2017 Luc Saffre
# License: BSD (see file COPYING for details)
"""User roles for `lino_xl.lib.tickets`.

"""

from lino.core.roles import UserRole

class TicketsReader(UserRole):
    pass

class Searcher(UserRole):    
    """A user who can see all tickets.

    """

class Triager(UserRole):
    """A user who is responsible for triaging new tickets.

    """

class Reporter(UserRole):
    """A user who can create new tickets and edit their own tickets.

    """


class TicketsStaff(UserRole):
    """Can configure tickets functionality.

    """

