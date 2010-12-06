from patient.models.djangomodels import Patient
from patient.models.couchmodels import CPatient, CDotWeeklySchedule
from datetime import datetime, timedelta
import uuid

days_of_week = ['sunday','monday','tuesday','wednesday','thursday','friday','saturday']

def run():
    td = timedelta(days=365)
    for pt in Patient.objects.all():
        for phone in pt.couchdoc.phones:
            phone.phone_id = uuid.uuid1().hex
            phone.save()
            print "Set patient phone

