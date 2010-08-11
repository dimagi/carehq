import csv
from sys import stdin
from ashand.apps.patient.models import *

# is there seriously no 'Address 2 - Country'?
HEADER = (
    'PACTID',
    'Given Name',
    'Family Name',
    'CHW Membership',
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
    #stdin = open('PACT-csv/patient-data.csv')
    reader = csv.reader(stdin)

    rows = iter(reader)
    header = rows.next()

    if tuple(header) != tuple(HEADER):
        raise Exception("incorrect header")

    patients = []

    structure = (
        ('phone', 3, ('type', 'value')),
        ('address', 2, ('type', 'street', 'city', 'postal code', 'country')),
        ('provider', 9, ('type', 'number')),
    )
    def normalize(s):
        return s.lower().replace(' ',  '_')
    for row in rows:
        data = dict(zip(map(normalize, HEADER), row))
        patient = dict()
        for key in map(normalize, ('PACTID', 'Given Name', 'Family Name', 'CHW Membership')):
            patient[key] = data[key]
        
        for key, N, fields in structure:
            patient[key] = []
            for i in range(1,N+1):
                format = "%s %d - %%s" % (key, i)
                patient[key].append(tuple([data.get(format % f, '') for f in fields]))
        patients.append(patient)

    # patients = [{'pactid':123, 'phone':[{'type':...]}]
    def get_user(first, last):
        users = User.objects.filter(first_name=first_name, last_name=last_name)
        if users.count():
            if users.count() > 1:
                print "Multiple users named %s %s" % (first_name, last_name)
            # This is not a smart way to deal with two people with the same name
            user = users[0]
        else:
            username = '_'.join(map(normalize, (first_name, last_name)))
            while User.objects.filter(username=username):
                username += '_'
            user = User.objects.create_user(username, '', 'demo')
            user.first_name = first_name
            user.last_name = last_name
            user.save()
        return user
    
    for patient in patients:
        first_name, last_name = patient['given_name'], patient['family_name']
        user = get_user(first_name, last_name)
        #patient = Patient.objects.get_or_create(user=user)