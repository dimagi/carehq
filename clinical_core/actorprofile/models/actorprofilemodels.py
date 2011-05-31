from couchdbkit.ext.django.schema import Document
from couchdbkit.schema.properties import StringProperty, DateTimeProperty, DictProperty
from couchdbkit.schema.properties_proxy import SchemaDictProperty
from django.contrib.auth.models import User
from datetime import datetime
from django.db import models
from dimagi.utils import make_uuid


class BaseActorProfileDocument(Document):
    actor_id = StringProperty() # the key to access the dict
    base_type = StringProperty(default="BaseActorProfileDocument")
    name = StringProperty() #the actor name

    class Meta:
        app_label='actorprofile'


class ProfileDocument(Document):
    profile_id = StringProperty() #the model id of the linked profile object
    last_edit = DateTimeProperty(default=datetime.utcnow)

    actors = SchemaDictProperty(BaseActorProfileDocument) #keyed by actor_id, the django uuid of the actor object.

    class Meta:
        app_label='actorprofile'


class ClinicalUserProfile(models.Model):
    """
    Django auth.user profile linking to the user.  you must set the UserProfile document to use this.
    This is just a passthrough model that links a user profile to a couchdb document that provides more useful metadata.
    """
    id = models.CharField(max_length=32, unique=True, default=make_uuid, primary_key=True, editable=False)
    user = models.ForeignKey(User, unique=True)
    profile_doc_id = models.CharField(help_text="CouchDB Document _id", max_length=32, unique=True, editable=False, db_index=True, blank=True, null=True)

    class Meta:
        app_label='actorprofile'


    @property
    def profiles(self):
        if self.couchdoc == None:
            return "No profile document"
        else:
            return self.couchdoc.actors

    def get_profiledoc(self, profile_key):
        if not self.couchdoc:
            return None

        pass

    @property
    def couchdoc(self):
        if self._couchdoc == None:
            couchdoc = ProfileDocument.view('actors/all_profiles', key=self.profile_doc_id, include_docs=True).first()
            if couchdoc != None:
                self._couchdoc = couchdoc
        return self._couchdoc

    def __unicode__(self):
        return "UserProfile: %s" % (self.user.username)



