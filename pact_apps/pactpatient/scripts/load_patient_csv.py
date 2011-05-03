import csv
from sys import stdin
from patient.models import Patient
from patient.models import PactPatient, CPhone, CAddress, CDotSchedule


# is there seriously no 'Address 2 - Country'?
from django.contrib.auth.models import User
from patient.models import Patient
import sys
from datetime import datetime

HEADER = (
#    'PACTID',
#    'Given Name',
#    'Family Name',
#    'CHW Membership',
#    'Phone 1 - Type',
#    'Phone 1 - Value',
#    'Phone 2 - Type',
#    'Phone 2 - Value',
#    'Phone 3 - Type',
#    'Phone 3 - Value',
#    'Address 1 - Type',
#    'Address 1 - Street',
#    'Address 1 - City',
#    'Address 1 - Postal Code',
#    'Address 1 - Country',
#    'Address 2 - Type',
#    'Address 2 - Street',
#    'Address 2 - City',
#    'Address 2 - Postal Code',
#    'Provider 1 - Type',
#    'Provider 1 - Number',
#    'Provider 2 - Type',
#    'Provider 2 - Number',
#    'Provider 3 - Type',
#    'Provider 3 - Number',
#    'Provider 4 - Type',
#    'Provider 4 - Number',
#    'Provider 5 - Type',
#    'Provider 5 - Number',
#    'Provider 6 - Type',
#    'Provider 6 - Number',
#    'Provider 7 - Type',
#    'Provider 7 - Number',
#    'Provider 8 - Type',
#    'Provider 8 - Number',
#    'Provider 9 - Type',
#    'Provider 9 - Number',
    'PACTID',
    'Given Name',
    'Family Name',
    'DOB',
    'Gender',
    'Arm',
    'HP',
    'ART Regimen',
    'Non-ART Regimen',
    'DOT - Sunday',
    'DOT - Monday',
    'DOT - Tuesday',
    'DOT - Wednesday',
    'DOT - Thursday',
    'DOT - Friday',
    'DOT - Saturday',
    'Phone 1 - Type',
    'Phone 1 - Value',
    'Phone 2 - Type',
    'Phone 2 - Value',
    'Phone 3 - Type',
    'Phone 3 - Value',
    'Address 1 - Type',
    'Address 1 - Street',
    'Address 1 - City',
    'Address 1 - Postal Code',
    'Address 1 - Country',
    'Address 2 - Type',
    'Address 2 - Street',
    'Address 2 - City',
    'Address 2 - Postal Code',
    'Provider 1 - Type',
    'Provider 1 - Number',
    'Provider 2 - Type',
    'Provider 2 - Number',
    'Provider 3 - Type',
    'Provider 3 - Number',
    'Provider 4 - Type',
    'Provider 4 - Number',
    'Provider 5 - Type',
    'Provider 5 - Number',
    'Provider 6 - Type',
    'Provider 6 - Number',
    'Provider 7 - Type',
    'Provider 7 - Number',
    'Provider 8 - Type',
    'Provider 8 - Number',
    'Provider 9 - Type',
    'Provider 9 - Number',
)

def run():    
    reader = csv.reader(stdin)
    rows = iter(reader)
    header = rows.next()
    if tuple(header) != tuple(HEADER):
        raise Exception("incorrect header")
    patients_arr = []
    structure = (
        ('phone', 3, ('type', 'value')),
        ('address', 2, ('type', 'street', 'city', 'postal code', 'country')),
        ('provider', 9, ('type', 'number')),
    )
    def normalize(s):
        return s.lower().replace(' ',  '_')
    
    for row in rows:
        data = dict(zip(map(normalize, HEADER), row))
        patient_dict = dict()
        #for key in map(normalize, ('PACTID', 'Given Name', 'Family Name', 'CHW Membership')):
        for key in map(normalize, ('PACTID',
                                   'Given Name',
                                   'Family Name',
                                   'DOB',
                                   'Gender',
                                   'Arm',
                                   'HP',
                                   'ART Regimen',
                                   'Non-ART Regimen',
                                   'DOT - Sunday',
                                   'DOT - Monday',
                                   'DOT - Tuesday',
                                   'DOT - Wednesday',
                                   'DOT - Thursday',
                                   'DOT - Friday',
                                   'DOT - Saturday')):
            patient_dict[key] = data[key]
        for key, N, fields in structure:
            patient_dict[key] = []
            for i in range(1,N+1):
                format = "%s %d - %%s" % (key, i)                             
                patient_dict[key].append(tuple([data.get(normalize(format % f), '') for f in fields]))
        
        patients_arr.append(patient_dict)

#
#    # patients_arr = [{'pactid':123, 'phone':[{'type':...]}]
#    def get_user(first, last):
#        users = User.objects.filter(first_name=first_name, last_name=last_name)
#        if users.count():
#            if users.count() > 1:
#                print "Multiple users named %s %s" % (first_name, last_name)
#            # This is not a smart way to deal with two people with the same name
#            user = users[0]
#        else:
#            username = '_'.join(map(normalize, (first_name, last_name)))
#            while User.objects.filter(username=username):
#                username += '_'
#            user = User.objects.create_user(username, '', 'demo')
#            user.first_name = first_name
#            user.last_name = last_name
#            user.save()
#        return user
#
    for patient_dict in patients_arr:
        first_name, last_name = patient_dict['given_name'], patient_dict['family_name']
        #user = get_user(first_name, last_name)
        
        sex = patient_dict['gender'].lower()[0]
        dob = datetime.strptime(patient_dict['dob'], "%m/%d/%Y").date() #%m/%d/%Y
        pact_id = patient_dict['pactid']

        arm = patient_dict['arm']
        hp = patient_dict['hp']

        art_regimen = patient_dict['art_regimen']
        non_art_regimen = patient_dict['non-art_regimen']

        ptquerystring = last_name.lower() + first_name.lower() + dob.strftime("%Y-%m-%d")
        existing_pts = PactPatient.view("patient/search", key=ptquerystring, include_docs=True).count()

        if existing_pts > 0:
            print "Patient already exists, skipping"
            continue

        django_patient = Patient()
        django_patient.doc_id=None
        django_patient.save()

        cpatient = PactPatient(django_uuid=django_patient.id,
                            pact_id=pact_id,
                            first_name = first_name,
                            last_name=last_name,
                            middle_name = '',
                            gender = sex,
                            birthdate = dob,
                            art_regimen=art_regimen,
                            non_art_regimen=non_art_regimen,
                            primary_hp = hp,
                            arm = arm)


        raw_phones = patient_dict['phone']
        couched_phones = []
        addresses = patient_dict['address']
        couched_addresses = []
        #chw_membership = patient_dict['chw_membership']
        providers = patient_dict['provider']


        #pt_model.notes = str([chw_membership,providers])
        #pt_model.save()
#        patient_dict.user = user
#        patient_dict.sex="f"
#        patient_dict.save()

        for phone in raw_phones:
            ident = phone[0]
            val = phone[1]
            newphone = CPhone(description=ident, number=val, created=datetime.utcnow())
            cpatient.phones.append(newphone)

        for addr in addresses:            
            if addr[0] == '' and addr [1] == '' and addr[2] == '':
                continue
            newaddress = CAddress(type=addr[0], street=addr[1], city=addr[2], state="MA", postal_code=addr[3])
            cpatient.address.append(newaddress)

        days_of_week = ['sunday','monday','tuesday','wednesday','thursday','friday','saturday']
        for day in days_of_week:
            cschedule= CDotSchedule(day_of_week=day, hp_username=patient_dict['dot_-_%s' % day])
            cpatient.dots_schedule.append(cschedule)


        cpatient.save()
        django_patient.doc_id = cpatient._id
        django_patient.save()

#        #dmyung:  ok we're just going guns a blazing to make our pact users, surely we will make this cleaner for future generations
#        try:
#            pact_identifier_type  = IdentifierType.objects.get(description="PACT Internal Identifier", shortname="PACTID")
#        except:
#            pact_identifier_type  = IdentifierType(description="PACT Internal Identifier", shortname="PACTID")
#            pact_identifier_type.save()
#
#        if pt_model.identifiers.all().filter(id_type=pact_identifier_type, id_value=patient_dict['pactid']).count() == 0:
#            try:
#                pact_id = PatientIdentifier.objects.get(id_type=pact_identifier_type, id_value=patient_dict['pactid'])
#            except:
#                pact_id = PatientIdentifier(id_type=pact_identifier_type, id_value=patient_dict['pactid'])
#                pact_id.save()
#            pt_model.identifiers.add(pact_id)
#
        
        
        
        
        
        
        
