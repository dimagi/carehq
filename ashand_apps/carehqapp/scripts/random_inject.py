from datetime import timedelta, datetime
from django.contrib.contenttypes.models import ContentType
import os
from carehq_core import carehq_api
from issuetracker import constants as caseconstants
from issuetracker.models import Case
import csv
from patient.models.patientmodels import Patient
import random
from permissions.models import Role, PrincipalRoleRelation

def run():
    """
    inject cases into system for aug 2011 usability studies
    """
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
        if row[2] == "threshold":
           continue

        pt = random.choice(patients)
        careteam_dict = carehq_api.get_careteam_dict(pt.couchdoc)
        actors = []
        for k, a in careteam_dict.items():
            actors+=a

        if row[3] == 'caregiver':
            actor = random.choice(careteam_dict[Role.objects.get(name='ashand-Caregiver')])
        elif row[3] == 'patient':
            ctype = ContentType.objects.get_for_model(pt)
            proles = PrincipalRoleRelation.objects.filter(content_type=ctype, content_id=pt.id).filter(role__display="Patient")
            actor = proles[0].actor
        elif row[3] == 'provider':
            #actor = random.choice(careteam_dict[Role.objects.get(name='ashand-GeneralProvider')] + careteam_dict[Role.objects.get(name='ashand-PrimaryProvider')])
            actor = random.choice(careteam_dict[Role.objects.get(name='ashand-GeneralProvider')])
        else:
            actor =   random.choice(actors)



        if row[0].count('%s') > 0:
            desc = row[0] % (pt.couchdoc.first_name)
        else:
            desc=row[0]
        if row[1].count('%s') > 0:
            body = row[1] % (pt.couchdoc.first_name)
        else:
            body=row[1]
        newcase = Case.objects.new_case(row[2],
                                        actor,
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



