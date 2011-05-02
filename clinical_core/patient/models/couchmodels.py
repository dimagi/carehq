#TODO:
import logging
from couchdbkit.schema.properties import IntegerProperty, DictProperty, DictProperty
from couchdbkit.schema.properties_proxy import SchemaListProperty, SchemaProperty
from datetime import datetime
from datetime import timedelta
import simplejson
from dimagi.utils import make_uuid
from couchdbkit.ext.django.schema import StringProperty, BooleanProperty, DateTimeProperty, Document, DateProperty
from dimagi.utils.couch.database import get_db
from dimagi.utils.make_time import make_time
from django.core.cache import cache


class CPhone(Document):
    phone_id=StringProperty(default=make_uuid)
    is_default = BooleanProperty()
    description = StringProperty()
    number = StringProperty()
    created = DateTimeProperty(default=datetime.utcnow)

    deprecated = BooleanProperty(default=False)
    started = DateTimeProperty(default=datetime.utcnow, required=True)
    ended = DateTimeProperty()
    created_by = StringProperty() #userid
    edited_by = StringProperty() #useridp
    notes = StringProperty()

    class Meta:
        app_label = 'patient'

class CAddress(Document):
    """
    An address.
    """
    description = StringProperty() #the title so to speak
    address_id = StringProperty(default=make_uuid)
    street = StringProperty()
    city = StringProperty()
    state = StringProperty()
    postal_code = StringProperty()

    deprecated = BooleanProperty(default=False)

    started = DateTimeProperty(default=make_time, required=True)
    ended = DateTimeProperty()

    created_by = StringProperty() #userid
    edited_by = StringProperty() #userid


    class Meta:
        app_label = 'patient'




class BasePatient(Document):
    """
    Base class for case-able patient model in CareHQ.  Actual implementations of CareHQ ought to subclass this for its own uses. Especially in cases of multi tenancy, or code reuse.
    """
    GENDER_CHOICES = (
        ('m','Male'),
        ('f','Female'),
        ('u','Undefined'),
    )

    django_uuid = StringProperty() #the django uuid of the patient object
    case_id = StringProperty() # the case_id generated for this patient object.  This is in situations where case == patient, but in reality cases can be other things.
    first_name = StringProperty(required=True)
    middle_name = StringProperty()
    last_name = StringProperty(required=True)
    gender = StringProperty(required=True)
    birthdate = DateProperty()
    patient_id = StringProperty()
    address = SchemaListProperty(CAddress)
    phones = SchemaListProperty(CPhone)
    date_modified = DateTimeProperty(default=datetime.utcnow)
    notes = StringProperty()

    base_type = StringProperty(default="BasePatient")

    class Meta:
        app_label = 'patient'


class CSimpleComment(Document):
    doc_fk_id = StringProperty() #is there a fk in couchdbkit
    deprecated = BooleanProperty(default=False)
    comment = StringProperty()
    created_by = StringProperty()
    created = DateTimeProperty(default=datetime.utcnow)
    class Meta:
        app_label = 'patient'