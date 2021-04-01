# -*- coding: UTF-8 -*-
# Copyright 2016-2017 Rumma & Ko Ltd
# License: BSD (see file COPYING for details)

"""Desktop UI for this plugin.

"""

from lino.modlib.users.desktop import *

from lino.api import _

from lino.core import actions
# from lino.modlib.office.roles import OfficeUser
from lino_xl.lib.working.roles import Worker
from .choicelists import UserStates

from lino.modlib.users.actions import SendWelcomeMail
from lino.modlib.office.roles import OfficeUser
#from .models import VerifyUser

Users.parameters.update(user_state=UserStates.field(blank=True))
# Users.simple_parameters = ['user_type', 'user_state']
# Users.workflow_state_field = 'user_state'

class OtherUsers(Users):
    hide_top_toolbar = True
    hide_navigator = True
    use_as_default_table = False
    editable = False
    required_roles = dd.login_required()
    detail_layout = dd.DetailLayout("""
    first_name last_name city #user_site
    phone gsm
    about_me
    """, window_size=(60, 15))


# def site_setup(site):
#     site.modules.users.Users.set_detail_layout(UserDetail())


class RegisterUserLayout(dd.InsertLayout):

    window_size = (60, 'auto')

    main = """
    first_name last_name
    email language
    gsm phone
    country city
    street street_no
    username
    """


class RegisterUser(actions.ShowInsert):
    """Fill a form in order to register as a new system user.

    """

    def get_action_title(self, ar):
        return _("Register new user")


class Register(Users):
    use_as_default_table = False
    insert_layout = RegisterUserLayout()
    # default_list_action_name = 'insert'
    required_roles = set([])

    @classmethod
    def get_insert_action(cls):
        return RegisterUser()


class NewUsers(Users):
    """List of new users to be confirmed by the system admin.

    Confirming a new user basically means to manually set the user
    type.

    """
    label = _("New user applications")
    welcome_message_when_count = 0
    required_roles = dd.login_required(SiteAdmin)
    use_as_default_table = False
    column_names = 'created first_name last_name username user_type workflow_buttons *'
    order_by = ['created']

    send_welcome_email = SendWelcomeMail()

    @classmethod
    def param_defaults(self, ar, **kw):
        kw = super(NewUsers, self).param_defaults(ar, **kw)
        # kw.update(show_closed=dd.YesNo.no)
        kw.update(user_state=UserStates.new)
        return kw
