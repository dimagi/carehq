from django.utils.translation import ugettext_lazy as _
from django.contrib.auth.models import User
from django.db import models
from datetime import datetime

import settings
import logging
from clincore.utils import make_uuid, make_time
from patient.models.couchmodels import CPatient


class Patient(models.Model):
    """
    The patient object now is a stub to point to a couch model in couchmodels.py
    """

    id = models.CharField(_('Unique Patient uuid PK'), max_length=32, unique=True, default=make_uuid, primary_key=True, editable=False)
    doc_id = models.CharField(help_text="CouchDB Document _id", max_length=32, unique=True, editable=False, db_index=True, blank=True, null=True)

    class Meta:
        app_label = 'patient'


    @property
    def couchdoc(self):
        try:
            return CPatient.view('patient/ids', key=self.doc_id).first()
        except:
            return None

    def get_full_name(self):
        if self.couchdoc:
            return "%s %s" % (self.couchdoc.first_name, self.couchdoc.last_name)