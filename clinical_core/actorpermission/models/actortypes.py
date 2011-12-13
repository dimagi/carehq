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

    last_name = StringProperty()
    first_name = StringProperty()
    title = StringProperty()

    notes = StringProperty()

    _subclass_dict = {}

    def get_name(self):
        return "%s %s" % (self.first_name, self.last_name)

    def get_display(self):
        return self.name

    @classmethod
    def _get_my_type(cls):
        return cls

    def _deprecate_data(self):
        self.doc_type = "Deleted%s" % (self._get_my_type().__name__)
        self.base_type = "DeletedBaseActorDocument"
        super(BaseActorDocument, self).save()

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

            django_actor.name = '%s-%s-%s' % (tenant.prefix, self.__class__.__name__, self.name)

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
        cache.delete('%s_actordoc' % (self._id))
        try:
            couchjson = simplejson.dumps(self.to_json())
            cache.set('%s_actordoc' % (self._id), couchjson)
        except Exception, ex:
            logging.error("Error serializing actor document object for cache (%s): %s" % (self._id, ex))

    @classmethod
    def _get_subclass_dict(cls):
        if len(cls._subclass_dict.keys()) == 0:
            for c in cls.__subclasses__():
                cls._subclass_dict[unicode(c.__name__)] = c
        return cls._subclass_dict

    @classmethod
    def get_typed_from_dict(cls, doc_dict):
        doc_type = doc_dict['doc_type']
        if cls._get_subclass_dict().has_key(doc_type):
            cast_class = cls._get_subclass_dict()[doc_type]
        else:
            cast_class = BaseActorDocument
            logging.error("Warning, unable to retrieve and cast the stored doc_type of the actor document model.")
        return cast_class.wrap(doc_dict)

    @classmethod
    def get_typed_from_id(cls, doc_id):
        """
        Using the doc's stored doc_type, cast the retrieved document to the requisite couch model
        """
        #todo this is hacky in a multitenant environment
        db = cls.get_db()
        doc_dict = db.open_doc(doc_id)
        return cls.get_typed_from_dict(doc_dict)

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
    Basic profile information on a PACT CHW
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

    class Meta:
        app_label = 'actorpermission'

    def get_name(self):
        return "%s (%s)" % (self.name, self.relation)

    def get_display(self):
        return self.relation

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



