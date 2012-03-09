from actorpermission.models.actortypes import CHWActor
#
#Remains to be seen if this should be xform'ed or django formed
#class TrainingLog(DocumentSchema):
#    training_attended = StringProperty()
#    training_date = DateTimeProperty()
#    notes = StringProperty()
#    entered_by = StringProperty() #actor doc_id
#
#
#class SupervisionLog(DocumentSchema):
#    pact_id = StringProperty() #pact_id of patient being supervised for
#    supervision_topics = ListProperty() # topics discussed
#    notes = StringProperty()
#
#    supervision_by = StringProperty()
#    supervision_date = DateTimeProperty() #actor doc_id
from couchdbkit.ext.django.schema import Document, DateTimeProperty, SchemaListProperty, IntegerProperty, StringProperty, DocumentSchema
from couchdbkit.schema.properties import DateProperty

class UserTally(DocumentSchema):
    username = StringProperty()
    submitted = IntegerProperty()
    scheduled = IntegerProperty()


class SubmissionTallyLog(Document):
    #report_type=StringProperty() #not needing to use this, just assume that once email is sent, then the report is successful
    report_date = DateProperty()
    created_time = DateTimeProperty()
    user_log = SchemaListProperty(UserTally)


from signals import *