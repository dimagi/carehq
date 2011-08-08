from carehqapp.scripts.demo.demo_cases import DEMO_CASES
from datetime import timedelta, datetime
import os
from casetracker import constants as caseconstants
from casetracker.models import Case
import csv
from patient import careteam_api
from patient.models.patientmodels import Patient
import random

def run():
    Case.objects.all().delete()
    filepath = os.path.abspath(os.path.dirname(__file__))
    patients = Patient.objects.all()
    demo_reader = csv.reader(open(os.path.join(filepath, 'demo', 'demo_cases.csv'), 'rb'), delimiter=',', quotechar='"')
    first = True
    for row in demo_reader:
        if first:
            #burn the headline row
            first=False
            continue

        pt = random.choice(patients)
        careteam_dict = careteam_api.get_careteam(pt)
        actors = []
        for k, a in careteam_dict.items():
            actors+=a


        if row[0].count('%s') > 0:
            desc = row[0] % (pt.couchdoc.first_name)
        else:
            desc=row[0]
        if row[1].count('%s') > 0:
            body = row[1] % (pt.couchdoc.first_name)
        else:
            body=row[1]
        newcase = Case.objects.new_case(row[2],
                              random.choice(actors),
                              desc,
                              body,
                              random.choice(caseconstants.PRIORITY_CHOICES)[0],
                              patient=pt,
                              status=caseconstants.STATUS_CHOICES[0][0],
                              activity=caseconstants.CASE_EVENT_CHOICES[0][0],
                              )

        startdelta = timedelta(hours=random.randint(0,200)) #sometime in the past 3
        fixed_time = datetime.utcnow() - startdelta
        newcase.opened_date = fixed_time
        newcase.assigned_to = random.choice(actors)
        newcase.save(activity=caseconstants.CASE_EVENT_CHOICES[2][0])
        print "Created case %s for patient %s by %s" % (newcase.description, pt.couchdoc.first_name+" "+pt.couchdoc.last_name, newcase.opened_by.name)



