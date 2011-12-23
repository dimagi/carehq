import hashlib
import pdb
import simplejson
import uuid
from couchdbkit.ext.django.schema import Document
from couchdbkit.schema.properties import StringProperty, DateTimeProperty, BooleanProperty
from couchdbkit.schema.properties_proxy import  SchemaListProperty
import logging
from django.core.cache import cache
from clinical_shared.mixins import TypedSubclassMixin
from permissions.models import Actor
from tenant.models import TenantActor


class BaseActorDocument(Document, TypedSubclassMixin):
    """
    When creating an Actor django model, a corresponding ActorProfileDocument is created for it.
    """
    actor_uuid = StringProperty() # the django_uuid of the Actor model in the db.
    base_type = StringProperty(default="BaseActorDocument")
    name = StringProperty() #the actor name

    last_name = StringProperty()
    first_name = StringProperty()
    title = StringProperty()

    notes = StringProperty()

    _subclass_dict = {}

    def get_name(self):
        return "%s %s" % (self.first_name, self.last_name)

    def get_display(self):
        pass

    @classmethod
    def _get_my_type(cls):
        return cls

    def _deprecate_data(self):
        self.doc_type = "Deleted%s" % (self._get_my_type().__name__)
        self.base_type = "DeletedBaseActorDocument"
        super(BaseActorDocument, self).save()

    def get_hash(self):
        return hashlib.sha1(simplejson.dumps(self.to_json())).hexdigest()

    @property
    def django_actor(self):
        if not hasattr(self, '_django_actor'):
            try:
                dja = Actor.objects.get(id=self.actor_uuid)
            except Actor.DoesNotExist:
                dja = None
            self._django_actor = dja
        return self._django_actor

    def save(self, tenant, user=None, *args, **kwargs):
        if self.actor_uuid is None:
        #this is a new instance
        #first check global uniqueness
        #            if not self.is_unique():
        #                raise DuplicateIdentifierException()
            django_actor = Actor()
            actor_uuid = uuid.uuid4().hex
            #doc_id = uuid.uuid4().hex
            if self._id == None and self.new_document:
                doc_id = uuid.uuid4().hex
                self._id = doc_id
            else:
                doc_id = self._id

            self.actor_uuid = actor_uuid
            django_actor.id = actor_uuid
            django_actor.doc_id=doc_id

            django_actor.name = '%s.%s.%s_%s.%s' % (tenant.prefix, self.__class__.__name__, self.last_name, self.first_name, self.get_hash()[0:10])
            if user:
                django_actor.user = user

            try:
                django_actor.save()
                ta = TenantActor(actor=django_actor, tenant=tenant)
                ta.save()
                super(BaseActorDocument, self).save(*args, **kwargs)
                self._django_actor = django_actor
            except Exception, ex:
                logging.error("Error creating actor: %s" % ex)
                raise ex
        else:
            #it's not new
            super(BaseActorDocument, self).save(*args, **kwargs)

        #Invalidate the cache entry of this instance
        cache.delete('%s_actordoc' % self._id)
        try:
            couchjson = simplejson.dumps(self.to_json())
            cache.set('%s_actordoc' % self._id, couchjson)
        except Exception, ex:
            logging.error("Error serializing actor document object for cache (%s): %s" % (self._id, ex))


    class Meta:
        app_label = 'actorpermission'


class DeviceDocument(Document):
    device_id = StringProperty()
    active_date = DateTimeProperty()
    modified_date = DateTimeProperty()
    is_active = BooleanProperty()
    is_suspended = BooleanProperty(default=False)
    class Meta:
        app_label = 'actorpermission'


class CHWActor(BaseActorDocument):
    """
    Basic profile information on a CHW
    """
    phone_number = StringProperty()
    device_list = SchemaListProperty(DeviceDocument)

    class Meta:
        app_label = 'actorpermission'

    def casexml_registration_block(self, user_profile):
        user = user_profile.user
        pass


class CaregiverActor(BaseActorDocument):
    """
    Basic profile information on a PACT CHW
    """

    RELATIONSHIP_CHOICES = (
        ('guardian', 'Guardian'),
        ('child', 'Child'),
        ('parent', 'Parent'),
        ('relative', 'Relative'),
        #('spouse', 'Spouse'),
        ('sibling', 'Sibling'),
        ('nextofkin', 'Next of kin'),
        ('friend', 'Friend'),
        ('neighbor', 'Neighbor'),
        ('other', 'Other'),
        )

    phone_number = StringProperty()
    address = StringProperty()
    relation = StringProperty(choices=RELATIONSHIP_CHOICES)

    class Meta:
        app_label = 'actorpermission'

    def get_name(self):
        return "%s (%s)" % (self.name, self.relation)

    def get_display(self):
        return self.relation

class PatientActor(BaseActorDocument):
    patient_doc_id = StringProperty()
    pass

class ProviderActor(BaseActorDocument):
    """
    Health Provider identification.
    A bulk of the actors in the system will likely be instances of this model.
    """
    provider_title = StringProperty()
    phone_number = StringProperty()
    email = StringProperty()

    facility_name = StringProperty()
    facility_address = StringProperty()

    affiliation = StringProperty()
    class Meta:
        app_label = 'actorpermission'

    def get_name(self):
        return "%s %s (%s)" % (self.first_name, self.last_name, self.provider_title)

    def get_display(self):
        return "%s, %s" % (self.title, self.facility_name)



