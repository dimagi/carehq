# django imports
import base64
import simplejson
import uuid
from django.core.management.base import BaseCommand

# permissions imports
# inspired source from
# https://bitbucket.org/diefenbach/django-lfc/src/1529b35fb12e/lfc/management/commands/lfc_init.py
# An implementation of the permissions for a CMS framework.
from patient.models import Patient

#DataSource: "Intel Health Guide System"
#ExternalUserID
#InternalUserID
#FirstName
#LastName
#Birthdate
#Gender
#TimeZoneID: 30
#TimeZone: "Eastern Standard Time"
#StatusID: 1
#Address1
#City
#State
#Country
#PostalCode
#PhoneNumber
#Email1?
#PINEntryRequired: 0
#CultureID: 1033



class Command(BaseCommand):
    args = ''
    help = """Generate the patients in a json form to then push to HCMS"""

    def handle(self, *args, **options):
        django_patients = Patient.objects.all()

        ret_arr = []
        for dj_patient in django_patients:
            couchdoc = dj_patient.couchdoc
            if couchdoc._id == 'c6f12e6c459c45b9b0e7272d1b23f932' or couchdoc._id == '157e9fae3800489b9dcb533cb1d48f66' or couchdoc._id == '2269122d211c472eb904ee2c4cf1ddf9'\
                or couchdoc._id == 'f21a992108fe4874ad5d0a8d38ef7847' or couchdoc._id == '36264411fa4643f4a2675742170b447c':
                continue
            pt_json = couchdoc.to_json()

            ret_json = {}
            doc_id = pt_json['_id']
            ret_json['DocID'] = base64.b64encode(uuid.UUID(doc_id).bytes)
            ret_json['ExternalUserID'] = pt_json['study_id']
            ret_json['FirstName'] = pt_json['first_name']
            ret_json['LastName'] = "SUBJECT" #pt_json['last_name']
            ret_json['Gender'] = pt_json['gender']

            if len(pt_json['address']) > 0:
                address = pt_json['address'][0]

                ret_json['Address1'] = "585 Massachusetts Avenue Suite 3" #address['street']
                ret_json['City'] = "Cambridge" #address['city']
                ret_json['State'] = "MA" #address['state']
                ret_json['PostalCode'] = "02139" #address['postal_code']
            else:
                ret_json['Address1'] ="585 Massachusetts Avenue Suite 3"
                ret_json['City'] = 'Cambridge'
                ret_json['State'] = 'MA'
                ret_json['PostalCode'] = '02139'
            if len(pt_json['phones']) > 0:
                ret_json['PhoneNumber'] = '617-649-2214' #pt_json['phones'][0]['number']
            else:
                ret_json['PhoneNumber'] = '617-649-2214'
            ret_arr.append(ret_json)
        print simplejson.dumps(ret_arr)

