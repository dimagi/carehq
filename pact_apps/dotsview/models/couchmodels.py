from django.db.models import *
from patient.models import Patient
from couchdbkit.ext.django.schema import *
import simplejson
import time, datetime

# Create your models here.

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

class CObservation(Document):
    doc_id = StringProperty()
    patient = StringProperty() #case id
    
    pact_id = StringProperty() #patient pact id
    provider = StringProperty()
    
    anchor_date = DateTimeProperty()
    observed_date = DateTimeProperty()
    
    submitted_date = DateTimeProperty()
    created_date = DateTimeProperty()
    
    is_art = BooleanField()
    dose_number=IntegerProperty()
    total_doses = IntegerProperty()
    adherence=StringProperty()
    method=StringProperty()
    
    day_index = IntegerProperty()
    
    note = StringProperty()
    
    @property
    def adinfo(self):
        """helper function to concatenate adherence and method to check for conflicts"""
        return ((self.is_art, self.dose_number, self.total_doses), "%s-%s" % (self.adherence, self.method))
    
    
    def save(self):
        #override save as this is not a document but just a view
        pass
    
    def __unicode__(self):
        return "Dots Observation: %s on %s" % (self.observed_date, self.anchor_date) 
    
    def get_time_label(self):
        """
        returns an English time label out of
        'Dose', 'Morning', 'Noon', 'Evening', 'Bedtime'
        """
        return TIME_LABEL_LOOKUP[self.total_doses][self.dose_number]
    @classmethod
    def get_time_labels(cls, total_doses):
        return TIME_LABEL_LOOKUP[total_doses]
    
    class Meta:
        app_label = 'dotsview'
    
def _date_from_string(s):
    """
    >>> _date_from_string("18 Aug 2010 04:00:00 GMT")
    datetime.date(2010, 8, 18)
    """
    return datetime.date(*time.strptime(s, "%d %b %Y %H:%M:%S %Z")[:3])
    

from dotsview import signals