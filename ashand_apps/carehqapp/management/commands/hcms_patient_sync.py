# django imports
import simplejson
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
            pt_json = couchdoc.to_json()

            ret_json = {}
            ret_json['InternalUserID'] = pt_json['_id']
            ret_json['ExternalUserID'] = pt_json['study_id']
            ret_json['FirstName'] = pt_json['first_name']
            ret_json['LastName'] = pt_json['last_name']
            ret_json['Gender'] = pt_json['gender']

            if len(pt_json['address']) > 0:
                address = pt_json['address'][0]

                ret_json['Address1'] = address['street']
                ret_json['City'] = address['city']
                ret_json['State'] = address['state']
                ret_json['PostalCode'] = address['postal_code']
            else:
                ret_json['Address1'] = ''
                ret_json['City'] = ''
                ret_json['State'] = ''
                ret_json['PostalCode'] = ''
            if len(pt_json['phones']) > 0:
                ret_json['PhoneNumber'] = pt_json['phones'][0]['number']
            else:
                ret_json['PhoneNumber'] = ''
            ret_arr.append(ret_json)
        print simplejson.dumps(ret_arr)

