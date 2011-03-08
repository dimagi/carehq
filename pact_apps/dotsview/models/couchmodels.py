from django.db.models import *
from patient.models import Patient
from couchdbkit.ext.django.schema import *
import simplejson
from dimagi.utils import make_uuid
import time, datetime

# Create your models here.

ADHERENCE_CHOICES = (
    ("empty", "Empty"),
    ("partial", "Partial"),
    ("full", "Full"),
)
METHOD_CHOICES = (
    ("direct", "Direct"),
    ("pillbox", "Pillbox"),
    ("self", "Self"),
)
TIME_LABEL_LOOKUP = (
    (),
    ('Dose',),
    ('Morning', 'Evening'),
    ('Morning', 'Noon', 'Evening'),
    ('Morning', 'Noon', 'Evening', 'Bedtime'),
    ('Dose', 'Morning', 'Noon', 'Evening', 'Bedtime'),
)
TIME_LABELS = ('Dose', 'Morning', 'Noon', 'Evening', 'Bedtime')
MAX_LEN_DAY = len(TIME_LABELS)

ADDENDUM_NOTE_STRING = "[AddendumEntry]"
class CObservation(Document):
    doc_id = StringProperty()
    patient = StringProperty() #case id
    
    pact_id = StringProperty() #patient pact id
    provider = StringProperty()

    encounter_date = DateTimeProperty()
    anchor_date = DateTimeProperty()
    observed_date = DateTimeProperty()
    
    submitted_date = DateTimeProperty()
    created_date = DateTimeProperty()
    
    is_art = BooleanProperty()
    dose_number=IntegerProperty()
    total_doses = IntegerProperty()
    adherence=StringProperty()
    method=StringProperty()

    is_reconciliation = BooleanProperty(default=False)
    
    day_index = IntegerProperty()

    day_note = StringProperty() #if there's something for that particular day, then it'll be here
    note = StringProperty() #this is for the overall note for that submission, will exist on the anchor date



    @property
    def obs_score(self):
        """Gets the relative score of the observation.
        """
        if self.method == "direct":
            return 3
        if self.method == "pillbox":
            return 2
        if self.method == "self":
            return 1



    @property
    def adinfo(self):
        """helper function to concatenate adherence and method to check for conflicts"""
        return ((self.is_art, self.dose_number, self.total_doses), "%s" % (self.adherence))
    
    
#    def save(self):
#        #override save as this is not a document but just a view
#        pass

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

class CObservationAddendum(Document):
#    sub_id = StringProperty(default=make_uuid)
    observed_date = DateProperty()
    art_observations = SchemaListProperty(CObservation)
    nonart_observations = SchemaListProperty(CObservation)
    created_by = StringProperty()
    created_date = DateTimeProperty()
    notes = StringProperty() #placeholder if need be
    class Meta:
        app_label = 'dotsview'




def _date_from_string(s):
    """
    >>> _date_from_string("18 Aug 2010 04:00:00 GMT")
    datetime.date(2010, 8, 18)
    """
    return datetime.date(*time.strptime(s, "%d %b %Y %H:%M:%S %Z")[:3])
    

from dotsview import signals