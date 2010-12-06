#TODO:
from couchdbkit.schema.properties_proxy import SchemaListProperty
from datetime import datetime
from dimagi.utils import make_uuid
from couchdbkit.ext.django.schema import StringProperty, BooleanProperty, DateTimeProperty, Document, DateProperty
from dimagi.utils.make_time import make_time

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
                   </update>
           </case>"""

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

    dots_schedule = SchemaListProperty(CDotSchedule) #deprecated
    weekly_schedule = SchemaListProperty(CDotWeeklySchedule)
    #    providers = SchemaListProperty(CProvider) # providers in PACT are done via the careteam
    notes = StringProperty()

    class Meta:
        app_label = 'patient'

    @property
    def latest_schedule(self):
        #return sorted(self.weekly_schedule, key=lambda x:x.started)[-1]
        if len(self.weekly_schedule) > 0:
            return self.weekly_schedule[-1]
        else:
            return None
        
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
        for sched in self.weekly_schedule:
            if not sched.deprecated:
                sched.deprecated=True
                sched.ended=datetime.utcnow()
                sched.save()
        new_schedule.deprecated=False
        new_schedule.started=datetime.utcnow()
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
        if self.latest_schedule != None:
            for day in days_of_week:
                if getattr(self.latest_schedule, day) != None:
                    hp_username = getattr(self.latest_schedule,day)
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