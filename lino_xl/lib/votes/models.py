# -*- coding: UTF-8 -*-
# Copyright 2016-2017 Rumma & Ko Ltd
#
# License: BSD (see file COPYING for details)
"""
Database models for this plugin.

"""

from __future__ import unicode_literals
from __future__ import print_function
from builtins import str
import six

from django.db import models
from django.conf import settings

from lino.api import dd, rt, _
from lino.core.utils import lazy_format
from etgen.html import E
from lino.utils import join_elems
from lino.mixins import Created, ObservedDateRange
from lino.modlib.users.mixins import UserAuthored, My
from lino.modlib.notify.choicelists import MailModes
from lino_xl.lib.cal.mixins import daterange_text
from lino_xl.lib.working.mixins import Workable

from .roles import VotesUser, VotesStaff
from .choicelists import VoteStates, VoteEvents  # , VoteViews
from .choicelists import Ratings
from .actions import EditVote

config = dd.plugins.votes

@dd.python_2_unicode_compatible
class Vote(UserAuthored, Created, Workable):
    """A **vote** is when a user has an opinion or interest about a given
    ticket (or any other votable).

    .. attribute:: votable

        The ticket (or other votable) being voted.

    .. attribute:: user

        The user who is voting.

    .. attribute:: state

        The state of this vote.  Pointer to :class:`VoteStates
        <lino_xl.lib.votes.choicelists.VoteStates>`.

    .. attribute:: priority

        My personal priority for this ticket.

    .. attribute:: rating

        How the ticket author rates my help on this ticket.

    .. attribute:: remark

        Why I am interested in this ticket.

    .. attribute:: nickname
    
        My nickname for this ticket. Optional. 

        If this is specified, then I get a quicklink to this ticket.

    """
    class Meta:
        app_label = 'votes'
        verbose_name = _("Vote")
        verbose_name_plural = _("Votes")
        abstract = dd.is_abstract_model(__name__, 'Vote')
        unique_together = ('user', 'votable')  # , 'project')

    allow_cascaded_delete = 'votable'

    state = VoteStates.field(
        default=VoteStates.as_callable('invited'))
    votable = dd.ForeignKey(
        dd.plugins.votes.votable_model,
        related_name="votes_by_ticket")
    priority = models.SmallIntegerField(_("Priority"), default=0)
    rating = Ratings.field(blank=True)
    # remark = dd.RichTextField(_("Remark"), blank=True)
    nickname = models.CharField(_("Nickname"), max_length=50, blank=True)
    mail_mode = MailModes.field(blank=True)
    # project = dd.ForeignKey(
    #     'tickets.Project',
    #     related_name="votes_by_project")

    # @dd.action(_("Cancel"))
    # def cancel_vote(self):
    #     self.state = VoteStates.cancelled
        
    # @dd.action(_("Candidate"))
    # def mark_me_as_candidate(self):
    #     self.state = VoteStates.candidate
        
    quick_search_fields = "nickname votable__summary votable__description"
    workflow_state_field = 'state'
    
    edit_vote = EditVote()

    # def full_clean(self):
    #     if not self.project_id:
    #         self.project = self.votable.get_project_for_vote(self)
    #     super(Vote, self).full_clean()

    # @dd.chooser()
    # def project_choices(cls, user):
    #     Project = rt.models.tickets.Project
    #     if not user:
    #         return Project.objects.none()
    #     return Project.objects.filter(duties_by_project__user=user)

    def __str__(self):
        # return _("{0.user} {0.state} on {0.votable}").format(self)
        if self.votable_id:
            return _("{user}'s {vote} on {votable}").format(
                user=self.user,
                # vote=self.state.vote_name,
                vote=self._meta.verbose_name,
                votable=self.votable)
                
        return _("{user}'s {vote} on {votable}").format(
            user=self.user,
            # vote=self.state.vote_name,
            vote=self._meta.verbose_name,
            votable=None)

    def get_ticket(self):
        return self.votable
    
    def disabled_fields(self, ar):
        df = super(Vote, self).disabled_fields(ar)
        if self.votable_id:
            me = ar.get_user()
            if not me.user_type.has_required_roles([VotesStaff]):
                if not me in self.votable.get_vote_raters():
                    df.add('rating')
        return df

    @classmethod
    def setup_parameters(cls, fields):
        fields.update(
            ticket_user=dd.ForeignKey(
                settings.SITE.user_model,
                verbose_name=_("Author"),
                blank=True, null=True,
                help_text=_(
                    "Only rows on votables whose author is this user.")),
            exclude_ticket_user=dd.ForeignKey(
                settings.SITE.user_model,
                verbose_name=_("Exclude author"),
                blank=True, null=True,
                help_text=_(
                    "Only rows on votables whose author is not this user.")),
            # show_todo=dd.YesNo.field(_("To do"), blank=True),
            # vote_view=VoteViews.field(blank=True),
            state=VoteStates.field(
                blank=True, help_text=_("Only rows having this state.")),
            mail_mode=MailModes.field(
                blank=True, help_text=_("Only rows having this mail mode.")))
        fld = config.votable_model._meta.get_field('state')
        hlp = lazy_format(
            _("Only rows whose {model} has this state."),
            model=config.votable_model._meta.verbose_name)
        lbl = lazy_format(
            _("{model} state"),
            model=config.votable_model._meta.verbose_name)
        fields.update(
            votable_state=fld.choicelist.field(
                lbl, blank=True, help_text=hlp))
        super(Vote, cls).setup_parameters(fields)

    @dd.displayfield(_("Description"))
    def votable_overview(self, ar):
        if ar is None or self.votable_id is None:
            return ''
        elems = self.votable.get_overview_elems(ar)
        # elems += [E.br()]
        # # elems += [E.br(), _("{} state:").format(
        # #     self._meta.verbose_name), ' ']
        # elems += self.get_workflow_buttons(ar)
        return E.div(*elems)

    def on_create(self, ar):
        """Set the default vote state,

        """
        if not self.state:
            if ar.get_user() == self.user:
                self.state = VoteStates.watching
            else:
                self.state = VoteStates.invited
        super(Vote, self).on_create(ar)

        

    # def get_author(self):
    def get_row_permission(self, ar, state, ba):
        # we bypass the author check because 
        return dd.Model.get_row_permission(self,ar, state, ba)

dd.update_field(Vote, 'user', verbose_name=_("Voter"))


class Votes(dd.Table):
    """Table parameters:

    .. attribute:: observed_event

        There are two class attributes for defining a filter conditions
        which canot be removed by the user:

    .. attribute:: filter_vote_states

        A set of vote states to require (i.e. to filter upon).  This
        must resolve using :meth:`resolve_states
        <lino.core.model.Model.resolve_states>`.

    .. attribute:: exclude_vote_states

        A set of vote states to exclude.  This must
        resolve using :meth:`resolve_states
        <lino.core.model.Model.resolve_states>`.


    .. attribute:: filter_ticket_states

        A set of ticket states to require (i.e. to filter upon). This
        must resolve using :meth:`resolve_states
        <lino.core.model.Model.resolve_states>`.

    """
    model = 'votes.Vote'
    order_by = ['-id']
    # stay_in_grid = True
    required_roles = dd.login_required(VotesUser)

    parameters = ObservedDateRange(
        observed_event=VoteEvents.field(blank=True))

    params_layout = """
    user mail_mode state votable_state ticket_user
    start_date end_date observed_event exclude_ticket_user"""

    params_panel_hidden = True
    # show_detail_navigator = False
    # hide_top_toolbar = True
    
    detail_layout = dd.DetailLayout("""
    user votable 
    #project
    mail_mode 
    priority nickname
    state
    rating 
    """, window_size=(40, 'auto'))

    filter_vote_states = None
    exclude_vote_states = None
    filter_ticket_states = None

    # @classmethod
    # def on_analyze(self, site):
    #     super(Votes, self).on_analyze(site)
        
    
    @classmethod
    def do_setup(self):
        # print("Votes.to_setup")
        self.filter_vote_states  = self.model.resolve_states(
            self.filter_vote_states)
        self.exclude_vote_states  = self.model.resolve_states(
            self.exclude_vote_states)
        self.filter_ticket_states = config.votable_model.resolve_states(
            self.filter_ticket_states)
        super(Votes, self).do_setup()
        self.detail_action.action.hide_top_toolbar = True

    @classmethod
    def get_detail_title(self, ar, obj):
        """Overrides the default beaviour

        """
        me = ar.get_user()
        pk = obj.votable.pk
        if me == obj.user:
            return _("My vote about #{}").format(pk)
        else:
            return _("{}'s vote about #{}").format(obj.user, pk)

    @classmethod
    def get_simple_parameters(cls):
        s = list(super(Votes, cls).get_simple_parameters())
        s.append('state')
        s.append('mail_mode')
        return s

    @classmethod
    def get_request_queryset(self, ar, **kwargs):
        qs = super(Votes, self).get_request_queryset(ar, **kwargs)
        pv = ar.param_values

        if self.filter_vote_states is not None:
            qs = qs.filter(state__in=self.filter_vote_states)
        if self.exclude_vote_states is not None:
            qs = qs.exclude(state__in=self.exclude_vote_states)
        if self.filter_ticket_states is not None:
            qs = qs.filter(votable__state__in=self.filter_ticket_states)

        if pv.ticket_user:
            qs = qs.filter(votable__user=pv.ticket_user)
        if pv.exclude_ticket_user:
            qs = qs.exclude(votable__user=pv.exclude_ticket_user)
            
        # if pv.show_todo == dd.YesNo.no:
        #     qs = qs.exclude(state__in=VoteStates.todo_states)
        # elif pv.show_todo == dd.YesNo.yes:
        #     qs = qs.filter(state__in=VoteStates.todo_states)

        if pv.observed_event:
            qs = pv.observed_event.add_filter(qs, pv)
        return qs
       
    @classmethod
    def get_title_tags(self, ar):
        pv = ar.param_values
        # if pv.vote_view:
        #     pv.vote_view.text
        for t in super(Votes, self).get_title_tags(ar):
            yield t
        if pv.start_date or pv.end_date:
            yield daterange_text(
                pv.start_date,
                pv.end_date)



class AllVotes(Votes):
    label = _("All votes")
    required_roles = dd.login_required(VotesStaff)
    column_names = "id votable user priority nickname rating mail_mode workflow_buttons *"


# class VotesByProject(Votes):
#     """Show the votes about this project.

#     """
#     label = _("Votes")
#     master_key = 'project'
#     column_names = 'votable user workflow_buttons *'
#     display_mode = 'summary'
#     stay_in_grid = True

    


class MyVotes(My, Votes):
    """Show all my votes."""
    label = _("My votes")
    column_names = "votable_overview workflow_buttons *"
    # hide_top_toolbar = True
    
    detail_layout = dd.DetailLayout("""
    user #project
    workflow_buttons 
    mail_mode
    priority nickname
    """, window_size=(40, 'auto'), hidden_elements='user')
    
    
class MyInvitations(My, Votes):
    """Show my votes in state invited. """
    label = _("My vote invitations")
    column_names = "votable_overview workflow_buttons *"
    order_by = ['-priority', '-id']
    filter_vote_states = "invited"
    # filter_ticket_states = "opened started talk"
    
    
class MyOffers(My, Votes):
    """Show the tickets for which I am candidate"""
    label = _("My candidatures")
    column_names = "votable_overview workflow_buttons *"
    filter_vote_states = "candidate"
    filter_ticket_states = "new talk opened working"
    

class MyTasks(My, Votes):
    """Show my votes in states assigned and done"""
    label = _("My tasks")
    column_names = "votable_overview workflow_buttons *"
    order_by = ['-priority', '-id']
    filter_vote_states = "assigned done"
    filter_ticket_states = "opened working talk"
    
class MyWatched(My, Votes):
    """Show my votes in state watching"""
    label = _("My watchlist")
    column_names = "votable_overview workflow_buttons *"
    filter_vote_states = "watching"
    # filter_ticket_states = "open talk"
    
    @classmethod
    def param_defaults(self, ar, **kw):
        kw = super(MyWatched, self).param_defaults(ar, **kw)
        kw.update(exclude_ticket_user=ar.get_user())
        return kw


class VotesByVotable(Votes):
    """Show the votes about this object.

    """
    label = _("Votes")
    master_key = 'votable'
    column_names = 'user workflow_buttons mail_mode *'
    # show_detail_navigator = False
    # hide_top_toolbar = True
    display_mode = 'summary'
    # exclude_vote_states = 'author'
    stay_in_grid = True

    detail_layout = dd.DetailLayout("""
    #project
    mail_mode 
    # priority nickname
    workflow_buttons 
    rating 
    """, window_size=(40, 'auto'))

    insert_layout = """
    user
    mail_mode 
    workflow_buttons 
    # rating 
    """

    @classmethod
    def get_table_summary(self, obj, ar):
        """Customized :meth:`summary view
        <lino.core.actors.Actor.get_table_summary>` for this table.

        """
        sar = self.request_from(ar, master_instance=obj)

        html = []
        states = {}
        for s, d in VoteStates.choices:
            states[s] = []

        u = ar.get_user()

        for o in sar:
            states[o.state].append(ar.obj2html(o, o.user.initials or str(o.user), title=o.state))
            if u == o.user:
                html.insert(0, E.span(
                    E.b(str(o.state)),
                    u" \u2192 ",
                    *join_elems([sar.action_button(ba, o) for ba in sar.actor.get_actions()
                                 if ba.action.show_in_workflow and
                                 sar.actor.get_row_permission(o, sar, o.state, ba) and
                                 isinstance(ba.action, dd.ChangeStateAction)],
                                " ")
                ))


        html.append(E.ul(
            *[E.li(*([str(s.text),  ": "] + join_elems(states[s], sep=", "))) for s, c in VoteStates.choices
              if states[s]
              ]
        ))
        # print(tostring(html))
        # items = [
        #     ar.obj2html(o, o.user.username or str(o.user))
        #     for o in rt.models.votes.Vote.objects.filter(
        #             votable=obj).order_by('-id')]
        # sar.get_user() == v.user
        sar = self.insert_action.request_from(sar)
        if sar.get_permission():
            # btn = sar.ar2button(None, _("Add voter"), icon_name=None)
            btn = sar.ar2button()
            # btn = sar.ar2button(None, u"⏍", icon_name=None)  # 23CD SQUARE FOOT
            # btn = sar.ar2button(None, u"⊞", icon_name=None) # 229e SQUARED PLUS
            
            html.append(E.div(btn))

            
        return ar.html_text(E.div(*html))

    

# class MyOfferedVotes(MyVotes):
#     """List of my help offers to other users' requests.

#     Only those which need my attention. 

#     """
    
#     column_names = "votable state priority rating nickname *"
#     order_by = ['-id']
    
# class MyRequestedVotes(MyVotes):
#     """List of other user's help offers on my requests. 

#     Only those which need my attention. 

#     """
#     column_names = "votable state priority rating nickname *"
#     order_by = ['-id']
    



def welcome_messages(ar):
    """Yield a message "Your favourites are X, Y, ..." for the welcome
page.

    This message mentions all voted objects of the requesting user
    and whose :attr:`nickname <Vote.nickname>` is not empty.

    """
    Vote = rt.models.votes.Vote
    qs = Vote.objects.filter(user=ar.get_user()).exclude(nickname='')
    qs = qs.order_by('priority')
    if qs.count() > 0:
        chunks = [six.text_type(_("Your favourite {0} are ").format(
            config.votable_model._meta.verbose_name_plural))]
        chunks += join_elems([
            ar.obj2html(obj.votable, obj.nickname)
            for obj in qs])
        chunks.append('.')
        yield E.span(*chunks)

dd.add_welcome_handler(welcome_messages)

