from _collections import defaultdict
from datetime import datetime, timedelta, date
import pdb
from couchdbkit.ext.django.schema import Document
from couchdbkit.schema.properties import StringProperty, DateTimeProperty, BooleanProperty, IntegerProperty, DictProperty, DateProperty
from couchdbkit.schema.properties_proxy import SchemaProperty, SchemaListProperty
from django.core.cache import cache
import simplejson
from django.core.urlresolvers import reverse
from pytz import timezone
from casexml.apps.case.models import CommCareCase
from couchforms.models import XFormInstance
from pactpatient.enums import  PACT_RACE_CHOICES, PACT_LANGUAGE_CHOICES, PACT_HIV_CLINIC_CHOICES
from patient.models import BasePatient
import logging
from dimagi.utils import make_uuid
import settings

PACT_CACHE_TIMEOUT=14400

ghetto_regimen_map = {
    "none":'0',
    "qd": '1',
    "bid": '2',
    "qd-am": '1',
    "qd-pm": '1',
    "tid": '3',
    "qid": '4',
    '': '' ,

    'morning': 1,
    'noon': 1,
    'evening': 1,
    'bedtime': 1,

    'morning,noon': 2,
    'morning,evening': 2,
    'morning,bedtime': 2,
    'noon,evening': 2,
    'noon,bedtime': 2,
    'evening,bedtime': 2,

    'morning,noon,evening':3,
    'morning,noon,bedtime':3,
    'morning,evening,bedtime':3,
    'noon,evening,bedtime':3,

    'morning,noon,evening,bedtime':4,

}

html_escape_table = {
    "&": "&amp;",
    '"': "&quot;",
    "'": "&apos;",
    ">": "&gt;",
    "<": "&lt;",
    }

def html_escape(text):
    """Produce entities within text."""
    return "".join(html_escape_table.get(c,c) for c in text)

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
        app_label='pactpatient'




#this class ought not to be used for new data
class CDotSchedule(Document):
    day_of_week = StringProperty()
    hp_username = StringProperty()

    class Meta:
        app_label='pactpatient'


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
                       <patient_notes>%(patient_note)s</patient_notes>
                       %(phones)s
                       %(addresses)s
                       %(dot_schedule)s
                       %(regimens)s
                       <dob>%(dob)s</dob>
                       <initials>%(pt_initials)s</initials>
                       <hp>%(hp)s</hp>
                       <last_note>%(last_note)s</last_note>
                       <last_dot>%(last_dot)s</last_dot>
                       %(last_bw_xml)s
                   </update>
           </case>"""

class CBloodworkCD(Document):
    cdcnt = StringProperty()
    cdper = StringProperty()

    class Meta:
        app_label='pactpatient'
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
        app_label='pactpatient'

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
        app_label='pactpatient'


class PactPatient(BasePatient):
    pact_id = StringProperty(required=True)
    primary_hp = StringProperty(required=True)
    arm = StringProperty()
    art_regimen = StringProperty()
    non_art_regimen = StringProperty()
    prior_bloodwork = SchemaProperty(CBloodwork) #legacy bloodwork data object.  All requests will be done via xform instance querying
    last_note = StringProperty() #will be a timestamp
    last_dot = StringProperty() #will be a timestamp
    dots_schedule = SchemaListProperty(CDotSchedule) #deprecated
    weekly_schedule = SchemaListProperty(CDotWeeklySchedule)

    race = StringProperty()
    is_latino = BooleanProperty()
    preferred_language = StringProperty()
    mass_health_expiration = DateProperty()
    hiv_care_clinic = StringProperty()
    ssn = StringProperty()

    @property
    def last_progress_note_date(self):
        #iterate through xforms in case and get namespace by doing xforminstance.get()
        case_doc = self._cache_case()

        if case_doc.has_key('last_note'):
            return case_doc['last_note']
        else:
            return '1969-12-31'

    #@property
    def last_dot_form_date(self):
        #todo: get case
        #iterate through xforms in case and get namespace by doing xforminstance.get()
        #if dots form, then break
        case_doc = self._cache_case()
        if case_doc.has_key('last_dot'):
            return case_doc['last_dot']
        else:
#            for id in reversed(case_doc.xform_ids):
#                xform = self._get_case_submission(id)
#                if xform.xmlns == 'http://dev.commcarehq.org/pact/dots_form':
#                    return xform['form']['encounter_date']
            return '1969-12-13'


    def _cache_case(self, invalidate=False):
        if invalidate:
            cache.delete('%s_casedoc' % self._id)
            delattr(self, '_case')

        if hasattr(self,'_case'):
            return self._case

        mem_case_string = cache.get('%s_casedoc' % (self._id), None)
        if mem_case_string is None:
            #it's null, so it's a cache miss.
            #do a requery
            self._case = CommCareCase.get_db().get(self.case_id)
            cache.set('%s_casedoc' % self._id, simplejson.dumps(self._case), PACT_CACHE_TIMEOUT)
            self._cached_submits=True
        else:
            #it's a cache hit, retrieve and return the document
            mem_case_json = simplejson.loads(mem_case_string)
            #self._case = CommCareCase.wrap(mem_case_json)
            self._case = mem_case_json
        self._cached_submits=True
        return self._case



#    def _get_case_submissions(self):
#        print "cache case submits for %s" % self._id
#        case = self._cache_case()
#        attrib = '_case_submissions_%s' % case._id
#        if hasattr(self, attrib):
#            print "hit cache case submits for %s" % self._id
#            return getattr(self, attrib)
#        else:
#            submissions = [XFormInstance.get(x) for x in case.xform_ids]
#            setattr(self, attrib, submissions)
#            print "finish cache case submits for %s" % self._id
#            return submissions

    def _get_case_submission(self, xform_id):
        if not hasattr(self, '_case'):
            self._cache_case()
        attrib = '_case_xform_%s' % xform_id
        if hasattr(self, attrib):
            return getattr(self, attrib)
        else:
            if xform_id in self._case['xform_ids']:
                instance = XFormInstance.get(xform_id)
                setattr(self, attrib, instance)
                return instance
            else:
                return None





    def get_absolute_url(self):
        return reverse('view_pactpatient', kwargs={'patient_guid': self._id, 'view_mode': ''})

    @property
    def get_race(self):
        if hasattr(self, '_race'):
            return self._race
        else:
            self._race = None
            for x in PACT_RACE_CHOICES:
                if x[0] == self.race:
                    self._race = x[1]
                    break
            return self._race

    @property
    def get_hiv_care_clinic(self):
        if hasattr(self, '_hiv_care_clinic'):
            return self._hiv_care_clinic
        else:
            self._hiv_care_clinic = None
            for x in PACT_HIV_CLINIC_CHOICES:
                if x[0] == self.hiv_care_clinic:
                    self._hiv_care_clinic = x[1]
                    break
            return self._hiv_care_clinic
    @property
    def get_preferred_language(self):
        if hasattr(self, '_preferred_language'):
            return self._preferred_language
        else:
            self._preferred_language = None
            for x in PACT_LANGUAGE_CHOICES:
                if x[0] == self.preferred_language:
                    self._preferred_language = x[1]
                    break
            return self._preferred_language

    @property
    def art_num(self):
        try:
            num = int(ghetto_regimen_map[self.art_regimen.lower()])
        except:
            num = 0
            logging.error("Patient does not have a set art regimen")
        return num

    @property
    def non_art_num(self):
        try:
            num = int(ghetto_regimen_map[self.non_art_regimen.lower()])
        except:
            num = 0
            logging.error("Patient does not have a set non art regimen")
        return num


    class Meta:
        app_label='pactpatient'


    def _set_schedule_dates(self):
        self.weekly_schedule = sorted(self.weekly_schedule, key=lambda x: x.started)

        for i in range(len(self.weekly_schedule)):
            cur = self.weekly_schedule[i]
            if i == len(self.weekly_schedule) - 1:
                #if we're at the end, ensure that this is set to go on forever
                cur.ended=None
                break
            #do a check and set to make sure
            next = self.weekly_schedule[i+1]

            cur.ended = next.started
        #this introduces a circular dependency up top
        from pactcarehq import schedule
        schedule.cached_schedules = {} #reinitialize the cache EVERY time the schedule is changed, not efficient, a major TODO


    def save(self, *args, **kwargs):
        self._set_schedule_dates()
        self.date_modified = datetime.utcnow()
        super(PactPatient, self).save(*args, **kwargs)

    @classmethod
    def check_pact_id(cls, pact_id):
        if cls.view('pactcarehq/patient_pact_ids', key=pact_id, include_docs=True).count() > 0:
            return False
        else:
            return True


    def is_unique(self):
        if self.__class__.view('pactcarehq/patient_pact_ids', key=self.pact_id, include_docs=True).count() > 0:
            return False
        else:
            return True

    @property
    def check_last_bloodwork(self):
        """bloodwork will check two places.  First, the custom bloodwork view to see if there's a bloodwork submission from an XForm, else, it'll check to see """
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
            pass

        #requery
        bw_docs = CBloodwork.view('pactcarehq/patient_bloodwork', key=self.pact_id).all()
        bw_docs = sorted(bw_docs, key=lambda x: x['test_date'], reverse=True)
        if len(bw_docs) > 0:
            self._prior_bloodwork = bw_docs[0]
            cache.set('%s_bloodwork' % (self._id), simplejson.dumps(bw_docs[0].to_json()), PACT_CACHE_TIMEOUT)
            return bw_docs[0]

        if self.prior_bloodwork.test_date is None:
            #this is a bit hacky, it should really be null, but since this is an added on object, to PactPatient, it doesn't show up as None
            #so we need to do an explicit check for the value
            #cache.set('%s_bloodwork' % (self._id), '[##Null##]')
            pass
        else:
            #self._prior_bloodwork = self.prior_bloodwork
            return self.prior_bloodwork
        return None


    @property
    def activity_dashboard(self):
        #[count, encounter_date, doc_id, chw_id, xmlns, received_on]
        if hasattr(self, '_dashboard'):
            return self._dashboard
        else:
            #Let's check memcached.
            cached_dashboard_json = cache.get('%s_dashboard' % self._id, None)
            if cached_dashboard_json is not None:
                if cached_dashboard_json == '[##Null##]':
                    self._dashboard = None #nullstring, so we have no dashboard but we don't want to requery
                else:
                    self._dashboard = CActivityDashboard.wrap(simplejson.loads(cached_dashboard_json))
            else:
                #new version pulling from case
                case_doc = self._cache_case()
                db = XFormInstance.get_db()

                last_submit = None
                for xform_id in case_doc['xform_ids']:
                    if db.doc_exist(xform_id):
                        last_submit = xform_id
                        break
                    else:
                        last_submit = None
                        continue
                if last_submit is None:
                    return CActivityDashboard()

                ret = dict()
                ret['count'] = len(set(case_doc['xform_ids']))
                last_form = self._get_case_submission(last_submit)#self._XFormInstance.get(case_doc.xform_ids[-1])
                ret['doc_id'] = last_form._id
                ret['last_xmlns'] = last_form.xmlns
                ret['last_received'] = last_form.received_on.strftime("%Y-%m-%dT%H:%M:%SZ")

                def _get_encounter_date(xform_doc):
                    ret_date = None
                    try:
                        if xform_doc['form'].get('encounter_date', None) is not None:
                            ret_date = xform_doc['form']['encounter_date']
                        if xform_doc['form'].get('note', None) is not None and xform_doc['form']['note'].get('encounter_date', None) is not None:
                            ret_date =  xform_doc['form']['note']['encounter_date']
                        if xform_doc['form'].get('Meta', None) is not None:
                            if xform_doc['form']['Meta'].get('TimeEnd', None) is not None:
                                ret_date = xform_doc['form']['Meta']['TimeEnd']
                            if xform_doc['form']['Meta'].get('TimeStart', None) is not None:
                                ret_date = xform_doc['form']['Meta']['TimeStart']


                        #last check
                        if ret_date is None:
                            ret_date = xform_doc['received_on']

                        if isinstance(ret_date, date):
                            ret_date = ret_date.strftime('%Y-%m-%dT04:00:00.000Z')
                        elif isinstance(ret_date, datetime):
                            ret_date = ret_date.strftime('%Y-%m-%dT%H:%M:%SZ')
                        elif isinstance(ret_date, str) or isinstance(ret_date, unicode):
                            splits = ret_date.split(' ')
                            if len(splits) > 1:
                                ret_date = "%sT%s" % (splits[0], splits[1])
                            else:
                                ret_date = None

                    except Exception, ex:
                        ret_date = None
                        logging.error("Unable to parse an encounter date from submission %s" % xform_doc['_id'])

                    return ret_date


                ret['encounter_date'] = _get_encounter_date(last_form)
                cache.set('%s_dashboard' % self._id, simplejson.dumps(ret))
                self._dashboard = CActivityDashboard.wrap(ret)

#            if self._dashboard is not None and self._dashboard['last_bloodwork'].test_date:
#                self._prior_bloodwork = self._dashboard.last_bloodwork
            return self._dashboard

    def dots_casedata_for_day(self, date, art_num, non_art_num):
        from dotsview.views import _get_observations_for_date #(date, pact_id, art_num, nonart_num):
        from dotsview.models import  TIME_LABELS, MAX_LEN_DAY, ADDENDUM_NOTE_STRING

        def get_day_elements(drug_data, num_timekeys, total_num):
            """helper function to return an array of the observations for a given drug_type, for the regimen frequency
            [[adherence,method], [adherence,method]...]
            """
            day_arr = []

            for timekey in TIME_LABELS: #this is just getting ALL the timelabels to see if the line up
                #get the top one from the array
                if not drug_data.has_key(timekey):
                    continue
#                if len(day_arr) >= total_num:
                    #logging.error("Day array for getting long, skipping superfluous data for patient %s" % (self.pact_id))
                if len(drug_data[timekey]) > 0 and len(day_arr) < MAX_LEN_DAY:
                    obs = drug_data[timekey][0]
                    if obs.day_note != None and len(obs.day_note) > 0 and obs.day_note != ADDENDUM_NOTE_STRING:
                        day_arr.append([obs.adherence, obs.method, obs['day_note']])
                    else:
                        day_arr.append([obs.adherence, obs.method])


                #else:
                 #   day_arr.append(["unchecked", "pillbox"])
            if len(day_arr) < total_num:
                delta = total_num - len(day_arr)
                for n in range(delta):
                    day_arr.append(["unchecked", "pillbox"])
            return day_arr

        def get_empty(n):
            return [["unchecked", "pillbox"] for x in range(n)]


        #[(ak, [(tk, sorted(grouping[ak][tk], key=lambda x: x.anchor_date)[-1:]) for tk in timekeys]) for ak in artkeys],
        day_dict, is_reconciled = _get_observations_for_date(date, self.pact_id, art_num, non_art_num, reconcile_trump=True)
        day_arr = []
        if day_dict.has_key('Non ART'):
            nonart_data = get_day_elements(day_dict['Non ART'], len(day_dict['Non ART'].keys()), non_art_num)
        else:
            nonart_data = get_empty(non_art_num)
        if day_dict.has_key('ART'):
            art_data = get_day_elements(day_dict['ART'], len(day_dict['ART'].keys()), art_num)
        else:
            nonart_data = get_empty(art_num)
        day_arr.append(nonart_data)
        day_arr.append(art_data)
        return day_arr

    def get_dots_data(self):
        startdate = datetime.utcnow()
        ret = {}
        try:
            art_num = int(ghetto_regimen_map[self.art_regimen.lower()])
        except:
            art_num = 0
            logging.error("Patient does not have a set art regimen")


        try:
            non_art_num = int(ghetto_regimen_map[self.non_art_regimen.lower()])
        except:
            non_art_num = 0
            logging.error("Patient does not have a set non art regimen")


        ret['regimens'] = [
                            non_art_num, #non art is 0
                            art_num,    #art is 1
                            ]

        ret['days'] = []
        #dmyung - hack to have it be timezone be relative specific to the eastern seaboard
        #ret['anchor'] = isodate.strftime(datetime.now(tz=timezone(settings.TIME_ZONE)), "%d %b %Y")
        ret['anchor'] = datetime.now(tz=timezone(settings.TIME_ZONE)).strftime("%d %b %Y")


        for delta in range(21):
            date = startdate - timedelta(days=delta)
            day_arr = self.dots_casedata_for_day(date, art_num, non_art_num)
            ret['days'].append(day_arr)
        ret['days'].reverse()
        return ret






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

    def get_address(self, address_id):
        filtered = filter(lambda x: x.address_id==address_id, self.address)
        if len(filtered) == 0:
            return None
        else:
            return filtered[0]

    def address_index(self, address_id):
        for i, addr in enumerate(self.address):
            if addr.address_id == address_id:
                return i
        return -1

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

    def remove_address(self, address_id):
        #remove a given address in the address array by the givenguid
        self.address = filter(lambda x: x.address_id!=address_id, self.address)
        self.save()

    def set_address(self, new_address, ):
        """set the schedule as head of the schedule by accepting a cdotweeklychedule"""
        self.address.append(new_address)
        self.save()

    def casexml_phones(self):
        """
        Get casexml phones
        """
        casedoc = self._cache_case()
        phone_properties = sorted(filter(lambda x: x.startswith("Phone"), casedoc.keys()))
        #iterate through all phones properties and make an array of [ {description, number}, etc ]
        ret = []

        for n, x in enumerate(phone_properties, start=1):
            p = {}
            p['phone_id'] = n
            if casedoc.has_key('Phone%d' % n):
                pnum = casedoc['Phone%d' % n]
                if pnum is not None and pnum != '':
                    p['number'] = pnum
            if casedoc.has_key('Phone%dType' % n):
                p['description'] = casedoc['Phone%dType' % n]
            else:
                p['description'] = 'Other'
            if p.has_key('number'):
                ret.append(p)
            if p == {}:
                break
        return ret


    @property
    def casexml_addresses(self):
        """
        Get casexml address info
        """
        casedoc = self._cache_case()
        #iterate through all address properties and make an array of [ {description, address_string}, etc ]
        address_props = sorted(filter(lambda x: x.startswith("address"), casedoc.keys()))
        ret = []

        for n, x in enumerate(address_props):
            p = {}
            p['address_id'] = n
            if casedoc.has_key('address%d' % n):
                pnum = casedoc['address%d' % n]
                if pnum != None and pnum != '':
                    p['address'] = pnum
            if casedoc.has_key('address%dtype' % n):
                p['description'] = casedoc['address%dtype' % n]

            if p.has_key('address'):
                ret.append(p)
            if p == {}:
                break
        return ret

    def get_ghetto_phone_xml(self):
        ret = ''
        counter = 1
        aphones = self.casexml_phones()
        for num, phone in enumerate(aphones, start=1):
            if phone['number'] == '':
                continue
            else:
                ret += "<Phone%d>%s</Phone%d>" % (num, phone['number'].replace("(", "").replace(")", ""),num)
                if phone['description'] != None and len(phone['description']) > 0:
                    ret += "<Phone%dType>%s</Phone%dType>" % (num, phone['description'], num)
                else:
                    ret += "<Phone%dType>Default</Phone%dType>" % (num, num)
        return ret

    def get_ghetto_regimen_xml(self, invalidate=False):
        """
        Returns DOT regimens as well as DOT adherence information
        """

        if invalidate:
            cache.delete('%s_dot_xml' % self._id)

        xml_ret = cache.get('%s_dot_xml' % self._id, None)
        if xml_ret is None:
            art_regimen = ghetto_regimen_map[self.art_regimen.lower()]
            if art_regimen == '0':
                art_regimen = ''

            nonart_regimen = ghetto_regimen_map[self.non_art_regimen.lower()]
            if nonart_regimen == '0':
                nonart_regimen = ''

            dots_data = self.get_dots_data()
            ret = ''
            ret += "<artregimen>%s</artregimen>" % art_regimen
            ret += "<nonartregimen>%s</nonartregimen>" % nonart_regimen
            ret += "<dots>%s</dots>" % simplejson.dumps(dots_data)
            cache.set('%s_dot_xml' % self._id, ret, PACT_CACHE_TIMEOUT)
            return ret
        else:
            return xml_ret




    def get_ghetto_address_xml(self):
        ret = ''
        counter = 1
        addresses = self.casexml_addresses
        for addr_dict in addresses:
            #addconcat = "%s %s, %s 0%s" % (addr.street, addr.city, addr.state, addr.postal_code)
            ret += "<address%d>%s</address%d>" % (addr_dict['address_id'],addr_dict['address'], addr_dict['address_id'])
            desc = addr_dict.get('description', 'No Label')
            ret += "<address%dtype>%s</address%dtype>" % (addr_dict['address_id'],desc, addr_dict['address_id'])
        return ret

    def get_ghetto_schedule_xml(self, invalidate=False):

        if invalidate:
            cache.delete('%s_schedule_xml' % self._id)

        xml_ret = cache.get('%s_schedule_xml' % self._id, None)
        if xml_ret is not None:
            return xml_ret

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
        cache.set('%s_schedule_xml' % self._id, ret, PACT_CACHE_TIMEOUT)
        return ret

    def ghetto_xml(self):
        casedoc = self._cache_case()
        xml_dict = defaultdict(lambda: '')
        xml_dict['case_id'] = self.case_id
        xml_dict['date_modified'] = self.date_modified.strftime("%Y-%m-%dT%H:%M:%S.000")
        xml_dict['patient_name'] = "%s, %s" % (self.last_name, self.first_name)
        xml_dict['patient_id'] = self.django_uuid
        xml_dict['pact_id'] = self.pact_id
        xml_dict['sex'] = self.gender
        xml_dict['arm'] = self.arm
        xml_dict['patient_note'] = html_escape(self.notes) if self.notes != None else ""
        xml_dict['dob'] = self.birthdate.strftime("%Y-%m-%d")
        xml_dict['pt_initials'] = "%s%s" % (self.first_name[0], self.last_name[0])
        xml_dict['hp'] = self.primary_hp
        xml_dict['phones'] = self.get_ghetto_phone_xml()
        xml_dict['addresses'] = self.get_ghetto_address_xml()

        #todo: this ought to also use a view to verify that the dots and progress notes are dynamically queried for last status.  This patient placeholder is for testing and legacy purposes

        #check the view if any exist.  if it's empty, check this property.

        xml_dict['last_dot'] = self.last_dot_form_date()
        xml_dict['last_note'] = self.last_progress_note_date

        #todo: check bloodwork view
        xml_dict['last_bw_xml'] = self.get_bloodwork_xml()

        if self.arm.lower().startswith('dot'):
            xml_dict['dot_schedule'] = self.get_ghetto_schedule_xml()
            xml_dict['regimens'] = self.get_ghetto_regimen_xml()
        else:
            xml_dict['dot_schedule'] = ''
            xml_dict['regimens'] = ''
        ret = ghetto_patient_xml % (xml_dict)
        return ret


    def single_bw_item(self, bw):

        #replicating the xml of submissions isn't in scope for parsing back on the phones.  will defer to simpler string output
#        ret = ""
#        ret += "\n<bw>"
#        ret += "<test_date>%s</test_date>" % (bw['test_date'])
#        ret += "<tests>%s</tests>" % (bw['tests'])
#
#        if bw.has_key('vl'):
#            ret += "<vl>%s</vl>" % (bw['vl'])
#        if bw.has_key('cd'):
#            ret +="<cd><cdcnt>%s</cdcnt><cdper>%s</cdper></cd>" % (bw['cd']['cdcnt'], bw['cd']['cdper'])
#        ret += "</bw>"

        ret = "%s|" % (bw['test_date'])
        if bw.has_key('cd'):
            ret += "cd %s" % bw['cd']['cdcnt']
            if bw['cd']['cdper'] != "":
                ret += " %s%%" % bw['cd']['cdper']
            ret += ","
        if bw.has_key('vl'):
            ret += "vl %s" % (bw['vl'])
        ret += "\n"
        return ret



    def get_bloodwork_xml(self):
        """Gets an xml block from the reduction view, patient_bloodwork
        return xml
        <last_bw_data>
        date|cd [count] [pct]%, vl [num]\n*
        </last_bw_data>
        <last_bw>
        datestring
        </last_bw>
        """
        bloodwork = XFormInstance.get_db().view('pactcarehq/patient_bloodwork', key=self.pact_id).all()
        if len(bloodwork) == 0:
            return ''
        bloodwork = sorted(bloodwork, key=lambda x: x['value']['test_date'])

        slice = []
        ret = ''

        if len(bloodwork) < 3:
            slice = bloodwork
            pass
        else:
            slice = bloodwork[-3:]

        ret += "<last_bw_data>"
        for bw in slice:
            ret += self.single_bw_item(bw['value'])
        ret += "</last_bw_data>"

        if len(bloodwork) > 0:
            ret += "\n<last_bw>" + slice[-1]['value']['test_date'] + "</last_bw>"

        return ret


