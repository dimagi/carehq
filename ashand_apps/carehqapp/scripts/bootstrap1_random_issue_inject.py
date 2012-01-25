from datetime import timedelta, datetime
import pdb
from django.contrib.contenttypes.models import ContentType
import os
from carehq_core import carehq_api, carehq_constants
from issuetracker import issue_constants as caseconstants
from issuetracker.models import Issue
import csv
from issuetracker.models.issuecore import IssueCategory
from patient.models import Patient
import random
from permissions.models import Role, PrincipalRoleRelation

def run():
    """
    inject cases into system for aug 2011 usability studies
    """
    Issue.objects.all().delete()
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
            actor = random.choice(careteam_dict[Role.objects.get(name=carehq_constants.role_caregiver)])
        elif row[3] == 'patient':
            #get the actor for the patient in question
            actor = pt.get_actor.actor
        elif row[3] == 'provider':
            #actor = random.choice(careteam_dict[Role.objects.get(name='ashand-GeneralProvider')] + careteam_dict[Role.objects.get(name='ashand-PrimaryProvider')])
            actor = random.choice(careteam_dict[Role.objects.get(name=carehq_constants.role_provider)])
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

        if actor is None:
            pdb.set_trace()
        newcase = Issue.objects.new_issue(
                                      random.choice(IssueCategory.objects.all()),
                                      actor,
                                      desc,
                                      body,
                                      random.choice(caseconstants.PRIORITY_CHOICES)[0],
                                      patient=pt,
                                      status=caseconstants.STATUS_CHOICES[0][0],
                                      activity=caseconstants.ISSUE_EVENT_CHOICES[0][0],
                              )

        startdelta = timedelta(hours=random.randint(0,200)) #sometime in the past 3
        fixed_time = datetime.utcnow() - startdelta
        newcase.opened_date = fixed_time
        newcase.assigned_to = random.choice(actors)
        newcase.save(actor, activity=caseconstants.ISSUE_EVENT_CHOICES[2][0])
        print "Created case %s for patient %s by %s" % (newcase.description, pt.couchdoc.first_name+" "+pt.couchdoc.last_name, newcase.opened_by.name)



