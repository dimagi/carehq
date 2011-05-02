from datetime import datetime
from couchdbkit.ext.django.schema import Document
from couchdbkit.schema.properties import StringProperty, DateTimeProperty
from django.contrib.auth.models import User
from django.db import models
from dimagi.utils import make_uuid

import settings
import logging


class ActorConfigurationException(Exception):
    def __init__(self, value):
        self.value = value
    def __str__(self):
        return repr(self.value)

if not hasattr(settings, "AUTH_PROFILE_MODULE"):
    logging.error("You do not have AUTH_PROFILE_MODULE settings variable setup, the actors permission framework is inoperable, exiting")
    raise ActorConfigurationException("No settings configuration for auth profile.")

if not hasattr(settings, "ACTOR_PROFILE_DOCUMENT_CLASS"):
    logging.warning("You do not have a custom ACTOR_PROFILE_DOCUMENT_CLASS set in your settings, defaulting to the default generic profile setting.")







class BaseProfileDocument(Document):
    base_type = StringProperty(default="ProfileDocument") #for subclassing this needs to stay consistent
    profile_id = StringProperty() #the model id of the linked profile object
    last_edit = DateTimeProperty(default=datetime.utcnow)

    class Meta:
        app_label='actors'

class ClinicalUserProfile(models.Model):
    """
    Django auth.user profile linking to the user.  you must set the UserProfile document to use this.
    This is just a passthrough model that links a user profile to a couchdb document that provides more useful metadata.
    """
    id = models.CharField(max_length=32, unique=True, default=make_uuid, primary_key=True, editable=False)
    user = models.ForeignKey(User, unique=True)
    profile_doc_id = models.CharField(help_text="CouchDB Document _id", max_length=32, unique=True, editable=False, db_index=True, blank=True, null=True)

    class Meta:
        app_label='actors'

    @property
    def couchdoc(self):
        if self._couchdoc == None:
            self._couchdoc = BaseProfileDocument.view('actors/all_profiles', key=self.profile_doc_id, include_docs=True).first()
        return self._couchdoc

    def __unicode__(self):
        return "UserProfile: %s" % (self.user.username)
