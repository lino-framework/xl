# -*- coding: UTF-8 -*-
# Copyright 2017-2018 Rumma & Ko Ltd
# License: BSD (see file COPYING for details)

"""
Import legacy data from TIM (second step). 

Much legacy data is already in Lino (first imported by
:mod:`spzloader` and then manually reviewed and maintained), now we
parse the legacy database once more, adding more data:

- import DLS.FOX as calendar entries
- import DLP.FOX as calendar guests
- import certain fields from PAR.FOX

This loader deletes all existing calendar entries and presences before
importing them from TIM.

In the project direcory on their production server I have a script
:file:`tl2.py`::

    from lino_xl.lib.tim2lino.spzloader2 import TimLoader
    from django.core.mail import mail_admins
    TimLoader.run()
    mail_admins("TimLoader2 done", "tl2.py has finished")

That script runs for quite some time. So I invoke it using nohup to
avoid having it killed when my terminal closes::

    $ nohup python manage.py run tl2.py &
    [1] 18804
    $ nohup: ignoring input and appending output to ‘nohup.out’

I can afterwards check that the process is running::

    $ ps -uf
    USER       PID %CPU %MEM    VSZ   RSS TTY      STAT START   TIME COMMAND
    lsaffre  18576  0.0  0.2  23424  5380 pts/0    Ss   04:11   0:00 -bash
    lsaffre  18804 88.6 40.9 1029360 843084 pts/0  R    04:20   8:27  \_ python manage.py run tl2.py
    lsaffre  18881  0.0  0.1  19100  2508 pts/0    R+   04:29   0:00  \_ ps -uf
  
I can also watch the :xfile:`lino.log` while the script is running.

And when the script has finished, I can see the results in the
:xfile:`nohup.out` file. Also in :xfile:`lino.log`.
"""
from __future__ import unicode_literals
from builtins import str

import datetime
from dateutil import parser as dateparser

from django.core.exceptions import ValidationError
from django.db import DEFAULT_DB_ALIAS

# from lino.utils import mti
from lino.utils.instantiator import create_row
from lino.utils.instantiator import create
from lino.utils.mti import mtichild, insert_child
from lino.core.gfks import gfk2lookup

from lino.api import dd, rt, _


from .spzloader import TimLoader
from .timloader1 import convert_gender

Person = dd.resolve_model("contacts.Person")
# Company = dd.resolve_model("contacts.Company")
RoleType = dd.resolve_model("contacts.RoleType")
Role = dd.resolve_model("contacts.Role")
Household = rt.models.households.Household
Product = dd.resolve_model('products.Product')
# List = dd.resolve_model('lists.List')
Client = rt.models.tera.Client
ClientContact = rt.models.clients.ClientContact
Course = rt.models.courses.Course
Line = rt.models.courses.Line
CourseAreas = rt.models.courses.CourseAreas
Enrolment = rt.models.courses.Enrolment
Country = rt.models.countries.Country

Account = dd.resolve_model('accounts.Account')

working = dd.resolve_app('working')

User = rt.models.users.User
UserTypes = rt.models.users.UserTypes
Partner = rt.models.contacts.Partner
Company = rt.models.contacts.Company
# Coaching = rt.models.coachings.Coaching

# lists_Member = rt.models.lists.Member
households_Member = rt.models.households.Member
Link = rt.models.humanlinks.Link
LinkTypes = rt.models.humanlinks.LinkTypes
households_MemberRoles = rt.models.households.MemberRoles

List = rt.models.lists.List
Member = rt.models.lists.Member
Topic = rt.models.topics.Topic
Interest = rt.models.topics.Interest
Note = rt.models.notes.Note
Guest = rt.models.cal.Guest
Event = rt.models.cal.Event



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
                
            v = row.beruf
            if v:
                v = rt.models.tera.ProfessionalStates.get_by_value(v)
                self.store(kw, professional_state=v)
                
        if issubclass(cl, Client):
            v = row.idnat
            if v:
                try:
                    obj = Country.objects.get(isocode=v)
                except Country.DoesNotExist:
                    obj = create(Country, name=v, isocode=v)
                    yield obj
                    dd.logger.info("Inserted new country %s ", v)
                    return
                self.store(kw, nationality=obj)
            
        if issubclass(cl, (Client, Household)):
            
            v = self.get_partner(Partner, row.zahler)
            if v:
                kw.update(invoice_recipient=v)
            
            v = row.tarif
            if v:
                v = rt.models.tera.PartnerTariffs.get_by_value(v)
                self.store(kw, tariff=v)

            ClientStates = rt.models.clients.ClientStates
            v = row.stand
            if v:
                v = ClientStates.get_by_value(v)
            if v:
                self.store(kw, client_state=v)
            else:
                self.store(
                    kw, client_state=ClientStates.auto_closed)
                dd.logger.info(
                    "%s : invalid PAR->Stand %s", row, row.stand)
                return

        if not kw:
            return
        try:
            obj = cl.objects.get(pk=pk)
        except cl.DoesNotExist:
            try:
                obj = Partner.objects.get(pk=pk)
            except Partner.DoesNotExist:
                dd.logger.info("Create new %s %s from %s (**%s)",
                               cl.__name__, pk, row, kw)
                # yield cl(**kw)
                for obj in super(TimLoader, self).load_par(row):
                    if isinstance(obj, cl):
                        for k, v in kw.items():
                            setattr(obj, k, v)
                    yield obj
                return
            dd.logger.info("Insert MTI child %s : %s", obj, kw)
            insert_child(obj, cl, True, **kw)
            # dd.logger.info("%s %s does not exist", cl, pk)
            return
        dd.logger.info("Update existing %s : %s", obj, kw)
        for k, v in kw.items():
            setattr(obj, k, v)
        yield obj

        v = self.get_partner(Company, row.kkasse)
        if v:
            cct = rt.models.clients.ClientContactType.objects.get(pk=1)
            yield rt.models.clients.ClientContact(
                type=cct, client=obj, company=v)
        
        v = self.get_partner(Person, row.hausarzt)
        if v:
            cct = rt.models.clients.ClientContactType.objects.get(pk=2)
            yield rt.models.clients.ClientContact(
                type=cct, client=obj, contact_person=v)
        

    # def load_pls(self, row, **kw):
    #     kw.update(ref=row.idpls.strip())
    #     kw.update(name=row.name)
    #     return List(**kw)

    def get_partner(self, model, idpar):
        pk = self.par_pk(idpar.strip())
        try:
            return model.objects.get(pk=pk)
        except model.DoesNotExist:
            return None
    
    def load_dlp(self, row, **kw):
        pk = row.iddls.strip()
        if not pk:
            return
        if pk.startswith('E'):
            pk = int(pk[1:])
        elif pk.startswith('S'):
            pk = int(pk[1:]) + 1000000

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
        pk = row.iddls.strip()
        # if not row.idpin.strip():
        #     return
        if pk.startswith('E'):
            team = self.eupen
            pk = int(pk[1:])
        elif pk.startswith('S'):
            team = self.stvith
            pk = int(pk[1:]) + 1000000
            # Cannot import duplicate session 104877
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


    def load_prb(self, row, **kw):
        kw = dict(
            id=row.idprb.strip(),
            name=row.name1.strip(),
            ref=row.ref.strip() or None)
        if Topic.objects.filter(pk=kw['id']).exists():
            return
        if Topic.objects.filter(ref=kw['ref']).exists():
            return
        yield Topic(**kw)
        
    def load_ppr(self, row, **kw):
        idprb = row.idprb.strip()
        if not idprb:
            return
        if not Topic.objects.filter(id=idprb).exists():
            return
        idpar = row.idpar.strip()
        try:
            prj = Course.objects.get(ref=idpar)
        except Course.DoesNotExist:
            dd.logger.warning(
                "Cannot import MSG %s : no course ref %s", row, idpar)
            return
        # idpar = self.par_pk(row.idpar.strip())
        # if idpar is None:
        #     return
        # try:
        #     par = Partner.objects.get(id=idpar)
        # except Partner.DoesNotExist:
        #     return
        yield Interest(owner=prj, topic_id=idprb)
        
    def load_msg(self, row, **kw):
        idpar = row.idpar.strip()
        try:
            prj = Course.objects.get(ref=idpar)
        except Course.DoesNotExist:
            dd.logger.warning(
                "Cannot import MSG %s : no course ref %s", row, idpar)
            return
        mt, new = rt.models.notes.NoteType.objects.get_or_create(
            name=row.type.strip())
            
        # idpar = self.par_pk(row.idpar.strip())
        # if idpar is None:
        #     return
        if row.date is None:
            return
        # try:
        #     prj = Course.objects.get(partner__id=idpar)
        # except Course.DoesNotExist:
        #     prj = None
        # except Course.MultipleObjectsReturned:
        #     prj = None
        yield Note(
            project=prj,
            type=mt,
            user=self.get_user(row.idusr),
            date=row.date,
            time=row.time.strip(),
            subject=row.titre.strip(),
            body=self.dbfmemo(row.texte))
        
        

                
    def objects(self):
        # yield Country(isocode='LU', **dd.str2kw('name', _("Luxemburg")))
        # yield Country(isocode='PL', **dd.str2kw('name', _("Poland")))
        # yield Country(isocode='AU', **dd.str2kw('name', _("Austria")))
        # yield Country(isocode='US', short_code='USA',
        #               **dd.str2kw('name', _("United States")))
        # yield self.load_dbf('USR')
        # yield super(TimLoader, self).objects()
        # yield self.load_dbf('PLP')

        def bulkdel(*models):
            for m in models:
                m.objects.all()._raw_delete(DEFAULT_DB_ALIAS)

        bulkdel(Guest, Event)
        bulkdel(Topic, Interest, Note)
        bulkdel(ClientContact, Enrolment, Course)
        
        yield self.load_dbf('PAR')

        yield self.load_dbf('PRB')
        yield self.load_dbf('PPR')
        yield self.load_dbf('MSG')

        yield self.load_dbf('DLS')
        yield self.load_dbf('DLP')
