# -*- coding: UTF-8 -*-
# Copyright 2016-2018 Rumma & Ko Ltd
# License: BSD (see file COPYING for details)

"""

Import legacy data from TIM (including households, ...).
An extension of :mod:`tim2lino <lino_xl.lib.tim2lino.tim2lino>`.


"""
from __future__ import unicode_literals
import datetime

from builtins import str

# from lino.utils import mti
from lino.api import dd, rt, _
from lino.utils.instantiator import create
from django.core.exceptions import ValidationError

from .timloader1 import TimLoader

Person = dd.resolve_model("contacts.Person")
Company = dd.resolve_model("contacts.Company")
RoleType = dd.resolve_model("contacts.RoleType")
Role = dd.resolve_model("contacts.Role")
Household = rt.models.households.Household
Product = dd.resolve_model('products.Product')
# List = dd.resolve_model('lists.List')
Client = rt.models.tera.Client
Course = rt.models.courses.Course
Line = rt.models.courses.Line
CourseAreas = rt.models.courses.CourseAreas
Course = rt.models.courses.Course
Enrolment = rt.models.courses.Enrolment
Event = rt.models.cal.Event
Account = dd.resolve_model('ledger.Account')

working = dd.resolve_app('working')

User = rt.models.users.User
Note = rt.models.notes.Note
UserTypes = rt.models.users.UserTypes
Partner = rt.models.contacts.Partner
# Coaching = rt.models.coachings.Coaching

# lists_Member = rt.models.lists.Member
households_Member = rt.models.households.Member
households_MemberRoles = rt.models.households.MemberRoles


class TimLoader(TimLoader):

    # archived_tables = set('GEN ART VEN VNL JNL FIN FNL'.split())
    # archive_name = 'rumma'
    # has_projects = False
    # languages = 'de fr'
    
    def __init__(self, *args, **kwargs):
        super(TimLoader, self).__init__(*args, **kwargs)
        self.imported_sessions = set([])
        self.obsolete_list = []
        # LinkTypes = rt.models.humanlinks.LinkTypes
        # plptypes = dict()
        # plptypes['01'] = LinkTypes.parent
        # plptypes['01R'] = None
        # plptypes['02'] = LinkTypes.uncle
        # plptypes['02R'] = None
        # plptypes['03'] = LinkTypes.stepparent
        # plptypes['03R'] = None
        # plptypes['04'] = LinkTypes.grandparent
        # plptypes['04R'] = None
        # plptypes['10'] = LinkTypes.spouse
        # plptypes['11'] = LinkTypes.friend
        # self.linktypes = plptypes
        
        
    def get_users(self, row):
        for idusr in (row.idusr2, row.idusr1, row.idusr3):
            user = self.get_user(idusr)
            if user is not None:
                yield user

    def par_pk(self, pk):
        try:
            if pk.startswith('E'):
                return 1000000 + int(pk[1:])
            elif pk.startswith('S'):
                return 2000000 + int(pk[1:])
            return int(pk)
        except ValueError:
            return None

    def par_class(self, data):
        prt = data.idprt
        if prt == 'L':  # Lieferant
            return Company
        elif prt == 'K':  # Krankenkasse
            return Company
        elif prt == 'S':  # Sonstige
            return Company
        elif prt == 'W':  # Netzwerkpartner
            return Company
        elif prt == 'R':  # Ärzte
            return Person
        elif prt == 'Z':  # Zahler
            return Company
        elif prt == 'P':  # Personen
            return Client
        elif prt == 'G':  # Lebensgruppen
            return Household
        elif prt == 'T':  # Therapeutische Gruppen
            return Household  # List
        #~ dblogger.warning("Unhandled PAR->IdPrt %r",prt)

    def load_par(self, row):
        for obj in super(TimLoader, self).load_par(row):
            if row.idpar.startswith('E'):
                obj.team = self.eupen
            elif row.idpar.startswith('S'):
                obj.team = self.stvith
            # idpar2 = row.idpar2.strip()
            # if idpar2 and row.idpar != idpar2:
            #     self.obsolete_list.append(
            #         (obj, self.par_pk(idpar2)))
            # if isinstance(obj, Partner):
            #     obj.isikukood = row['regkood'].strip()
            #     obj.created = row['datcrea']
            #     obj.modified = datetime.datetime.now()
            name = row.firme.strip()
            if row.name2.strip():
                name += "-" + row.name2.strip()
            name += ' ' + row.vorname.strip()
            prt = row.idprt
            if prt == "T":
                # if Course.objects.filter(id=obj.id).exists():
                #     return
                # if Course.objects.filter(ref=row.idpar.strip()).exists():
                #     return
                kw = dict(name=name, line=self.other_groups, id=obj.id)
                kw.update(ref=row.idpar.strip())
                for user in self.get_users(row):
                    kw.update(teacher=user)
                    break
                yield Course(**kw)
                return
            
            yield obj
            
            if prt == "G":
                # if Course.objects.filter(id=obj.id).exists():
                #     return
                # if Course.objects.filter(ref=row.idpar.strip()).exists():
                #     return
                kw = dict(
                    name=name, line=self.life_groups, id=obj.id,
                    partner_id=obj.id)
                kw.update(ref=row.idpar.strip())
                for user in self.get_users(row):
                    kw.update(teacher=user)
                    break
                yield Course(**kw)
                return
            if prt == "P":
                for user in self.get_users(row):
                    # if Course.objects.filter(id=obj.id).exists():
                    #     return
                    # if Course.objects.filter(ref=row.idpar.strip()).exists():
                    #     return
                    therapy = Course(
                        line=self.therapies,
                        partner_id=obj.id,
                        name=name, teacher=user, id=obj.id,
                        ref=row.idpar.strip())
                    yield therapy
                    kw = dict()
                    if row.date1:
                        kw.update(start_date=row.date1)
                        if row.date2 and row.date2 > row.date1:
                            # avoid "Date period ends before it started."
                            kw.update(end_date=row.date2)
                    yield Enrolment(pupil=obj, course=therapy, **kw)
                    return
            else:
                dd.logger.warning(
                    "No coaching for non-client %s", obj)

    # def load_pls(self, row, **kw):
    #     kw.update(ref=row.idpls.strip())
    #     kw.update(name=row.name)
    #     return List(**kw)

    def get_user(self, idusr=None):
        try:
            return User.objects.get(username=idusr.strip().lower())
        except User.DoesNotExist:
            return None

    def create_users(self):
        pass
        
    def load_usr(self, row, **kw):
        kw.update(username=row.userid.strip().lower())
        kw.update(first_name=row.name.strip())
        abtlg = row.abtlg.strip()
        if abtlg == 'E':
            kw.update(team=self.eupen)
        elif abtlg == 'S':
            kw.update(team=self.stvith)
        kw.update(user_type=UserTypes.admin)
        o = User(**kw)
        o.set_password("1234")
        return o

    def get_partner(self, model, idpar):
        pk = self.par_pk(idpar.strip())
        try:
            return model.objects.get(pk=pk)
        except model.DoesNotExist:
            return None
    
    def load_plp(self, row, **kw):
        # Link = rt.models.humanlinks.Link
        # LinkTypes = rt.models.humanlinks.LinkTypes

        plptype = row.type.strip()
        if plptype.endswith("-"):
            return
        if not plptype:
            return
        if plptype[0] in "01":
            if not plptype in self.linktypes:
                dd.logger.warning(
                    "Ignored PLP %s : Invalid type %s", row, plptype)
                return
            linktype = self.linktypes.get(plptype)
            if linktype is None:
                # silently ignore reverse PLPType
                return
            
            p1 = self.get_partner(Person, row.idpar1)
            if p1 is None:
                dd.logger.debug(
                    "Ignored PLP %s : Invalid idpar1", row)
                return
            p2 = self.get_partner(Person, row.idpar2)
            if p2 is None:
                dd.logger.debug(
                    "Ignored PLP %s : Invalid idpar2", row)
                return
            yield Link(parent=p1, child=p2, type=linktype)
        
        elif plptype == "80":
            # p1 = self.get_partner(List, row.idpar1)
            p1 = self.get_partner(Course, row.idpar1)
            if p1 is None:
                dd.logger.debug(
                    "Ignored PLP %s : Invalid idpar1", row)
                return
            p2 = self.get_partner(Client, row.idpar2)
            if p2 is None:
                dd.logger.debug(
                    "Ignored PLP %s : Invalid idpar2", row)
                return
            # return lists_Member(list=p1, partner=p2)
            yield Enrolment(course=p1, pupil=p2, state='confirmed')  # 

        elif plptype[0] in "78":
            p1 = self.get_partner(Household, row.idpar1)
            if p1 is None:
                dd.logger.warning(
                    "Ignored PLP %s : Invalid idpar1", row)
                return
            p2 = self.get_partner(Client, row.idpar2)
            if p2 is None:
                dd.logger.warning(
                    "Ignored PLP %s : Invalid idpar2", row)
                return
            if plptype == "81":
                role = households_MemberRoles.spouse
            elif plptype == "82":
                role = households_MemberRoles.child
            elif plptype == "83":
                role = households_MemberRoles.partner
            elif plptype == "84":
                role = households_MemberRoles.other
            elif plptype == "71":  # Onkel/Tante
                role = households_MemberRoles.relative
            elif plptype == "72":  # Nichte/Neffe
                role = households_MemberRoles.relative
            else:
                role = households_MemberRoles.relative
            yield households_Member(household=p1, person=p2, role=role)
            
            p1 = self.get_partner(Course, row.idpar1)
            if p1 is None:
                dd.logger.warning(
                    "Ignored PLP %s : no course for idpar1", row)
                return
            yield Enrolment(course=p1, pupil=p2, remark=str(role),
                            state='confirmed')
        elif plptype == "81-":
            return
        dd.logger.debug(
            "Ignored PLP %s : invalid plptype", row)


    def unused_load_dls(self, row, **kw):
        if not row.iddls.strip():
            return
        # if not row.idpin.strip():
        #     return
        pk = row.iddls.strip()
        idusr = row.idusr.strip()
        if pk.startswith('E'):
            team = self.eupen
            pk = int(pk[1:])
        elif pk.startswith('S'):
            team = self.stvith
            pk = int(pk[1:]) + 1000000

        if pk in self.imported_sessions:
            dd.logger.warning(
                "Cannot import duplicate session %s", pk)
            return
        self.imported_sessions.add(pk)
        u = self.get_user(idusr)
        if u is None:
            dd.logger.warning(
                "Cannot import session %s because there is no user %s",
                pk, idusr)
            return
        
        if u.team != team:
            u1 = u
            idusr += '@' + str(team.pk)
            try:
                u = User.objects.get(username=idusr)
            except User.DoesNotExist:
                u = create(
                    User, username=idusr, first_name=u1.first_name, team=team,
                    user_type=u1.user_type)
            
        kw.update(user=u)
        kw.update(id=pk)
        # if row.idprj.strip():
        #     kw.update(project_id=int(row.idprj))
            # kw.update(partner_id=PRJPAR.get(int(row.idprj),None))
        if row.idpar.strip():
            idpar = self.par_pk(row.idpar.strip())
            try:
                ticket = Partner.objects.get(id=idpar)
                kw.update(ticket=ticket)
            except Partner.DoesNotExist:
                dd.logger.warning(
                    "Cannot import session %s because there is no partner %d",
                    pk, idpar)
                return
                
        kw.update(summary=row.nb.strip())
        kw.update(start_date=row.date)

        def set_time(kw, fldname, v):
            v = v.strip()
            if not v:
                return
            if v == '24:00':
                v = '0:00'
            kw[fldname] = v

        set_time(kw, 'start_time', row.von)
        set_time(kw, 'end_time', row.bis)
        # set_time(kw, 'break_time', row.pause)
        # kw.update(start_time=row.von.strip())
        # kw.update(end_time=row.bis.strip())
        # kw.update(break_time=row.pause.strip())
        # kw.update(is_private=tim2bool(row.isprivat))
        obj = working.Session(**kw)
        # if row.idpar.strip():
            # partner_id = self.par_pk(row.idpar)
            # if obj.project and obj.project.partner \
                # and obj.project.partner.id == partner_id:
                # pass
            # elif obj.ticket and obj.ticket.partner \
                # and obj.ticket.partner.id == partner_id:
                # pass
            # else:
                # ~ dblogger.warning("Lost DLS->IdPar of DLS#%d" % pk)
        yield obj
        # if row.memo.strip():
        #     kw = dict(owner=obj)
        #     kw.update(body=self.dbfmemo(row.memo))
        #     kw.update(user=obj.user)
        #     kw.update(date=obj.start_date)
        #     yield rt.models.notes.Note(**kw)

    def finalize(self):
        dd.logger.info("Deleting %d obsolete partners", len(self.obsolete_list))
        for (par1, idpar2) in self.obsolete_list:
            par2 = None
            try:
                par2 = Client.objects.get(id=idpar2)
            except Client.DoesNotExist:
                try:
                    par2 = Household.objects.get(id=idpar2)
                except Household.DoesNotExist:
                    pass
                
            if par2 is None:
                continue

            def replace(model, k, delete=False):
                for obj in model.objects.filter(**{k: par1}):
                    setattr(obj, k, par2)
                    try:
                        obj.full_clean()
                        obj.save()
                    except ValidationError as e:
                        if delete:
                            obj.delete()
                        else:
                            dd.logger.warning(
                                "Couldn't change obsolete %s to %s: %s",
                                k, par2, e)

            # replace(Coaching, 'client')

            if isinstance(par1, Person):
                replace(Enrolment, 'pupil', True)
                replace(rt.models.households.Member, 'person')
                #replace(rt.models.humanlinks.Link, 'parent')
                #replace(rt.models.humanlinks.Link, 'child')
                replace(rt.models.cal.Guest, 'partner', True)
                replace(rt.models.clients.ClientContact, 'client')

            if isinstance(par1, Client):
                replace(Course, 'partner')

            if isinstance(par1, Household):
                if isinstance(par2, Household):
                    replace(Course, 'partner')

            try:
                par1.delete()
            except Exception as e:
                par1.obsoletes = par2
                par1.full_clean()
                par1.save()
                dd.logger.warning("Failed to delete {} : {}".format(
                    par1, e))
                
        super(TimLoader, self).finalize()

        dd.logger.info("Deleting dangling individual therapies")
        # if there is exactly one therapy for a patient, and if that
        # therapy has only one enrolment, and if that patient has
        # enrolments in other therapies as well, then the therapy is
        # useless
        
        for p in Client.objects.all():
            qs = Course.objects.filter(partner=p)
            if qs.count() == 1:
                et = qs[0]
                if Note.objects.filter(project=et).count():
                    continue
                if Event.objects.filter(project=et).count():
                    continue
                qs = Enrolment.objects.filter(pupil=p)
                qs = qs.exclude(course=et)
                if qs.count() > 0:
                    qs = Enrolment.objects.filter(course=et)
                    if qs.count() == 1:
                        Enrolment.objects.filter(course=et).delete()
                        et.delete()
        
                
    def objects(self):

        Team = rt.models.teams.Team
        Country = rt.models.countries.Country
        self.eupen = create(Team, name="Eupen")
        yield self.eupen
        self.stvith = create(Team, name="St. Vith")
        yield self.stvith
        
        yield Country(isocode='LU', **dd.str2kw('name', _("Luxemburg")))
        yield Country(isocode='PL', **dd.str2kw('name', _("Poland")))
        yield Country(isocode='AU', **dd.str2kw('name', _("Austria")))
        yield Country(isocode='US', short_code='USA',
                      **dd.str2kw('name', _("United States")))
        yield self.load_dbf('USR')
        
        yield super(TimLoader, self).objects()

        yield self.load_dbf('PLP')

        if False:
            yield self.load_dbf('DLS')
            
