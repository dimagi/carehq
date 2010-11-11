#from couchdbkit.ext.django.schema import Document
#from couchdbkit.schema.properties import *
#from datetime import datetime
#from casetracker.models.casecore import Case
#
#class CaseDocument(Document):
#    case_uuid = StringProperty() #the django uuid of the patient object
#    source = StringProperty()
#    date_submitted = DateTimeProperty(default=datetime.utcnow)
#    class Meta:
#        app_label = 'casetracker'
#
#
#class CaseDocumentLink(models.Model):
#    doc_id = models.CharField(db_index=True, max_length=32)
#    case = models.ForeignKey(Case)
#    date_submitted = models.DateTimeField()
#    reason = models.CharField(max_length=64)