from patient.models.djangomodels import Patient
from patient.models.couchmodels import CPatient, CDotWeeklySchedule
from datetime import datetime, timedelta
import uuid

days_of_week = ['sunday','monday','tuesday','wednesday','thursday','friday','saturday']

def run():
    for pt in Patient.objects.all():
        for i in range(0, len(pt.couchdoc.phones)):
            pt.couchdoc.phones[i].phone_id = uuid.uuid1().hex
        pt.couchdoc.save()
        print "Set patient phone %s" % (pt.id)


