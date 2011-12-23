from couchdbkit.ext.django.schema import Document, DocumentSchema, ListProperty, StringProperty, DateTimeProperty, SchemaListProperty, DictProperty
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

