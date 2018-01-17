# -*- coding: UTF-8 -*-
# Copyright 2017 Luc Saffre
# License: BSD (see file COPYING for details)

"""
Import legacy data from TIM (second step). 

Much legacy data is already in Lino, (first imported by
:mod:`spzloader` and then manually reviewed), now we parse the legacy
database once more, adding more data.

- import DLS.DBF as calendar entries
- import DLP.DBF as calendar guests
- Therapie E130280 : nicht Harry sondern Daniel müsste Therapeut
  sein. Falsch importiert.
- No de GSM, Date naissance, Geschlecht n'ont pas été importés
- Rechnungsempfänger und Krankenkasse importieren : pro Patient, nicht
  pro Einschreibung.

"""
from __future__ import unicode_literals
from builtins import str

import datetime
from dateutil import parser as dateparser

from django.core.exceptions import ValidationError

# from lino.utils import mti
from lino.utils.instantiator import create_row
from lino.utils.instantiator import create
from lino.utils.mti import mtichild
from lino.core.gfks import gfk2lookup

from lino.api import dd, rt, _


from .spzloader import TimLoader
from .timloader1 import convert_gender

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
Enrolment = rt.models.courses.Enrolment

Account = dd.resolve_model('accounts.Account')

working = dd.resolve_app('working')

User = rt.models.users.User
UserTypes = rt.models.users.UserTypes
Partner = rt.models.contacts.Partner
# Coaching = rt.models.coachings.Coaching

# lists_Member = rt.models.lists.Member
households_Member = rt.models.households.Member
Link = rt.models.humanlinks.Link
LinkTypes = rt.models.humanlinks.LinkTypes
households_MemberRoles = rt.models.households.MemberRoles


class TimLoader(TimLoader):

    # archived_tables = set('GEN ART VEN VNL JNL FIN FNL'.split())
    # archive_name = 'rumma'
    # has_projects = False
    # languages = 'de fr'
    
    def __init__(self, *args, **kwargs):
        super(TimLoader, self).__init__(*args, **kwargs)
        Line = rt.models.courses.Line
        Team = rt.models.teams.Team
        # Country = rt.models.countries.Country
        self.eupen = Team.objects.get(name="Eupen")
        self.stvith = Team.objects.get(name="St. Vith")

        Line = rt.models.courses.Line
        self.other_groups = Line.objects.filter(
            course_area=CourseAreas.default).order_by('id')[0]
        
        
        self.imported_sessions = set([])
        # self.obsolete_list = []
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
        # a = CourseAreas.default
        # self.other_groups = create_row(Line, name=a.text, course_area=a)
        # a = CourseAreas.life_groups
        # self.life_groups = create_row(Line, name=a.text, course_area=a)
        # a = CourseAreas.therapies
        # self.therapies = create_row(Line, name=a.text, course_area=a)
        
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
        kw = dict()
        pk = self.par_pk(row.idpar)
        if row.gsm:
            self.store(kw, gsm=row.gsm)
            
        cl = self.par_class(row)
        if cl is None:
            dd.logger.info("Cannot handle %s : par_class is None", row)
            return
        if issubclass(cl, Person):
            v = row.gebdat
            if isinstance(v, basestring):
                self.store(
                    kw, birth_date=dateparser.parse(v.strip()))
            v = row.sexe
            if v:
                self.store(
                    kw, gender=convert_gender(v))

        if not kw:
            return
        try:
            obj = cl.objects.get(pk=pk)
        except cl.DoesNotExist:
            dd.logger.info("%s %s does not exist", cl, pk)
            return
        dd.logger.info("Updating %s : %s", obj, kw)
        for k, v in kw.items():
            setattr(obj, k, v)
        yield obj
        

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
        
    def get_partner(self, model, idpar):
        pk = self.par_pk(idpar.strip())
        try:
            return model.objects.get(pk=pk)
        except model.DoesNotExist:
            return None
    
    def load_dlp(self, row, **kw):
        Event = rt.models.cal.Event
        Guest = rt.models.cal.Guest
        pk = row.iddls.strip()
        if not pk:
            return
        if pk.startswith('E'):
            pk = int(pk[1:])
        elif pk.startswith('S'):
            pk = int(pk[1:]) + 100000

        try:
            kw.update(event=Event.objects.get(pk=pk))
        except Event.DoesNotExist:
            dd.logger.warning("Unknown DLP->IdDls %s", pk)
            return
        
        idpar = row.idpar.strip()
        p = self.get_partner(Person, idpar)
        if p is None:
            co = self.get_partner(Company, idpar)
            if co:
                p = mtichild(co.partner_ptr, Person, last_name=co.name)
            else:
                try:
                    course = Course.get_by_ref(idpar)
                except Course.DoesNotExist:
                    dd.logger.warning("Unknown DLP->IdPar %s", idpar)
                    return
                if not course.partner:
                    dd.logger.warning(
                        "Failed to import DLP %s : course has no partner", pk)
                    return
                p = course.partner.person

        kw.update(partner=p)
        o = Guest(**kw)
        try:
            o.full_clean()
        except ValidationError as e:
            dd.logger.warning("Failed to import DLP %s : %s", o, e)
            return
        yield o
                

    def load_dls(self, row, **kw):
        Course = rt.models.courses.Course
        Event = rt.models.cal.Event
        pk = row.iddls.strip()
        # if not row.idpin.strip():
        #     return
        if pk.startswith('E'):
            team = self.eupen
            pk = int(pk[1:])
        elif pk.startswith('S'):
            team = self.stvith
            pk = int(pk[1:]) + 100000
        if not pk:
            return

        if pk in self.imported_sessions:
            dd.logger.warning(
                "Cannot import duplicate session %s", pk)
            return
        idusr = row.idusr.strip()
        u = self.get_user(idusr)
        if u is None:
            dd.logger.warning(
                "Cannot import session %s because there is no user %s",
                pk, idusr)
            return
        
        if u.team != team:
            u1 = u
            # idusr += '@' + str(team.pk)
            idusr += '@' + str(team)
            try:
                u = User.objects.get(username=idusr)
            except User.DoesNotExist:
                u = create(
                    User, username=idusr, first_name=u1.first_name, team=team,
                    user_type=u1.user_type)
                dd.logger.info("Created new user %s", u)
            
        kw.update(user=u)
        kw.update(id=pk)
        # if row.idprj.strip():
        #     kw.update(project_id=int(row.idprj))
            # kw.update(partner_id=PRJPAR.get(int(row.idprj),None))
        idpar = row.idpar.strip()
        if not idpar:
            dd.logger.info("Missing IdPar in DLS:%s", pk)
            return
        try:
            course = Course.get_by_ref(idpar)
        except Course.DoesNotExist:
            course = Course(
                ref=idpar, line=self.other_groups)
            dd.logger.info("Created new therapy %s", course)
            yield course
            
        self.imported_sessions.add(pk)
        kw.update(**gfk2lookup(Event.owner, course))
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
        obj = Event(**kw)
        yield obj

                
    def objects(self):

        
        # yield Country(isocode='LU', **dd.str2kw('name', _("Luxemburg")))
        # yield Country(isocode='PL', **dd.str2kw('name', _("Poland")))
        # yield Country(isocode='AU', **dd.str2kw('name', _("Austria")))
        # yield Country(isocode='US', short_code='USA',
        #               **dd.str2kw('name', _("United States")))
        # yield self.load_dbf('USR')
        
        # yield super(TimLoader, self).objects()

        # yield self.load_dbf('PLP')

        if False:  # temporarily deactivaed
            Event = rt.models.cal.Event
            Event.objects.all().delete()
            yield self.load_dbf('DLS')
        
            Guest = rt.models.cal.Guest
            Guest.objects.all().delete()
            yield self.load_dbf('DLP')
            
        yield self.load_dbf('PAR')
            