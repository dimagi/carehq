from django.db.models import *
from patient.models import Patient
from django.db import models

import simplejson
import time, datetime

# Create your models here.
from django.contrib.auth.models import User

ADHERENCE_CHOICES = (
    ("empty", "Empty"),
    ("partial", "Partial"),
    ("full", "Full"),
)
METHOD_CHOICES = (
    ("pillbox", "Pillbox"),
    ("direct", "Direct"),
    ("self", "Self"),
)
TIME_LABEL_LOOKUP = (
    (),
    ('Dose',),
    ('Morning', 'Evening'),
    ('Morning', 'Noon', 'Evening'),
    ('Morning', 'Noon', 'Evening', 'Bedtime'),
)
TIME_LABELS = ('Dose', 'Morning', 'Noon', 'Evening', 'Bedtime')

class Observation(Model):
    doc_id = models.CharField(max_length=32, db_index=True)
    patient = ForeignKey(Patient)
    provider = ForeignKey(User) #should be actor but for short trial this is a user becauseonly chw's are users at the moment
    
    date = DateField(blank=False, null=False)
    is_art = BooleanField() # is Anti Retroviral Treatment
    adherence = CharField(max_length=10, choices=ADHERENCE_CHOICES)
    method = CharField(max_length=10, choices=METHOD_CHOICES)
    note = CharField(max_length=100, null=True, blank=True)
    dose_number = IntegerField()
    total_doses = IntegerField()
    
    def __repr__(self):
        return u"dots.models.Observation(%s)" % (', '.join(
            ["%s=%r" % (field, getattr(self, field)) for field in self._meta.get_all_field_names()]))
    
    def get_time_label(self):
        """
        returns an English time label out of
        'Dose', 'Morning', 'Noon', 'Evening', 'Bedtime'
        """
        return TIME_LABEL_LOOKUP[self.total_doses][self.dose_number]
    @classmethod
    def get_time_labels(cls, total_doses):
        return TIME_LABEL_LOOKUP[total_doses]
    @classmethod
    def from_json(cls, json, patient, user, xforminstance):
        if isinstance(patient, basestring):
            patient = Patient.objects.get(id=patient)  # lookup by uuid
        data = simplejson.loads(json)
        days = data['days']
        last_date = _date_from_string(data['anchor'])
        models = []
        dates = [last_date - datetime.timedelta(n) for n in reversed(range(len(days)))]
        for date, day in zip(dates, days):
            for drug, is_art in zip(day, (False, True)):
                total_doses = len(drug)
                for dose_number, observation in enumerate(drug):
                    try:
                        adherence, method = observation
                        note = None
                    except Exception, ex:
                        adherence, method, note = observation
                        print "Observation exception: %s" % (ex.message)
                    if adherence != 'unchecked':
                        models.append(
                            Observation(
                                doc_id=xforminstance._id, patient=patient, provider=user,
                                date=date, is_art=is_art, adherence=adherence, method=method,
                                note=note, dose_number=dose_number, total_doses=total_doses
                            )
                        )
        for model in models: 
            model.save()
                    
        return models
def _date_from_string(s):
    """
    >>> _date_from_string("18 Aug 2010 04:00:00 GMT")
    datetime.date(2010, 8, 18)
    """
    return datetime.date(*time.strptime(s, "%d %b %Y %H:%M:%S %Z")[:3])
    

from dotsview import signals