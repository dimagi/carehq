#TODO:
from couchdbkit.schema.properties import IntegerProperty, DictProperty, DictProperty
from couchdbkit.schema.properties_proxy import SchemaListProperty, SchemaProperty
from datetime import datetime
import simplejson
from dimagi.utils import make_uuid
from couchdbkit.ext.django.schema import StringProperty, BooleanProperty, DateTimeProperty, Document, DateProperty
from dimagi.utils.make_time import make_time
from django.core.cache import cache

ghetto_regimen_map = {
    "qd": '1',
    "bid": '2',
    "qd-am": '1',
    "qd-pm": '1',
    "tid": '3',
    "qid": '4',
    '': '' ,
}

class CPhone(Document):
    is_default = BooleanProperty()
    description = StringProperty()
    number = StringProperty()
    created = DateTimeProperty(default=datetime.utcnow)
    
    deprecated = BooleanProperty(default=False)
    started = DateTimeProperty(default=datetime.utcnow, required=True)
    ended = DateTimeProperty()
    created_by = StringProperty() #userid
    edited_by = StringProperty() #useridp
    notes = StringProperty()

    class Meta:
        app_label = 'patient'

class CAddress(Document):
    """
    An address.
    """
    description = StringProperty() #the title so to speak
    address_id = StringProperty(default=make_uuid)
    street = StringProperty()
    city = StringProperty()
    state = StringProperty()
    postal_code = StringProperty()
    
    deprecated = BooleanProperty(default=False)

    started = DateTimeProperty(default=make_time, required=True)
    ended = DateTimeProperty()

    created_by = StringProperty() #userid
    edited_by = StringProperty() #userid


    class Meta:
        app_label = 'patient'
        
        
class CDotWeeklySchedule(Document):
    """Weekly schedule where each day has a username"""
    schedule_id = StringProperty(default=make_uuid)
    
    sunday = StringProperty() 
    monday = StringProperty() 
    tuesday = StringProperty() 
    wednesday = StringProperty() 
    thursday = StringProperty() 
    friday = StringProperty() 
    saturday = StringProperty() 
    
    
    comment = StringProperty()
    
    deprecated = BooleanProperty(default=False)
    
    started = DateTimeProperty(default=datetime.utcnow, required=True)
    ended = DateTimeProperty()
    
    created_by = StringProperty() #userid
    edited_by = StringProperty() #userid
    
    class Meta:
        app_label = 'patient'
    

    

#this class ought not to be used for new data
class CDotSchedule(Document):
    day_of_week = StringProperty()
    hp_username = StringProperty()

    class Meta:
        app_label = 'patient'


ghetto_patient_xml = """<case>
                   <case_id>%(case_id)s</case_id>
                   <date_modified>%(date_modified)s</date_modified>
                   <create>
                       <user_id></user_id>
                       <case_type_id>cc_path_client</case_type_id>
                       <case_name>%(patient_name)s</case_name>
                       <external_id>%(patient_id)s</external_id>
                   </create>
                   <update>
                       <pactid>%(pact_id)s</pactid>
                       <gender>%(sex)s</gender>
                       <type>%(arm)s</type>
                       %(phones)s
                       %(addresses)s
                       %(dot_schedule)s
                       %(regimens)s
                       <dob>%(dob)s</dob>
                       <initials>%(pt_initials)s</initials>
                       <hp>%(hp)s</hp>
                       <last_note>%(last_note)s</last_note>
                       <last_dot>%(last_dot)s</last_dot>
                   </update>
           </case>"""

class CBloodworkCD(Document):
    cdcnt = StringProperty()
    cdper = StringProperty()

    class Meta:
        app_label = 'patient'
    def save(self):
        pass

class CBloodwork(Document):

    test_date = StringProperty()
    tests = StringProperty()
    vl = StringProperty()
    cd = SchemaProperty(CBloodworkCD)

    @property
    def get_date(self):
        try:
            return datetime.strptime(self.test_date, "%Y-%m-%d")
        except:
            return None

    @property
    def is_overdue(self):
        if self.get_date != None:
            days = (datetime.utcnow() - self.get_date).days
            if days > 90:
                return True
            else:
                return False
        else:
            return True
    class Meta:
        app_label = 'patient'

    def save(self):
        pass


class CActivityDashboard(Document):
    count = IntegerProperty()
    encounter_date = DateTimeProperty()
    doc_id = StringProperty()
    chw_id = StringProperty()
    last_xmlns = StringProperty()
    last_received = DateTimeProperty()
    last_bloodwork = SchemaProperty(CBloodwork)

    patient_doc = DictProperty()

    @property
    def last_form_type(self):
        if self.last_xmlns == 'http://dev.commcarehq.org/pact/progress_note':
            return "Progress Note"
        elif self.last_xmlns == 'http://dev.commcarehq.org/pact/dots_form':
            return "DOTS"

    def save(self):
        pass

    class Meta:
        app_label = 'patient'

class CPatient(Document):
    GENDER_CHOICES = (
        ('m','Male'),
        ('f','Female'),
        ('u','Undefined'),
    )

    django_uuid = StringProperty() #the django uuid of the patient object
    pact_id = StringProperty(required=True)
    first_name = StringProperty(required=True)
    middle_name = StringProperty()
    last_name = StringProperty(required=True)
    gender = StringProperty(required=True)
    primary_hp = StringProperty(required=True)
    arm = StringProperty()
    birthdate = DateProperty()
    patient_id = StringProperty()
    address = SchemaListProperty(CAddress)
    phones = SchemaListProperty(CPhone)
    #cases = SchemaListProperty(PatientCase)
    art_regimen = StringProperty()
    non_art_regimen = StringProperty()
    date_modified = DateTimeProperty(default=datetime.utcnow)

    prior_bloodwork = SchemaProperty(CBloodwork) #legacy bloodwork data object.  All requests will be done via xform instance querying

    last_note = DateTimeProperty()
    last_dot = DateTimeProperty()

    dots_schedule = SchemaListProperty(CDotSchedule) #deprecated
    weekly_schedule = SchemaListProperty(CDotWeeklySchedule)
    #    providers = SchemaListProperty(CProvider) # providers in PACT are done via the careteam
    notes = StringProperty()

    class Meta:
        app_label = 'patient'


    def _set_schedule_dates(self):
        self.weekly_schedule = sorted(self.weekly_schedule, key=lambda x: x.started)

        for i in range(len(self.weekly_schedule)):
            cur = self.weekly_schedule[i]
            print "%d: %s" % (i, cur.schedule_id)
            print "\tStarted: %s" % (cur.started)
            print "\tEnded: %s" % (cur.ended)
            if i == len(self.weekly_schedule) - 1:
                #if we're at the end, ensure that this is set to go on forever
                cur.ended=None
                break
            #do a check and set to make sure
            next = self.weekly_schedule[i+1]

            cur.ended = next.started
            cur.save()
        #this introduces a circular dependency up top
        from pactcarehq import schedule
        schedule.cached_schedules = {} #reinitialize the cache EVERY time the schedule is changed, not efficient, a major TODO



    def save(self):
        #reorder the schedules to sort by start date
        self._set_schedule_dates()
        super(CPatient, self).save()
        #next, we need to invalidate the cache
        cache.delete('%s_couchdoc' % (self.django_uuid))
        try:
            couchjson = simplejson.dumps(self.to_json())
            cache.set('%s_couchdoc' % (self.django_uuid), couchjson)
            #print "invalidated and updated cache for patient"
        except Exception, ex:
            #print "unable to invalidate cache: %s" % (ex)
            pass

    @property
    def last_bloodwork(self):
        """bloodwork will check two places.  First, the custom bloodwork view to see if there's a bloodwork submission from an XForm, else, it'll check to see """
        #print "getting last bloodwork"
        if hasattr(self, '_prior_bloodwork'):
            #in memory lookup
            return self._prior_bloodwork

        #memcached lookup
        last_bw = cache.get('%s_bloodwork' % (self._id), None)
        if last_bw == None:
            #it's null, so it's a cache miss.
            #do a requery
            pass
        elif last_bw == '[##Null##]':
            return None
        else:
            self._prior_bloodwork = CBloodwork.wrap(simplejson.loads(last_bw))
            return self._prior_bloodwork


        #requery
        bw_docs = CBloodwork.view('pactcarehq/patient_bloodwork', key=self.pact_id).all()
        bw_docs = sorted(bw_docs, key=lambda x: x['test_date'])
        if len(bw_docs) > 0:
            self._prior_bloodwork = bw_docs[0]
            cache.set('%s_bloodwork' % (self._id), simplejson.dumps(bw_docs[0].to_json()))
            return bw_docs[0]
        if self.prior_bloodwork.test_date == None:
            #this is a bit hacky, it should really be null, but since this is an added on object, to CPatient, it doesn't show up as None
            #so we need to do an explicit check for the
            cache.set('%s_bloodwork' % (self._id), '[##Null##]')
            pass
        else:
            self._prior_bloodwork = self.prior_bloodwork
            return self.prior_bloodwork
        return None


    @property
    def activity_dashboard(self):
        #[count, encounter_date, doc_id, chw_id, xmlns, received_on]
        #print "\tActivity dashboard %s" % (self._id)

        if hasattr(self, '_dashboard'):
            #print "\t\tIn memory"
            return self._dashboard
        else:
            #Let's check memcached.
            cached_dashboard_json = cache.get('%s_dashboard' % (self._id), None)
            if cached_dashboard_json != None:
                #print "\t\tmemcached hit!"
                if cached_dashboard_json == '[##Null##]':
                    self._dashboard = None #nullstring, so we have no dashboard but we don't want to requery
                else:
                    self._dashboard = CActivityDashboard.wrap(simplejson.loads(cached_dashboard_json))
            else:
                #print "\t\tRequery"
                dashboard_data = CActivityDashboard.view('pactcarehq/patient_dashboard', key=self.pact_id).first()
                if dashboard_data == None:
                    #if it's null, set it to null in memcached using a nullstring
                    cache.set("%s_dashboard" % (self._id), '[##Null##]')
                    self._dashboard = None
                else:
                    cache.set('%s_dashboard' % (self._id), simplejson.dumps(dashboard_data['value']))
                    self._dashboard = CActivityDashboard.wrap(dashboard_data['value'])

            if self._dashboard != None and self._dashboard.last_bloodwork.test_date != None:
                #print "\t\t\tSetting prior bloodwork"
                self._prior_bloodwork = self._dashboard.last_bloodwork

            return self._dashboard



    @property
    def current_schedule(self):
        #return sorted(self.weekly_schedule, key=lambda x:x.started)[-1]
        if len(self.weekly_schedule) > 0:
            rsched = range(0, len(self.weekly_schedule))
            rsched.reverse()

            for i in rsched:
                sched = self.weekly_schedule[i]
                if sched.deprecated == True:
                    continue
                if sched.started > datetime.utcnow():
                    #greedily check to see if the schedule will return
                    continue
                else:
                    return sched
            #return self.weekly_schedule[-1]
        else:
            return None

    @property
    def past_schedules(self):
        ret = []
        if len(self.weekly_schedule) > 0:
            scheds = range(0, len(self.weekly_schedule))
            for i in scheds:
                sched = self.weekly_schedule[i]
                if sched.started > datetime.utcnow():
                    continue
                elif sched.ended == None or sched.ended > datetime.now():
                    continue
                else:
                    ret.append(sched)
        else:
            return []
        return ret


    @property
    def future_schedules(self):
        ret = []
        if len(self.weekly_schedule) > 0:
            rsched = range(0, len(self.weekly_schedule))
            rsched.reverse()

            for i in rsched:
                sched = self.weekly_schedule[i]
                if sched.deprecated == True:
                    continue
                if sched.started > datetime.utcnow():
                    ret.insert(0,sched)
        else:
            return []
        return ret
        
    @property
    def latest_address(self):
        #return sorted(self.weekly_schedule, key=lambda x:x.started)[-1]
        if len(self.address) > 0:
            return self.address[-1]
        else:
            return None

    def set_schedule(self, new_schedule):
        """set the schedule as head of the schedule by accepting a cdotweeklychedule"""
        #first, set all the others to inactive

        new_schedule.deprecated=False
        if new_schedule.started == None or new_schedule.started <= datetime.utcnow():
            new_schedule.started=datetime.utcnow()
            for sched in self.weekly_schedule:
                if not sched.deprecated:
                    #sched.deprecated=True
                    sched.ended=datetime.utcnow()
                    sched.save()
        elif new_schedule.started > datetime.utcnow():
            #if it's in the future, then don't deprecate the future schedule, just procede along and let the system set the dates correctly
            pass
        self.weekly_schedule.append(new_schedule)
        self.save()

    def set_address(self, new_address):
        """set the schedule as head of the schedule by accepting a cdotweeklychedule"""
        #first, set all the others to inactive
        for addr in self.address:
            if not addr.deprecated:
                addr.deprecated=True
                addr.ended=datetime.utcnow()
                addr.save()
        new_address.deprecated=False
        self.address.append(new_address)
        self.save()

    @property
    def active_phones(self):
        ret = []
        for phone in self.phones:
            if phone.deprecated:
                continue
            else:
                ret.append(phone)
        return ret
    @property
    def active_addresses(self):
        ret = []
        for addr in self.address:
            if addr.deprecated:
                continue
            else:
                ret.append(addr)
        return ret

    def get_ghetto_phone_xml(self):
        ret = ''
        counter = 1
        for phone in self.active_phones:
            if phone.number == '':
                continue
            else:
                ret += "<Phone%d>%s</Phone%d>" % (counter, phone.number.replace("(", "").replace(")", ""),counter)
                counter += 1
        return ret

    def get_ghetto_regimen_xml(self):
        ret = ''
        ret += "<artregimen>%s</artregimen>" % (ghetto_regimen_map[self.art_regimen.lower()])
        ret += "<nonartregimen>%s</nonartregimen>" % (ghetto_regimen_map[self.non_art_regimen.lower()])
        return ret

    def get_ghetto_address_xml(self):
        ret = ''
        counter = 1
        for addr in self.active_addresses:
            addconcat = "%s %s, %s 0%s" % (addr.street, addr.city, addr.state, addr.postal_code)
            ret += "<address%d>%s</address%d>" % (counter,addconcat, counter)
            counter += 1
        return ret

    def get_ghetto_schedule_xml(self):
        ret = ''
        counter = 1
        days_of_week = ['sunday','monday','tuesday','wednesday','thursday','friday','saturday']
        if self.current_schedule != None:
            #current_schedule is the NEW format for scheduling.  If it is not null, use it and use it only.
            #else, 
            for day in days_of_week:
                if getattr(self.current_schedule, day) != None:
                    hp_username = getattr(self.current_schedule,day)
                else:
                    hp_username=self.primary_hp
                ret += "<dotSchedule%s>%s</dotSchedule%s>" % (day,hp_username, day)
        else:
            for sched in self.dots_schedule:
                day_of_week = sched.day_of_week
                hp_username = sched.hp_username
                if hp_username == '':
                    hp_username = self.primary_hp
                ret += "<dotSchedule%s>%s</dotSchedule%s>" % (day_of_week,hp_username, day_of_week)
                counter += 1
        return ret

    def ghetto_xml(self):
        xml_dict = {}
        xml_dict['case_id'] = self._id
        xml_dict['date_modified'] = self.date_modified.strftime("%Y-%m-%dT%H:%M:%S.000")
        xml_dict['patient_name'] = "%s, %s" % (self.last_name, self.first_name)
        xml_dict['patient_id'] = self.django_uuid
        xml_dict['pact_id'] = self.pact_id
        xml_dict['sex'] = self.gender
        xml_dict['arm'] = self.arm
        xml_dict['dob'] = self.birthdate.strftime("%Y-%m-%d")
        xml_dict['pt_initials'] = "%s%s" % (self.first_name[0], self.last_name[0])
        xml_dict['hp'] = self.primary_hp
        xml_dict['phones'] = self.get_ghetto_phone_xml()
        xml_dict['addresses'] = self.get_ghetto_address_xml()

        #todo: this ought to also use a view to verify that the dots and progress notes are dynamically queried for last status.  This patient placeholder is for testing and legacy purposes
        if self.last_dot != None:
            xml_dict['last_dot'] = self.last_dot
        else:
            xml_dict['last_dot'] = ''

        if self.last_note != None:
            xml_dict['last_note'] = self.last_note
        else:
            xml_dict['last_note'] = ''

        if self.arm.lower() == 'dot':
            xml_dict['dot_schedule'] = self.get_ghetto_schedule_xml()
            xml_dict['regimens'] = self.get_ghetto_regimen_xml()
        else:
            xml_dict['dot_schedule'] = ''
            xml_dict['regimens'] = ''
        ret = ghetto_patient_xml % (xml_dict)
        return ret



class CSimpleComment(Document):
    doc_fk_id = StringProperty() #is there a fk in couchdbkit
    deprecated = BooleanProperty(default=False)
    comment = StringProperty()
    created_by = StringProperty()
    created = DateTimeProperty(default=datetime.utcnow)
    class Meta:
        app_label = 'patient'