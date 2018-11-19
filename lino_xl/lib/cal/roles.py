from lino.core.roles import UserRole

class CalendarReader(UserRole):
    """Has read-only access to calendars of other users."""
    pass

class GuestOperator(UserRole):
    """Can see guests of calendar entries."""
    pass

# class CalendarOperator(UserRole):
#     """Can modify calendar entries of other users."""
#     pass

