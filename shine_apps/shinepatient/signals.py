import uuid
from casexml.apps.case.models import CommCareCase
from couchforms.signals import xform_saved
import logging
import simplejson
from shinepatient.models import ShinePatient
from receiver.signals import successful_form_received
from django.core.files.base import ContentFile
from slidesview.models import ImageAttachment
   
def process_shinepatient_registration(sender, xform, **kwargs):
    try:
        if xform.xmlns != "http://shine.commcarehq.org/patient/reg":
            return
        try:
            case_id = xform['form']['case']['case_id']
            case_doc = CommCareCase.get(case_id)

            newptdoc = ShinePatient()
            newptdoc.external_id = case_doc['external_id']
            newptdoc.first_name = case_doc['first_name']
            newptdoc.last_name = case_doc['last_name']
            newptdoc.gender = case_doc['sex']
            newptdoc.birthdate = case_doc['dob']
            newptdoc.cases.append(case_id)
            newptdoc.save()

        except Exception, ex:
            logging.error("Error, shine patient submission: %s" % (ex))

    except:
        logging.error("Error processing the submission due to an unknown error.")
        raise
successful_form_received.connect(process_shinepatient_registration)


def process_bloodwork_attachments(sender, xform, **kwargs):
    try:
        if xform.xmlns != "http://shine.commcarehq.org/bloodwork/entry":
            return
        try:
            for k, v in xform._attachments.items():
                if k == 'form.xml':
                    continue
                img = ImageAttachment()
                img.xform_id = xform._id
                img.attachment_key = k
                img.content_length = v['length']
                img.content_type = v['content_type']

                imgfile = ContentFile(xform.fetch_attachment(k, stream=True).read())
                img.image.save(k, imgfile)
                img.save()
        except Exception, ex:
            logging.error("Error, bloodwork attachment submission error: %s" % (ex))

    except:
        logging.error("Error processing the submission due to an unknown error.")
        raise
successful_form_received.connect(process_bloodwork_attachments)
