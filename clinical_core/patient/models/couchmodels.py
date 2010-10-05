#TODO:
from couchdbkit.ext.django.schema import *
from couchdbkit.schema.properties_proxy import SchemaListProperty


class CPhone(Document):
    is_default = BooleanProperty()
    description = StringProperty()
    number = StringProperty()
    created = DateTimeProperty()

    class Meta:
        app_label = 'patient'

class CAddress(Document):
    """
    An address.
    """
    description = StringProperty()
    street = StringProperty()
    city = StringProperty()
    state = StringProperty()
    postal_code = StringProperty()

    class Meta:
        app_label = 'patient'

class CDotSchedule(Document):
    day_of_week = StringProperty()
    hp_username = StringProperty()

    class Meta:
        app_label = 'patient'



class CPatient(Document):
    first_name = StringProperty(required=True)
    middle_name = StringProperty()
    last_name = StringProperty(required=True)
    gender = StringProperty(required=True)

    birthdate = DateProperty()

    patient_id = StringProperty()
    address = SchemaListProperty(CAddress)
    phones = SchemaListProperty(CPhone)
    #cases = SchemaListProperty(PatientCase)

    art_regimen = StringProperty()
    non_art_regimen = StringProperty()

    dots_schedule = SchemaListProperty(CDotSchedule)
#    providers = SchemaListProperty(CProvider) # providers in PACT are done via the careteam

    class Meta:
        app_label = 'patient'



