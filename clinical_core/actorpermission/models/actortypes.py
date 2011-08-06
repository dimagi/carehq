import simplejson
import uuid
from couchdbkit.ext.django.schema import Document
from couchdbkit.schema.properties import StringProperty, DateTimeProperty, BooleanProperty
from couchdbkit.schema.properties_proxy import  SchemaListProperty
import logging
from django.core.cache import cache
from permissions.models import Actor
from tenant.models import TenantActor


class BaseActorDocument(Document):
    """
    When creating an Actor django model, a corresponding ActorProfileDocument is created for it.
    """
    actor_uuid = StringProperty() # the django_uuid of the Actor model in the db.
    base_type = StringProperty(default="BaseActorDocument")
    name = StringProperty() #the actor name

    notes = StringProperty()


    @property
    def django_actor(self):
        if not hasattr(self, '_django_actor'):
            try:
                dja = Actor.objects.get(id=self.actor_uuid)
            except Actor.DoesNotExist:
                dja = None
            self._django_actor = dja
        return self._django_actor


    def save(self, tenant, *args, **kwargs):
        if self.actor_uuid == None:
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

            django_actor.name = '%s-%s-%s' % (tenant.prefix, self.__class__.__name__, self.name)

            try:
                super(BaseActorDocument, self).save(*args, **kwargs)
                django_actor.save()
                ta = TenantActor(actor=django_actor, tenant=tenant)
                ta.save()
                self._django_actor = django_actor

            except Exception, ex:
                logging.error("Error creating actor: %s" % ex)
                raise ex
        else:
            #it's not new
            super(BaseActorDocument, self).save(*args, **kwargs)


        #Invalidate the cache entry of this instance
        cache.delete('%s_actordoc' % (self._id))
        try:
            couchjson = simplejson.dumps(self.to_json())
            cache.set('%s_actordoc' % (self._id), couchjson)
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


class CHWActor(BaseActorDocument):
    """
    Basic profile information on a PACT CHW
    """
    phone_number = StringProperty()
    device_list = SchemaListProperty(DeviceDocument)

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
        ('spouse', 'Spouse'),
        ('sibling', 'Sibling'),
        ('nextofkin', 'Next of kin'),
        ('friend', 'Friend'),
        ('neighbor', 'Neighbor'),
        ('other', 'Other'),
        )

    phone_number = StringProperty()
    address = StringProperty()
    relation = StringProperty(choices=RELATIONSHIP_CHOICES)

class ProviderActor(BaseActorDocument):
    """
    Health Provider identification.
    A bulk of the actors in the system will likely be instances of this model.
    """
    title = StringProperty()
    phone_number = StringProperty()
    email = StringProperty()

    facility_name = StringProperty()
    facility_address = StringProperty()

    affiliation = StringProperty()



