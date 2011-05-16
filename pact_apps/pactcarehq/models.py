from django.db import models
from couchdbkit.ext.django.schema import *
from couchdbkit.schema.properties_proxy import SchemaListProperty
from datetime import datetime
from pactpatient.models import PactPatient


class trial1mapping(models.Model):
    last_name = models.CharField(max_length=64, db_index=True)
    first_name = models.CharField(max_length=64, db_index=True)
    old_uuid = models.CharField(max_length=32, db_index=True, help_text="old case_id hash")
    old_id = models.PositiveIntegerField(help_text = "old user.id")
    pact_id = models.PositiveIntegerField(help_text = 'old pact_id')

    def __unicode__(self):
        print "Trial1Patient: %s, %s" % (str(self.last_name), str(self.first_name))


    def get_new_patient_doc_id(self):
        pts = PactPatient.view('patient/name_search_id', key=self.last_name.lower() + "_" + self.first_name.lower(), include_docs=True).all()
        for pt in pts:
            pact_id = str(pt.pact_id)
            new_id = pt._id
            if cmp(pact_id, str(self.pact_id)) == 0:
                return new_id
            else:
                print "non matching pact ids: |%s| != |%s|" % (self.pact_id, pact_id)
        return None



    