import uuid
from couchdbkit.ext.django.schema import Document
from couchdbkit.schema.properties import StringProperty, BooleanProperty, DateTimeProperty, DateProperty
from couchdbkit.schema.properties_proxy import SchemaListProperty
from django.utils.translation import ugettext_lazy as _
from django.contrib.auth.models import User
from django.db import models
from datetime import datetime
import simplejson
from dimagi.utils.couch.database import get_db

import settings
import logging
from dimagi.utils import make_uuid, make_time
from django.core.cache import cache


class DuplicateIdentifierException(Exception):
    pass
class PatientCreationException(Exception):
    """Exception on initial creation of a Patient object"""
    pass

class PatientIntegrityException(Exception):
    """Data integrity exception on a patient being recalled from the database"""
    pass


#preload all subclasses of BasePatient into a dictionary for easy access for casting documents to their instance class




class Patient(models.Model):
    """ The patient object now is a stub to point to a couch model in couchmodels.py
    This object is retained to provide a Relational foreign key for traditional django models.

    Also, permissions via the Actor framework and other permission/integration/security features will link to this object rather.

    All differentiations of roles and patient types for this should be determined by the underlying couchmodel.  This model is just a placeholder for the
    actors permission framework which uses the django orm.
    """
    id = models.CharField(_('Unique Patient uuid PK'), max_length=32, unique=True,  primary_key=True, editable=False)
    doc_id = models.CharField(help_text="CouchDB Document _id", max_length=32, unique=True, editable=False, db_index=True, blank=True, null=True)
    user = models.ForeignKey(User, blank=True, null=True) #note it's note unique, possibly that they could be multi enrolled, so multiple notions of patient should exist


    class Meta:
        app_label = 'patient'

    @property
    def couchdoc(self):
        #next, do a memcached lookup
        if hasattr(self, '_couchdoc') and self._couchdoc != None:
            return self._couchdoc

        couchjson = cache.get('%s_couchdoc' % (self.id), None)
        if couchjson == None:
            try:
                self._couchdoc = BasePatient.get_typed_from_id(self.doc_id)
                couchjson = simplejson.dumps(self._couchdoc.to_json())
                cache.set('%s_couchdoc' % (self.id), couchjson)
            except Exception, ex:
                self._couchdoc = None
        else:
            self._couchdoc = BasePatient.get_typed_from_dict(simplejson.loads(couchjson))

#        if self._couchdoc == None:
#            raise PatientIntegrityException("Error, unable to instantiate the patient document object")
        return self._couchdoc

    def _get_COUCHDATA(self, propertyname):
        """
        Return a generic top level property of a patient couch object.
        """
        if self.couchdoc != None:
            return self.couchdoc[propertyname]

    def _set_COUCHDATA(self, propertyname, setvalue, do_save=False):
        """
        Generic setter for top level property of a patient couch object.  By default does not save unless you override.
        """
        if self.couchdoc != None:
            doc = self.couchdoc
            doc[propertyname] = setvalue
            if do_save:
                doc.save()

    def save(self, django_uuid=None, doc_id=None, *args, **kwargs):
        """
        Saving of Patient django objects directly is discouraged.  This usually will only be in the case where you are creating a new Patient.
        This should be done from the BasePatient subclass, where it will automatically generate this object.
        """
        if self.id == None or self.id == '':
            isnew = True
            if doc_id == None:
                raise PatientCreationException("In order to create a new Patient django model, you must provide a patient couch document id.")
            if django_uuid == None:
                raise PatientCreationException("In order to create a new Patient django model, you must provide a patient django model id as well.")

            #sanity check to ensure that this doc_id isn't counted elsewhere
            if self.__class__.objects.filter(doc_id=doc_id).count() != 0:
                raise PatientCreationException("Error saving patient, the doc_id %s already exists in the patient database." % (doc_id))

            self.id = django_uuid
            self.doc_id = doc_id
        else:
            #nothing to see here, just save it like a normal django model.
            pass
        super(Patient, self).save(*args, **kwargs)


    def __unicode__(self):
        if self.couchdoc:
            return self.full_name
        else:
            return "Unlinked Patient [%s]" % (self.id)

    @property
    def full_name(self):
        if self.couchdoc:
            return "%s %s" % (self.couchdoc.first_name, self.couchdoc.last_name)

    def grant_care_access(self, actor):
        pass
#todo: replace these accessors with functions from the django-permissions framework
#    def add_role(self, role):
#        from actors.models.roles import CareTeamMember
#        pal = CareTeamMember(patient=self, role=role, active=True)
#        pal.save()
#
#    def add_provider(self, role):
#        self.add_role(role)
#
#    def add_caregiver(self, role):
#        self.add_role(role)
#
#    def get_caregivers(self):
#        """Returns a queryset of actors for this given patient whose role is a caregiver"""
#        from actors.models.roles import Actor, CareTeamMember
#        all_roles = CareTeamMember.objects.filter(patient=self)
#        cg_roles = Actor.objects.CaregiverRoles()
#        caregivers = all_roles.filter(role__role_type__in=cg_roles)
#        return caregivers
#
#    def get_caregivers(self):
#        """Returns a queryset of actors for this given patient whose role is a caregiver"""
#        from actors.models.roles import Actor, CareTeamMember
#        all_roles = CareTeamMember.objects.filter(patient=self)
#        pr_roles = Actor.objects.ProviderRoles()
#        providers = all_roles.filter(role__role_type__in=pr_roles)
#        return providers


#class MergedPatient(models.Model):
#    """
#    For multi tenancy, or multi context patients, we will merge them via django
#    """
#    id = models.CharField(_('Unique Patient uuid PK'), max_length=32, unique=True, default=make_uuid, primary_key=True, editable=False)
#    patients = models.ManyToManyField(Patient)
#



class CPhone(Document):
    phone_id=StringProperty(default=make_uuid)
    is_default = BooleanProperty()
    description = StringProperty()
    number = StringProperty()
    created = DateTimeProperty(default=datetime.utcnow)

    deprecated = BooleanProperty(default=False)
    started = DateTimeProperty(default=datetime.utcnow, required=True)
    ended = DateTimeProperty()
    created_by = StringProperty() #userid
    edited_by = StringProperty() #useridp
    notes = StringProperty()

    class Meta:
        app_label = 'patient'

class CAddress(Document):
    """
    An address.
    """
    description = StringProperty() #the title so to speak
    address_id = StringProperty(default=make_uuid)
    street = StringProperty()
    city = StringProperty()
    state = StringProperty()
    postal_code = StringProperty()

    deprecated = BooleanProperty(default=False)

    started = DateTimeProperty(default=make_time, required=True)
    ended = DateTimeProperty()

    created_by = StringProperty() #userid
    edited_by = StringProperty() #userid


    class Meta:
        app_label = 'patient'




class BasePatient(Document):
    """
    Base class for case-able patient model in CareHQ.  Actual implementations of CareHQ ought to subclass this for its own uses. Especially in cases of multi tenancy, or code reuse.
    """
    GENDER_CHOICES = (
        ('m','Male'),
        ('f','Female'),
        ('u','Undefined'),
    )

    django_uuid = StringProperty() #the django uuid of the patient object
    case_id = StringProperty() # the case_id generated for this patient object.  This is in situations where case == patient, but in reality cases can be other things.
    first_name = StringProperty(required=True)
    middle_name = StringProperty()
    last_name = StringProperty(required=True)
    gender = StringProperty(required=True)
    birthdate = DateProperty()
    patient_id = StringProperty() #particular identifiers will likley be defined in the subclass. - this is a placeholder for nothing actually used.
    address = SchemaListProperty(CAddress)
    phones = SchemaListProperty(CPhone)
    date_modified = DateTimeProperty(default=datetime.utcnow)
    notes = StringProperty()

    base_type = StringProperty(default="BasePatient")


    _subclass_dict = {}
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
            cast_class = BasePatient
            logging.error("Warning, unable to retrieve and cast the stored doc_type of the patient model.")
        return cast_class.wrap(doc_dict)

    @classmethod
    def get_typed_from_id(cls, doc_id):
        """
        Using the doc's stored doc_type, cast the retrieved document to the requisite couch model
        """
        #todo this is hacky in a multitenant environment
        db = get_db()
        doc_dict = db.open_doc(doc_id)
        return cls.get_typed_from_dict(doc_dict)


    def is_unique(self):
        raise NotImplementedError("Error, subclass for patient document type must have a uniqueness check for its own instance.  %s" % (self.__class__()))

    @classmethod
    def _get_my_type(cls):
        return cls

    def __init__(self, *args, **kwargs):
        super(BasePatient, self).__init__(*args, **kwargs)

    def delete(self):
        """
        Overriding delete for a patient, by setting base_type and doc_type to DeletedFOO
        Do not delete in the patient context, only deprecate.
        """
#        self.doc_type = "Deleted%s" % (self._get_my_type())
#        self.base_type = "DeletedBasePatient"
#        self.save()
        django_model = Patient.objects.get(id=self.django_uuid)
        django_model.delete()




    def save(self):
        if self.django_uuid == None:
            #this is a new instance
            #first check global uniqueness
            if not self.is_unique():
                raise DuplicateIdentifierException()

            djangopt = Patient()
            django_uuid = uuid.uuid1().hex
            doc_id = uuid.uuid1().hex
            self.django_uuid = django_uuid
            self._id = doc_id
            try:
                djangopt.save(django_uuid=django_uuid, doc_id=doc_id)
                super(BasePatient, self).save()
            except PatientCreationException, ex:
                logging.error("Error creating patient: %s" % ex)
                raise ex
        else:
            #it's not new
            super(BasePatient, self).save()
        #Invalidate the cache entry of this instance
        cache.delete('%s_couchdoc' % (self.django_uuid))
        try:
            couchjson = simplejson.dumps(self.to_json())
            cache.set('%s_couchdoc' % (self.django_uuid), couchjson)
        except Exception, ex:
            logging.error("Error serializing patient document object for cache (%s): %s" % (self._id, ex))


    class Meta:
        app_label = 'patient'


class CSimpleComment(Document):
    doc_fk_id = StringProperty() #is there a fk in couchdbkit
    deprecated = BooleanProperty(default=False)
    comment = StringProperty()
    created_by = StringProperty()
    created = DateTimeProperty(default=datetime.utcnow)
    class Meta:
        app_label = 'patient'

from .signals import *