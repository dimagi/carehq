from StringIO import StringIO
import random
import os
import uuid
from django.core.urlresolvers import reverse
from contrib_apps.django_digest.test import Client
import Image, ImageDraw
import settings
from patient.utils.names import NAMES
from dimagi.utils.post import post_data

patient_registration_xml = """
<data xmlns:jrm="http://dev.commcarehq.org/jr/xforms" xmlns="http://shine.commcarehq.org/patient/reg" uiVersion="2" version="2" name="Patient Registration">
  <Meta>
    <DeviceID>354957030960291</DeviceID>
    <TimeStart>2011-09-07T03:21:55.703+02</TimeStart>
    <TimeEnd>2011-09-07T03:26:27.625+02</TimeEnd>
    <username>shine</username>
    <chw_id>2</chw_id>
    <uid>%(uid)s</uid>
  </Meta>
  <case>
    <case_id>%(case_id)s</case_id>
    <date_modified>2011-09-07T03:26:27.625+02</date_modified>
    <create>
      <case_type_id>shine_patient</case_type_id>
      <user_id>2</user_id>
      <case_name>test, dan</case_name>
      <external_id>%(external_id)s</external_id>
    </create>
    <update>
      <first_name>%(first_name)s</first_name>
      <last_name>%(first_name)s</last_name>
      <sex>male</sex>
      <dob>1980-09-06</dob>
      <barcode_one_aerobic>6001240206256</barcode_one_aerobic>
      <barcode_two_aerobic>33070254</barcode_two_aerobic>
      <barcode_mycolytic>2633223348</barcode_mycolytic>
      <bloodwork_pending>one</bloodwork_pending>
      <patient_open>yes</patient_open>
      <consent_status>obtained</consent_status>
      <ward>99</ward>
      <bed>88</bed>
    </update>
  </case>
  <name>
    <first_name>dan</first_name>
    <last_name>test</last_name>
    <patient_id>999999999</patient_id>
  </name>
  <dob_known>no</dob_known>
  <age>31</age>
  <sex>male</sex>
  <temperature>38.0</temperature>
  <hiv_test>no</hiv_test>
  <location>
    <ward>99</ward>
    <bed>88</bed>
  </location>
  <consent>yes</consent>
  <consent_photo>consent.jpg</consent_photo>
  <barcode_one_aerobic>6001240206256</barcode_one_aerobic>
  <barcode_two_aerobic>33070254</barcode_two_aerobic>
  <barcode_mycolytic>2633223348</barcode_mycolytic>
</data>
"""

lab_one_submission = """
<data xmlns:jrm="http://dev.commcarehq.org/jr/xforms" xmlns="http://shine.commcarehq.org/lab/one" uiVersion="2" version="2" name="Lab Data">
  <Meta>
    <DeviceID>354957030960291</DeviceID>
    <TimeStart>2011-09-07T03:47:59.918+02</TimeStart>
    <TimeEnd>2011-09-07T03:48:12.117+02</TimeEnd>
    <username>shine</username>
    <chw_id>2</chw_id>
    <uid>%(lab_uuid)s</uid>
  </Meta>
  <case>
    <case_id>%(case_id)s</case_id>
    <date_modified>2011-09-07T03:48:12.118+02</date_modified>
    <update>
      <bloodwork_pending>two</bloodwork_pending>
    </update>
  </case>
  <positive_bottles>one_aerobic two_aerobic</positive_bottles>
  <gram_stain>gpc_pairs gpc_clusters</gram_stain>
  <gram_stain_photo>gonorreah.jpg</gram_stain_photo>
  <afb_stain>present</afb_stain>
  <afb_stain_photo>streptococci.jpg</afb_stain_photo>
</data>
"""

def get_image_stream(full_filepath):
    image_f = open(full_filepath, 'rb')
    return image_f

def create_image(x, y, word):
    """
    Return a buffer of a jpeg image
    """
    im = Image.new("RGB",(x,y))
    drtext = ImageDraw.Draw(im)
    drtext.text((10,10), str(word),fill="white")

    buf = StringIO()
    im.save(buf,"JPEG")
    buf.seek(0)
    buf.name = ""
    return buf


def generate_mock_patient():
    pdict = _mkpatient_dict()
    final_xml = get_registration_xml(pdict)
    consent_image = create_image(100,100, uuid.uuid4().hex)
    resp = do_submit(final_xml, attachments_list=[('consent.jpg', consent_image)])

    labdict = {'case_id': pdict['case_id'], 'lab_uuid':uuid.uuid4().hex}
    lab_xml = lab_one_submission % labdict
    resp2 = do_submit(lab_xml, attachments_list = [
        ('streptococci.jpg', get_image_stream(os.path.join(settings.filepath,'shine_apps','shinecarehq', 'tests','sampledata','streptococci.jpg'))),
        ('gonorrhea.jpg', get_image_stream(os.path.join(settings.filepath,'shine_apps','shinecarehq', 'tests','sampledata','gonorrhea.jpg'))),
    ], is_unit_test=False
    )

    print resp2







def _mkpatient_dict():
    data_dict = {}

    some_name = random.choice(NAMES)

    data_dict['uid'] = uuid.uuid4().hex
    data_dict['case_id'] = uuid.uuid4().hex
    data_dict['external_id'] = random.randint(100000,9999999)
    data_dict['first_name'] = some_name['firstname']
    data_dict['last_name'] = some_name['lastname']
    return data_dict


def get_registration_xml(pdict):
    final_xml = patient_registration_xml % pdict
    return final_xml


def do_submit(xml, attachments_list=[], is_unit_test=True):
    """
    
    """
    client = Client()
    final_dict = {}
    xml_f = StringIO(xml.encode('utf-8'))
    xml_f.name = 'form.xml'

    final_dict['xml_submission_file']=xml_f

    for atuple in attachments_list:
        final_dict[atuple[0]] = atuple[1]

    if is_unit_test:
        response = client.post(reverse('receiver_post'), final_dict)
    else:
        response = post_data(xml, 'localhost:8000/receiver/', path=None, use_curl=True, is_odk=True, attachments=[(x[0], x[1].name) for x in attachments_list])
    return response

