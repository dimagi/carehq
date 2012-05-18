from datetime import datetime
import pdb
import random
import simplejson
from couchdbkit.ext.django.schema import  SchemaListProperty, Document, DateTimeProperty, IntegerProperty, DateProperty, BooleanProperty, DictProperty, ListProperty
from django.core.files.base import ContentFile
import isodate
from casexml.apps.case.models import CommCareCase
from couchforms.models import XFormInstance
from hutch.couchdb_doc_storage import CouchDBAttachmentFile, CouchDBDocStorage
from hutch.models import AuxMedia, AttachmentImage
from patient.models import BasePatient
from couchdbkit.schema.properties import StringProperty, StringListProperty
import settings
from shineforms.lab_utils import merge_labs
from shineforms.constants import xmlns_display_map, form_sequence, xmlns_sequence, STR_MEPI_ENROLLMENT_FORM, STR_MEPI_LABDATA_FORM, STR_MEPI_LAB_TWO_FORM, STR_MEPI_LAB_FOUR_FORM, STR_MEPI_LAB_THREE_FORM, STR_MEPI_LAB_ONE_FORM
from django.core.cache import cache


couchdb_image_storage = CouchDBDocStorage(db_url=settings.COUCH_DATABASE)

class Foo(Document):
    pass


class ShinePatientReportCache(Document):
    """
    Due to the way in which the casexml is structured, and our need for reporting on status, it's becoming necessary
    to make a separate cache document to efficiently store/retrieve things.  Even memcached queries are too slow because
    i still try to do some walking of the data to see if it's stale or not, or i get too much data to serialize/deserialize.

    Time to be more compact
    """
    case_id = StringProperty()
    patient_doc_id = StringProperty()

    active = BooleanProperty()

    ward = StringProperty()
    bed = StringProperty()

    culture_status = StringProperty()
    contamination = BooleanProperty()

    hiv_status = StringProperty()
    cd4_count = StringProperty()
    enrollment_date = DateProperty()

    labs_dict = DictProperty()

    last_encounter = StringProperty()
    last_encounter_date = DateTimeProperty()
    last_encounter_by = StringProperty()

    tally = DictProperty()

class ShinePatient(BasePatient):
    """
    A stub implementation of the Patient model
    """
    external_id = StringProperty() #patient_id for human readable
    cases = StringListProperty()
    aux_media = SchemaListProperty(AuxMedia)
    cache_doc_id = StringProperty() # add on cache id for the document with all the computed values for web reports


    @property
    def clinical_images(self):
        """
        Wrapper function that does two things:
        1: Scans existing submissions for photos
        2: Scans patient object for auxiliary submissions

        Returns them as a dictionary of arrays where {"image_context": [Image, Image, Image...]}

        These images will then be made displayable in templates via sorl-thumbnails
        """
        case = self.latest_case
        xform_id_keys = case.xform_ids
        db = CommCareCase.get_db()
        attach_submissions = db.view('slidesview/shine_image_submits', keys=xform_id_keys).all()

        #ret = OrderedDict()
        ret = []

        #step 1, check the case's submissions
        for submit in attach_submissions:

            xmlns = submit['value'][0]
            attachment_filename = submit['value'][1]
            xform_id = submit['id']
            submission = XFormInstance.get(xform_id)
            image_context = ''

            #get metadata on photo info
            if xmlns == STR_MEPI_ENROLLMENT_FORM:
                #it's a consent form
                #the field in question is consent_photo
                if submission.form.get('consent_photo', None) == attachment_filename:
                    image_context = "consent"
            elif xmlns == STR_MEPI_LAB_ONE_FORM:
                #emergency lab form, lab one
                #the fields in question are:
                #afb_stain_photo
                if submission.form.get('afb_stain_photo', None) == attachment_filename:
                    image_context = 'AFB Stain'
                #gram_stain_photo
                elif submission.form.get('gram_stain_photo', '') == attachment_filename:
                    image_context = 'Gram Stain'
            elif xmlns == STR_MEPI_LAB_TWO_FORM:
                #lab two
                #agar_photos/<field>
                if submission.form.get('agar_photos', None) is not None:
                    if submission.form['agar_photos'].get('macconkey', None) == attachment_filename:
                        image_context = 'Macconkey'
                    elif submission.form['agar_photos'].get('blood', None) == attachment_filename:
                        image_context = 'Blood'
                    elif submission.form['agar_photos'].get('chocolate', None) == attachment_filename:
                        image_context = 'Chocolate'
                    elif submission.form['agar_photos'].get('lowenstein-jensen', None) == attachment_filename:
                        image_context = 'Lowenstein-Jensen'
            elif xmlns == STR_MEPI_LAB_THREE_FORM:
            #vitek_photo
                if submission.form.get('vitek_photo',None) == attachment_filename:
                    image_context = 'Vitek'
                #api_strip_photo
                elif submission.form.get('api_strip_photo', None) == attachment_filename:
                    image_context = 'API Strip'
                pass
            elif xmlns == STR_MEPI_LAB_FOUR_FORM:
                #plate_image
                if submission.form.get('plate_image',None) == attachment_filename:
                    image_context = 'Plate Image'

            attachments_img_dict = AttachmentImage.objects.get_doc_attachments(submission)
            if attachment_filename in attachments_img_dict:
                ret.append((attachments_img_dict[attachment_filename], image_context))

        #step 2: check the AuxImages
        aux_img_dict = AttachmentImage.objects.get_doc_auxmedia(self)
        for aux, attach_img in aux_img_dict.items():
            ret.append((attach_img, aux['media_meta']['image_type']))
        return ret


    def cache_clinical_case(self):
        case = self.latest_case
        submissions = self._get_case_submissions(case)
        for s in submissions:
            formname = xmlns_display_map[s['xmlns']].replace(' ','_').lower()
        self._cached_submits=True

    def compute_cache(self):
        case = self.latest_case
        submissions = self._get_case_submissions(case)
        cache_doc = ShinePatientReportCache.get(self.cache_doc_id)

        cache_doc.ward = case.ward
        cache_doc.bed = case.bed
        cache_doc.sex = self.gender

        cache_doc.enrollment_date = case.opened_on.date()

        #compute last_encounter stuff
        last_submission = submissions[-1]
        last_submission_id = last_submission['_id']
        last_xmlns = last_submission['xmlns']
        recv = isodate.parse_datetime(last_submission['received_on'])
        cache_doc.last_encounter = xmlns_display_map[last_xmlns]
        cache_doc.last_encounter_date = recv
        cache_doc.last_encounter_by = last_submission['form']['Meta']['username']


        #cd4 count, hiv status
        seen_hiv = False
        seen_cd4 = False
        elab_submissions = []

        #for tally
        completed = dict()
        done_keys = xmlns_display_map.keys()
        for submit in submissions:
            if not seen_hiv and submit['xmlns'] == STR_MEPI_ENROLLMENT_FORM:
                if submit['form'].get('hiv_test', '') == "yes":
                    cache_doc.hiv_status = "yes"
                    seen_hiv = True

            if not seen_hiv and submit['xmlns'] == STR_MEPI_LABDATA_FORM:
                if submit['form'].has_key('hiv'):
                    hiv = submit['form']['hiv']
                    cache_doc.hiv_status = hiv
                    seen_hiv = True

            if not seen_cd4 and submit['xmlns'] == STR_MEPI_LABDATA_FORM:
               if submit['form'].has_key('hiv_followup'):
                    if submit['form']['hiv_followup']['cdfour'] != '':
                        cd4 = submit['form']['hiv_followup']['cdfour']
                        cache_doc.cd4_count = cd4
                        seen_cd4 = True
            if submit['xmlns'] == STR_MEPI_LAB_ONE_FORM:
                elab_submissions.append(submit)

            #tally calculation
            xmlns = submit['xmlns']
            displayname = xmlns_display_map[xmlns]
            if xmlns in done_keys:
                completed[displayname] = {'status': True, 'instance': True}
                done_keys.remove(submit['xmlns'])



        #labs dict
        lab_submissions = filter(lambda x: x['xmlns'] == STR_MEPI_LABDATA_FORM, submissions)
        cache_doc.labs_dict = merge_labs(lab_submissions, as_dict=True)

        #culture_status positive | negative
        sorted_labs = sorted(elab_submissions, key=lambda x: x['received_on'], reverse=True)
        if len(sorted_labs) == 0:
            cache_doc.culture_status = "[No Data]"
        else:
            latest_lab = sorted_labs[0]

            if latest_lab['form'].get('result', None) is None:
                #where there's no explicit result field

                bottle_string = latest_lab['form'].get('positive_bottles', '')
                if bottle_string == '':
                    cache_doc.culture_status = "negative"
                else:
                    cache_doc.culture_status = 'positive'


#                positives = bottle_string.split(' ')
#
#                if len(positives) > 0:
#                    cache_doc.culture_status = "positive"
#                else:
            else:
                #where there is an explicit result field
                if latest_lab['form']['result'] == 'negative':
                    cache_doc.culture_status = 'negative'
                elif latest_lab['form']['result'] == 'positive':
                    cache_doc.culture_status = 'positive'


        #active
        cache_doc.active = not case.closed
        #contamination
        if hasattr(case, 'contamination'):
            cache_doc.contamination = getattr(case, 'contamination', '') == 'yes'
        else:
            cache_doc.contamination = False


        #tally calculation
        tally = []
        #for n in form_sequence:
            #status = completed.get(n, [False, None])
            #tally.append([n,status])
        cache_doc.tally = completed

        cache_doc.save()
        return cache_doc

    def get_cached_object(self):
        """
        New cached document to store all the precomputed stuff for this patient.
        """
        if self.cache_doc_id is None:
            cache_doc = ShinePatientReportCache()
            cache_doc.patient_doc_id = self._id
            cache_doc.save()
            self.cache_doc_id = cache_doc._id
            self.save()
            return self.compute_cache()

        else:
            cache_doc = ShinePatientReportCache.get(self.cache_doc_id)
            return cache_doc

    def _get_case_submissions(self, case, wrap=False):
        attrib = '_case_submissions_%s' % case._id
        db = XFormInstance.get_db()

        submissions_str = cache.get(attrib, None)
        if submissions_str is not None:
            submissions = simplejson.loads(submissions_str)
        else:
            submissions = [db.open_doc(x) for x in case.xform_ids]
            submissions_json = simplejson.dumps(submissions)
            cache.set(attrib, submissions_json, 172800)

        if wrap:
            return [XFormInstance.wrap(x) for x in submissions]

        else:
            return submissions


    def _do_get_latest_case(self, invalidate=False):
        if invalidate:
            cache.delete('shinepatient_latest_case_%s' % self._id)

        cache_latest_case_str = cache.get('shinepatient_latest_case_%s' % self._id, None)
        if cache_latest_case_str is not None:
            raw_case_json = simplejson.loads(cache_latest_case_str)
            latest_case = CommCareCase.wrap(raw_case_json)
            return latest_case
        else:
            #no cache no internal cache, reget
            case_docs = [CommCareCase.get(x) for x in self.cases]
            sorted_docs = sorted(case_docs, key=lambda x: x.opened_on)
            latest_case = sorted_docs[-1]
            cache.set('shinepatient_latest_case_%s' % self._id, simplejson.dumps(latest_case.to_json()), 14400)
        if invalidate:
            attrib = '_case_submissions_%s' % latest_case._id
            cache.delete(attrib)
        return latest_case


    @property
    def latest_case(self):
        return self._do_get_latest_case()

    def is_unique(self):
        return True

    @property
    def enrollment_date(self):
        if hasattr(self, '_enrollment_date'):
            return self._enrollment_date
        self._enrollment_date =  self.latest_case.opened_on
        return self._enrollment_date

    @property
    def view_name(self):
        return "shine_single_patient"

    @property
    def get_cd4_count(self):
        if hasattr(self, "_cached_submits"):
            if not self._cached_submits:
                self.cache_clinical_case()
        else:
            self.cache_clinical_case()


        cd4="---"
        if hasattr(self, '_lab_data'):
            if self._lab_data['form'].has_key('hiv_followup'):
                if self._lab_data['form']['hiv_followup']['cdfour'] != '':
                    cd4 = self._lab_data['form']['hiv_followup']['cdfour']
                    return cd4
        return cd4


    def get_culture_status(self):
        if hasattr(self, "_get_culture_status"):
            return self._get_culture_status

        bottles = self.get_elab_bottle_data()

        if bottles == '[No Data]':
            return '[No Data]'

        if len(bottles) > 0:
            self._get_culture_status = 'positive'
            return 'positive'
        else:
            self._get_culture_status = 'negative'
            return 'negative'

    @property
    def get_hiv_status(self):
        """
        Return HIV positive/negative status
        """
        case = self.latest_case
        submissions = self._get_case_submissions(case)
        hiv ="no"
        for s in submissions:
            if s['xmlns'] == STR_MEPI_ENROLLMENT_FORM:
                if s['form'].get('hiv_test', '') == "yes":
                    return "yes"

            if s['xmlns'] == STR_MEPI_LABDATA_FORM:
                if s['form'].has_key('hiv'):
                    hiv = s['form']['hiv']
                    return hiv
        return hiv


    @property
    def last_activity(self):
        cases = CommCareCase.view("shinepatient/shine_patient_cases", key=self._id, include_docs=True).all()
        if len(cases) == 0:
            return datetime.mindate
        else:
            return cases[0].modified_on


    def get_last_action(self):
        case = self.latest_case
        cached_action = cache.get('patient_last_action_%s' % self._id, None)
        if cached_action is not None:
            last_submission = simplejson.loads(cached_action)
        else:
            case = self.latest_case
            #submissions = self._get_case_submissions(case)
            last_submission_id = case.xform_ids[-1]
            last_submission = XFormInstance.get_db().get(last_submission_id)
        xmlns = last_submission['xmlns']
        #2012-02-21T11:31:05Z
        recv = isodate.parse_datetime(last_submission['received_on'])
        cache.set('patient_last_action_%s' % self._id, simplejson.dumps(last_submission))
        return recv, xmlns_display_map[xmlns]

    @property
    def get_completed_tally(self):
        """
        Returns whether or not patient is active in the study (whether they've been discharged)
        Returns an array with tuples indicating form done-ness along with the submission itself
        """
        case = self.latest_case
        submissions = self._get_case_submissions(case)
        keys = xmlns_display_map.keys()
        completed = dict()
        full_len = len(keys)
        for i,s in enumerate(submissions):
            xmlns = s['xmlns']
            displayname = xmlns_display_map[xmlns]
            if xmlns in keys:
                completed[displayname] = (True, s)
                keys.remove(s['xmlns'])


        ret = []
        for n in form_sequence:
            status = completed.get(n, (False, None))
            ret.append((n,status))
        return ret


    def get_activity_history(self):
        """
        For patient Activity History Tab
        For all forms possible in system, fill it in as a section in the activity tab

        activities[xmlns] = [submit, submit...]

        returns: [(xmlns display, xmlns, [submit, submit...]), ... ]
        """
        case = self.latest_case
        submissions = self._get_case_submissions(case, wrap=True)
        activities_dict = dict()
        all_xmlns = xmlns_display_map.keys()

        for s in submissions:
            xmlns = s['xmlns']

            if xmlns in all_xmlns:
                all_xmlns.remove(xmlns)

            activity_arr = activities_dict.get(xmlns, [])
            activity_arr.append(s)
            activities_dict[xmlns] = activity_arr
        for xmlns in all_xmlns:
            #fill in the remainder of unseen xmlns as []
            activity_arr = activities_dict.get(xmlns, [])
            activities_dict[xmlns] = activity_arr

        ret = []
        for x in xmlns_sequence:
            ret.append((xmlns_display_map[x], x, activities_dict[x]))

        return ret



    def _do_get_emergency_lab_submission(self):
        if hasattr(self, '_elab'):
            return self._elab
        case = self.latest_case
        submissions = self._get_case_submissions(case)
        elab_submissions = filter(lambda x: x['xmlns'] == STR_MEPI_LAB_ONE_FORM, submissions)
        #hack: assume to be one here
        sorted_labs = sorted(elab_submissions, key=lambda x: x['received_on'], reverse=True)

        if len(sorted_labs) == 0:
            return None
        lab = sorted_labs[0]
        self._elab = lab
        return lab


    @property
    def get_emergency_lab_submit(self):
        return self._do_get_emergency_lab_submission()


    def get_elab_bottle_data(self):
        """
        Return an array of the positive bottles or [No Data]
        """
        lab = self._do_get_emergency_lab_submission()
        if lab is None:
            return "[No Data]"

        if lab['form'].get('positive_bottles', '') == '':
            return []
        positives = lab['form']['positive_bottles'].split(' ')
        return positives
        



    def get_lab_data(self):
        #get all clinical lab data submissions
        case = self.latest_case
        submissions = self._get_case_submissions(case)
        lab_submissions = filter(lambda x: x['xmlns'] == STR_MEPI_LABDATA_FORM, submissions)
        return merge_labs(lab_submissions)

    @property
    def get_current_bed(self):
        if hasattr(self, '_get_current_bed'):
            return self._get_current_bed
        else:
            self._get_current_bed  = self.latest_case.bed
            return self._get_current_bed

    @property
    def get_current_ward(self):
        if hasattr(self, '_get_current_ward'):
            return self._get_current_ward
        else:
            self._get_current_ward = self.latest_case.ward
            return self._get_current_ward


from .signals import *
