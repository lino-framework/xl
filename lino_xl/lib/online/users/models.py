# -*- coding: UTF-8 -*-
# Copyright 2015-2020 Rumma & Ko Ltd
# License: GNU Affero General Public License v3 (see file COPYING for details)
"""Database models for this plugin.

"""

from lino.api import dd, rt, _

contacts = dd.resolve_app('contacts')
Person = contacts.Person

from lino.modlib.users.models import *

from .choicelists import UserStates

import random
import string

def id_generator(size=6, chars=string.ascii_uppercase + string.digits):
    # thanks to http://stackoverflow.com/questions/2257441/random-string-generation-with-upper-case-letters-and-digits-in-python
    return ''.join(random.SystemRandom().choice(chars) for _ in range(size))

from lino.core.actions import SubmitInsert


class CheckedSubmitInsert(SubmitInsert):
    """Like the standard :class:`lino.core.actions.SubmitInsert`, but
    checks certain things before accepting the new user.

    """
    def run_from_ui(self, ar, **kw):
        obj = ar.create_instance_from_request()
        qs = obj.__class__.objects.filter(username=obj.username)
        if len(qs) > 0:
            msg = _("The username {} is taken. "
                    "Please choose another one").format(obj.username)

            ar.error(msg)
            return

        def ok(ar2):
            SubmitInsert.run_from_ui(self, ar, **kw)
            # self.save_new_instance(ar2, obj)
            ar2.success(_("Your request has been registered. "
                          "An email will shortly be sent to {0}"
                          "Please check your emails.").format(
                              obj.email))
            # ar2.set_response(close_window=True)
            # logger.info("20140512 CheckedSubmitInsert")

        ok(ar)


class VerifyUser(dd.Action):
    """Enter your verification code."""
    label = _("Verify")
    # http_method = 'POST'
    # select_rows = False
    # default_format = 'json'
    required_roles = set([])
    # required_roles = dd.login_required(SiteAdmin)
    show_in_bbar = False
    show_in_workflow = True
    parameters = dict(
        email=models.EmailField(_('e-mail address')),
        verification_code=models.CharField(
            _("Verification code"), max_length=50))
    params_layout = """
    email
    # instruct
    verification_code
    """
    # def get_action_title(self, ar):
    #     return _("Register new user")

    # @dd.constant()
    # def instruct(self, *args):
    #     return _("Enter the verification code you received.")

    def get_action_permission(self, ar, obj, state):
        if not obj.verification_code:
            return False
        return super(
            VerifyUser, self).get_action_permission(ar, obj, state)

    def run_from_ui(self, ar, **kw):
        assert len(ar.selected_rows) == 1
        user = ar.selected_rows[0]
        pv = ar.action_param_values
        # qs = rt.models.users.User.objects.exclude(verification_code='')
        # try:
        #     user = qs.get(email=pv.email)
        # except Exception:
        #     msg = _("Invalid email address")
        #     return ar.error(msg)
        if user.verification_code != pv.verification_code:
            msg = _("Invalid verification code")
            return ar.error(msg)
        user.verification_code = ''
        user.save()
        ar.success(_("User {} is now verified.").format(user))



#
#class User(User, Phonable, AddressLocation):
class User(User, Person):

    """
    Adds the following database fields to the User model.

    .. attribute:: callme_mode

        Whether other users can see my contact data.

    .. attribute:: verification_code

        A random string set for every new user. Used for
        online_registration.

    .. attribute:: user_state

        The registration state of this user.

    """

    workflow_state_field = 'user_state'

    class Meta(User.Meta):
        app_label = 'users'
        abstract = dd.is_abstract_model(__name__, 'User')

    callme_mode = models.BooleanField(
        _('Others may contact me'), default=True)

    verification_code = models.CharField(max_length=200, blank=True)

    user_state = UserStates.field(default=UserStates.as_callable('new'))

    submit_insert = CheckedSubmitInsert()
    verify = VerifyUser()

    # partner = dd.DummyField()

    def get_person(self):
        return self

    def on_create(self, ar):
        self.verification_code = id_generator(12)
        return super(User, self).on_create(ar)

    def get_detail_action(self, ar):
        a = super(User, self).get_detail_action(ar)
        if a is not None:
            return a
        if self.callme_mode:
            a = rt.models.users.OtherUsers.detail_action
        if a is not None and a.get_view_permission(ar.get_user().user_type):
            return a

    @dd.htmlbox(_("About me"))
    def about_me(self, ar):
        return self.remarks

    @classmethod
    def get_simple_parameters(cls):
        s = list(super(User, cls).get_simple_parameters())
        s.append('user_state')
        return s

    # def get_default_table(self, ar):
    #     tbl = super(User, self).get_default_table(ar)
    #     return rt.models.users.OtherUsers

    # def __str__(self):
    #     s = self.get_full_name()
    #     if self.callme_mode:
    #         if self.tel:
    #             s += " ({})".format(self.tel)
    #     return s


dd.update_field('users.User', 'remarks', verbose_name=_("About me"))
