from actorprofile.models.actorprofilemodels import BaseActorProfileDocument
import uuid
from couchdbkit.ext.django.schema import Document
from couchdbkit.schema.properties import StringProperty, DateTimeProperty, BooleanProperty
from couchdbkit.schema.properties_proxy import SchemaListProperty



class PactDevice(Document):
    device_id = StringProperty()
    active_date = DateTimeProperty()
    modified_date = DateTimeProperty()
    is_active = BooleanProperty()
    is_suspended = BooleanProperty(default=False)

class PactCHWProfileDocument(BaseActorProfileDocument):
    """
    Basic profile information on a PACT CHW
    """
    phone_number = StringProperty()
    device_list = SchemaListProperty(PactDevice)

    def casexml_registration_block(self, user_profile):
        user = user_profile.user

        pass


class PactExternalProvider(BaseActorProfileDocument):
    """External Provider identification"""

    title = StringProperty()
    affiliation = StringProperty()
    facility_address = StringProperty()
    phone_number = StringProperty()

    pass