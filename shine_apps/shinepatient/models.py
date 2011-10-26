from datetime import datetime, timedelta
import random
from couchdbkit.ext.django.schema import Document, SchemaListProperty
from casexml.apps.case.models import CommCareCase
from couchforms.models import XFormInstance
from patient.models.patientmodels import BasePatient
from couchdbkit.schema.properties import StringProperty, StringListProperty, DateTimeProperty
from shineforms.lab_utils import merge_labs
from shineforms.constants import xmlns_display_map, form_sequence, xmlns_sequence, STR_MEPI_ENROLLMENT_FORM, STR_MEPI_LABDATA_FORM, STR_MEPI_LAB_TWO_FORM, STR_MEPI_LAB_FOUR_FORM, STR_MEPI_LAB_THREE_FORM, STR_MEPI_LAB_ONE_FORM


class AuxImage(Document):
    uploaded_date = DateTimeProperty()
    uploaded_by = StringProperty()
    uploaded_filename = StringProperty() #the uploaded filename info
    checksum = StringProperty()
    attachment_id = StringProperty() #the actual attachment id in _attachments
    image_type = StringProperty()
    notes = StringProperty()





class ShinePatient(BasePatient):
    """
    A stub implementation of the Patient model
    """
    external_id = StringProperty() #patient_id for human readable

    cases = StringListProperty()

    aux_images = SchemaListProperty(AuxImage)


    def _get_or_create_image_from_submission(self, submission, attachment_filename):
        #check if an ImageAttachment exists for it.
        imgs = ImageAttachment.objects.filter(xform_id=submission._id, attachment_key=attachment_filename)
        if imgs.count() == 0:
            #make new ImageAttachment
            new_img = ImageAttachment()
            attach_dict = submission._attachments.get(attachment_filename,None)
            img = ImageAttachment()

            img.patient_guid = self._id
            img.xform_id = submission._id
            img.attachment_key = attachment_filename
            img.content_length = attach_dict['length']
            img.content_type = attach_dict['content_type']

            imgfile = ContentFile(submission.fetch_attachment(attachment_filename, stream=True).read())
            img.image.save(attachment_filename, imgfile)
            img.save()
        else:
            #verify checksums are equal
            img = imgs[0]
        return img
    def _get_or_create_image_from_aux(self, aux_image):
                #check if an ImageAttachment exists for it.
        attach_dict = self._attachments.get(aux_image.attachment_id,None)
        imgs = ImageAttachment.objects.filter(patient_guid = self._id, attachment_key=aux_image.attachment_id)
        if imgs.count() == 0:
            #make new ImageAttachment
            new_img = ImageAttachment()
            img = ImageAttachment()

            img.patient_guid = self._id
            img.attachment_key = aux_image.attachment_id
            img.content_length = attach_dict['length']
            img.content_type = attach_dict['content_type']

            imgfile = ContentFile(self.fetch_attachment(aux_image.attachment_id, stream=True).read())
            img.image.save(aux_image.attachment_id, imgfile)
            img.save()
        else:
            #verify checksums are equal
            img = imgs[0]
        return img


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
                    if submission.form['agar_photos']['macconkey'] == attachment_filename:
                        image_context = 'Macconkey'
                    elif submission.form['agar_photos'].get('blood', None) == attachment_filename:
                        image_context = 'Blood'
                    elif submission.form['agar_photos'].get('chocolate', None) == attachment_filename:
                        image_context = 'Chocolate'
                    elif submission.form['agar_photos'].get('lowenstein-jensen', None) == attachment_filename:
                        image_context = 'Lowenstein-Jensen'
                pass
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
            img = self._get_or_create_image_from_submission(submission, attachment_filename)
            ret.append((img, image_context))

        #step 2: check the AuxImages
        for aux in self.aux_images:
            img = self._get_or_create_image_from_aux(aux)
            ret.append((img, aux.image_type))

        print ret


        return ret


    def cache_clinical_case(self):
        case = self.latest_case
        submissions = self._get_case_submissions(case)

        for s in submissions:
            formname = xmlns_display_map[s.xmlns].replace(' ','_').lower()
            setattr(self, "_%s" % formname, s)
        self._cached_submits=True

    def _get_case_submissions(self, case):
        attrib = '_case_submissions_%s' % case._id
        if hasattr(self, attrib):
            return getattr(self, attrib)
        else:
            submissions = [XFormInstance.get(x) for x in case.xform_ids]
            setattr(self, attrib, submissions)
            return submissions



    @property
    def latest_case(self):
        if hasattr(self,'_latest_case'):
            return self._latest_case

        case_docs = [CommCareCase.get(x) for x in self.cases]
        sorted_docs = sorted(case_docs, key=lambda x: x.opened_on)
        self._latest_case = sorted_docs[-1]
        return self._latest_case

    def is_unique(self):
        return True

    @property
    def enrollment_date(self):
        return self.latest_case.opened_on

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


    @property
    def get_culture_status(self):
        bottles = self.get_elab_bottle_data

        if bottles == '[No Data]':
            return '[No Data]'

        if len(bottles) > 0:
            return 'positive'
        else:
            return 'negative'


    @property
    def get_status(self):
        case = self.latest_case
        submissions = self._get_case_submissions(case)


    @property
    def get_hiv_status(self):
        case = self.latest_case
        submissions = self._get_case_submissions(case)
        hiv ="No"
        for s in submissions:
            if s.xmlns == STR_MEPI_ENROLLMENT_FORM:
                if s['form']['hiv_test'] == "yes":
                    return "yes"

            if s.xmlns == STR_MEPI_LABDATA_FORM:
                if s['form'].has_key('hiv'):
                    hiv = s['form']['hiv']
                    return hiv
        return hiv

    @property
    def get_current_status(self):
        return "Bloodwork > Positive > Lab2"

    @property
    def last_activity(self):
        cases = CommCareCase.view("shinepatient/shine_patient_cases", key=self._id, include_docs=True).all()
        if len(cases) == 0:
            #return "No activity"
            return datetime.mindate
        else:
            return cases[0].modified_on



    @property
    def get_last_action(self):
        case = self.latest_case
        submissions = self._get_case_submissions(case)
        xmlns = submissions[-1]['xmlns']
        recv = submissions[-1]['received_on']

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
        """
        case = self.latest_case
        submissions = self._get_case_submissions(case)
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

    @property
    def get_current_status(self):
        """
        Returns whether or not patient is active in the study (whether they've been discharged)
        """
        case = self.latest_case
        submissions = self._get_case_submissions(case)
        keys = xmlns_display_map.keys()
        full_len = len(keys)
        for i,s in enumerate(submissions):
            if s['xmlns'] in keys:
                keys.remove(s['xmlns'])
        if len(keys) != 0:
            return "%d/%d" % (full_len-len(keys), full_len)
        else:
            return "[Done]"

    @property
    def data_complete(self):
        """
        todo: Do an analysis of all the fields collected in all forms to determine if dataset is complete
        """
        return random.choice([True, False])

    @property
    def is_positive(self):
        """
        Determine positivity from submitted form TODO
        """
        return random.choice([True, False])


    def _do_get_emergency_lab_submission(self):
        if hasattr(self, '_elab'):
            return self._elab
        case = self.latest_case
        submissions = self._get_case_submissions(case)
        elab_submissions = filter(lambda x: x.xmlns == STR_MEPI_LAB_ONE_FORM, submissions)
        #hack: assume to be one here
        sorted_labs = sorted(elab_submissions, key=lambda x: x.received_on, reverse=True)

        if len(sorted_labs) == 0:
            return None
        lab = sorted_labs[0]
        self._elab = lab
        return lab


    @property
    def get_emergency_lab_submit(self):
        return self._do_get_emergency_lab_submission()


    @property
    def get_elab_bottle_data(self):
        """
        Return an array of the positive bottles or [No Data]
        """
        lab = self._do_get_emergency_lab_submission()
        if lab is None:
            return "[No Data]"

        if lab.form['positive_bottles'] == '':
            return []
        positives = lab.form['positive_bottles'].split(' ')
        return positives
        




    @property
    def get_lab_data(self):
        #get all clinical lab data submissions
        case = self.latest_case
        submissions = self._get_case_submissions(case)
        lab_submissions = filter(lambda x: x.xmlns == STR_MEPI_LABDATA_FORM, submissions)


        return merge_labs(lab_submissions)

    @property
    def get_current_bed(self):
        if hasattr(self, '_enrollment'):
            return self._enrollment.form['location']['bed']
        else:
            return 'Unknown'

    @property
    def get_current_ward(self):
        if hasattr(self, '_enrollment'):
            return self._enrollment.form['location']['ward']
        else:
            return 'Unknown'



from signals import *
