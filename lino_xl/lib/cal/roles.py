from lino.core.roles import UserRole

class CalendarGuest(UserRole):
    """Can see and manage their presences in calendar events."""
    pass

class CalendarReader(UserRole):
    """Has read-only access to calendars of other users."""
    pass

class GuestOperator(UserRole):
    """Can see guests of calendar entries."""
    pass

# class CalendarOperator(UserRole):
#     """Can modify calendar entries of other users."""
#     pass
