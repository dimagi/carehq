#TODO:
#Put your couch related documents you want to link with your patient django models


from datetime import datetime
from couchdbkit.ext.django.schema import *
from couchdbkit.schema.properties_proxy import SchemaListProperty


class CCareHQPatient(Document):
    pass

class CDotSchedule(Document):
    day_of_week = StringProperty()
    hp_username = StringProperty()

class CPactPatient(Document):
#    first_name = StringProperty(required=True)
#    middle_name = StringProperty()
#    last_name = StringProperty(required=True)
#    birthdate = DateProperty()
#    birthdate_estimated = BooleanProperty()
#    gender = StringProperty(required=True)
#    patient_id = StringProperty()
#    clinic_ids = StringListProperty()
#    address = SchemaProperty(CAddress)
#    encounters = SchemaListProperty(Encounter)
#    phones = SchemaListProperty(CPhone)
#    cases = SchemaListProperty(PatientCase)
    dots_schedule = SchemaListProperty(CDotSchedule)
    #providers = SchemaListProperty(CProvider)
    art_regimen = StringProperty()
    non_art_regimen = StringProperty()





