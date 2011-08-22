#this is a ghetto method to update a patient by submitting an xform directly via.
#<Phone1>857-334-1329</Phone1>
#<Phone1Type>Terae (daughter)</Phone1Type>
#
#<Phone2/>
#
#<Phone3>857-249-3684</Phone3>
#<Phone3Type>client's cell (CURRENTLY OUT OF SERVICE)</Phone3Type>
#
#<address1>11 East Main St. Mattapan, MA 02126</address1>
#<address1type>Mother's address</address1type>
#
#<address2>50 Blue Hill Ave. 3rd fl. Roxbury, 0</address2>
#<address2type>CURRENT ADDRESS</address2type>
from datetime import datetime
import re
import uuid
from casexml.apps.case.models import CommCareCase

xml_template = """
<data xmlns:jrm="http://dev.commcarehq.org/jr/xforms" xmlns="http://dev.commcarehq.org/pact/patientupdate" version="3" uiVersion="3">
    <Meta>
        <DeviceID>PatientUpdateForm</DeviceID>
        <TimeStart>%(time_start)s</TimeStart>
        <TimeEnd>%(time_end)s</TimeEnd>
        <username>%(username)s</username>
        <chw_id>%(chw_id)s</chw_id>
        <uid>%(uid)s</uid>
    </Meta>

    <pact_id>%(pact_id)s</pact_id>
    <case>
        <case_id>%(case_id)s</case_id>
        <date_modified>%(date_modified)s</date_modified>
        <update>
            %(update_block)s
        </update>
    </case>
</data>
"""

phone_template = """
<Phone%(num)s>%(number)s</Phone%(num)s>
<Phone%(num)sType>%(typestring)s</Phone%(num)sType>
"""

address_template_full = """
<address%(num)s>%(street)s %(city)s %(state)s %(postal_code)s</address%(num)s>
<address%(num)stype>%(typestring)s</address%(num)stype>
"""


address_template = """
<address%(num)s>%(address)s</address%(num)s>
<address%(num)stype>%(typestring)s</address%(num)stype>
"""


def generate_submission_from_cpatient(couchdoc):
    """
    This is the method to first push an unconverted patient
    """
    pass

def update_patient_casexml(user, patient_doc, active_phones, active_addresses):
    """
    Update casexml
    """
    data_dict = {}
    data_dict['time_start'] = datetime.utcnow()#.isoformat()
    phone_xml = []
    for i, p in enumerate(active_phones, start=1):
        if p == None:
            continue
        phone_xml.append(get_phone_xml(i, p['number'], typestring=p['description']))

    address_xml = []
    for i, a in enumerate(active_addresses, start=1):
        if a == None:
            continue
        address_xml.append(get_address_xml(i, a['address'], typestring=a['description']))



#    case = CommCareCase.get(patient_doc.case_id)
    data_dict['update_block'] = ''.join(phone_xml + address_xml)
    data_dict['uid'] = uuid.uuid4().hex
    data_dict['case_id'] = patient_doc.case_id
    data_dict['username'] = user.username
    data_dict['chw_id'] = user.id
    data_dict['date_modified'] = datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%S.000Z") # this is != to isoformat()!!!
    data_dict['pact_id'] = patient_doc.pact_id
    data_dict['time_end'] = datetime.utcnow() #datetime.utcnow().isoformat() + "Z"
    return xml_template % data_dict


def generate_update_xml_old(user, patient_doc, cphones, caddresses):
    """
    For a given patient and in memory phone and address objects, generate the xml.
    This is using the old cphone and cpatient models. This is a migration method.
    """

    data_dict = {}
    data_dict['time_start'] = datetime.utcnow()#.isoformat()
    phone_xml = []
    for i, p in enumerate(cphones, start=1):
        if p == None:
            continue
        phone_xml.append(get_phone_xml(i, p.number, typestring=p.description))

    address_xml = []
    for i, a in enumerate(caddresses, start=1):
        if a == None:
            continue
        address_xml.append(get_address_xml_full(i, a.street, a.city, a.state, a.postal_code, typestring=a.description))



    case = CommCareCase.get(patient_doc.case_id)
    data_dict['update_block'] = ''.join(phone_xml + address_xml)
    data_dict['uid'] = uuid.uuid4().hex
    data_dict['case_id'] = case._id
    data_dict['username'] = user.username
    data_dict['chw_id'] = user.id
    data_dict['date_modified'] = datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%S.000Z") # this is != to isoformat()!!!
    data_dict['pact_id'] = patient_doc.pact_id
    data_dict['time_end'] = datetime.utcnow() #datetime.utcnow().isoformat() + "Z"
    return xml_template % data_dict


def get_phone_xml(n, phone, typestring=None):
    """
    Generage a singular casexml phone block.
    
    """
    dict = {'num': n, 'number': phone,
            'typestring': typestring if typestring is not None or len(typestring) > 0 else ''}
    return phone_template % dict

def get_address_xml(n, address, typestring=None):
    if typestring == None:
        typestring = ''
    dict = { 'num': n, 'address': address,
             'typestring': typestring if typestring is not None or len(typestring) > 0 else ''}
    return address_template % dict



def get_address_xml_full(n, street, city, state, postal_code, typestring=None):
    dict = {'num': n, 'street': street, 'city': city, 'state': state, 'postal_code': postal_code,
            'typestring': typestring if typestring is not None or len(typestring) > 0 else ''}
    return address_template_full % dict


def get_blank_phone_xml(n):
    return "<Phone%(num)s/><Phone%(num)sType/>" % {'num': n}


def get_blank_address_xml(n):
    return "<address%(num)s/><address%(num)stype/>" % {'num': n}

