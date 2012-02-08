import pdb
import uuid
from couchdbkit.ext.django.schema import Document, TimeProperty, IntegerProperty
from couchdbkit.schema.properties import StringProperty, BooleanProperty, DateTimeProperty, DateProperty, StringListProperty
from couchdbkit.schema.properties_proxy import SchemaListProperty
from django.core.urlresolvers import reverse
from django.utils.timesince import timesince
from django.utils.translation import ugettext_lazy as _
from django.contrib.auth.models import User
from django.db import models
from datetime import datetime, time
import simplejson
import math
from clinical_shared.mixins import TypedSubclassMixin
from permissions.models import Actor

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


class PatientActorLink(models.Model):
    """
    Intermediary model to link django Patient stub to the Actor model
    """
    patient = models.OneToOneField("Patient", related_name='get_actor')
    actor = models.OneToOneField(Actor, related_name='get_patient')

    class Meta:
        app_label='patient'


class Patient(models.Model):
    """ The patient object now is a stub to point to a couch model in couchmodels.py
    This object is retained to provide a Relational foreign key for traditional django models.

    Also, permissions via the Actor framework and other permission/integration/security features will link to this object rather.

    All differentiations of roles and patient types for this should be determined by the underlying couchmodel.  This model is just a placeholder for the
    actors permission framework which uses the django orm.
    """
    id = models.CharField(_('Unique Patient uuid PK'), max_length=32, unique=True,  primary_key=True, editable=False)
    doc_id = models.CharField(help_text="CouchDB Document _id", max_length=32, unique=True, editable=False, db_index=True, blank=True, null=True)
    #user = models.ForeignKey(User, blank=True, null=True) #note it's note unique, possibly that they could be multi enrolled, so multiple notions of patient should exist - should be removed in favor of the actor FK


    def get_absolute_url(self):
        if self.couchdoc is not None:
            return self.couchdoc.get_absolute_url()
        else:
            return '#'

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
                try:
                    cache.set('%s_couchdoc' % (self.id), couchjson)
                except:
                    logging.error("Error, caching framework unavailable")
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

    def delete(self, *args, **kwargs):
        """
        Delete is handled by a signal to check the couchdoc's deletion/deprecation as well
        """
        super(Patient, self).delete(*args, **kwargs)

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
    phone_id= IntegerProperty()
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
    address_id = IntegerProperty()
    street = StringProperty()
    city = StringProperty()
    state = StringProperty()
    postal_code = StringProperty()

    full_address = StringProperty() #this is a combined address and will be used in replacement of the individual components

    deprecated = BooleanProperty(default=False)

    started = DateTimeProperty(default=make_time, required=True)
    ended = DateTimeProperty()

    created_by = StringProperty() #userid
    edited_by = StringProperty() #userid

    def get_full_address(self):
        return "%s %s, %s %s" % (self.street, self.city, self.state, self.postal_code)


    class Meta:
        app_label = 'patient'




class BasePatient(Document, TypedSubclassMixin):
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
    poly_types = StringListProperty() #if the document is assumed as multiple patient types (by multi tenancy), store the different types here.  it's left up to the tenant's querying method to retreive the document.




    @property
    def django_patient(self):
        if not hasattr(self, '_django_patient'):
            try:
                djpt = Patient.objects.get(id=self.django_uuid)
            except Actor.DoesNotExist:
                djpt = None
            self._django_patient = djpt
        return self._django_patient

    @property
    def age_string(self):
        """
        Return the age in only one maximal unit (since the timesince template tag adds a secondary unit)
        """
        tsince_string = timesince(datetime.combine(self.birthdate, time(0)))
        return tsince_string.split(',')[0]

    @property
    def age_int(self):
        """
        Return the age in only as an int
        """
        td = datetime.utcnow() - datetime.combine(self.birthdate, time(0))
        return int(round(td.days/365.25))

    def is_unique(self):
        raise NotImplementedError("Error, subclass for patient document type must have a uniqueness check for its own instance.  %s" % (self.__class__()))

    @classmethod
    def _get_my_type(cls):
        return cls

    def __init__(self, *args, **kwargs):
        super(BasePatient, self).__init__(*args, **kwargs)


    def _deprecate_data(self):
        self.doc_type = "Deleted%s" % (self._get_my_type().__name__)
        self.base_type = "DeletedBasePatient"
        self.save()

    def delete(self):
        """
        Overriding delete for a patient, by setting base_type and doc_type to DeletedFOO
        Do not delete in the patient context, only deprecate.
        """
        self._deprecate_data()
        django_model = Patient.objects.get(id=self.django_uuid)
        django_model.delete()




    def save(self, *args, **kwargs):
        user = kwargs.get('user', None)
        if self.poly_types == None:
            self.poly_types = []

        if self.__class__.__name__ not in self.poly_types:
            self.poly_types.append(self.__class__.__name__)


        if self.django_uuid == None:
            #this is a new instance
            #first check global uniqueness
            if not self.is_unique():
                raise DuplicateIdentifierException()

            djangopt = Patient()
            django_uuid = uuid.uuid4().hex
            doc_id = uuid.uuid4().hex
            if self._id == None and self.new_document:
                doc_id = uuid.uuid4().hex
                self._id = doc_id
            else:
                doc_id = self._id
            self.django_uuid = django_uuid
            try:
                super(BasePatient, self).save(*args, **kwargs)
                djangopt.save(django_uuid=django_uuid, doc_id=doc_id)
            except PatientCreationException, ex:
                logging.error("Error creating patient: %s" % ex)
                raise ex
        else:
            #it's not new
            super(BasePatient, self).save(*args, **kwargs)


        #Invalidate the cache entry of this instance
        cache.delete('%s_couchdoc' % (self.django_uuid))
        try:
            couchjson = simplejson.dumps(self.to_json())
            cache.set('%s_couchdoc' % (self.django_uuid), couchjson)
        except Exception, ex:
            logging.error("Error serializing patient document object for cache (%s): %s" % (self._id, ex))


    class Meta:
        app_label = 'patient'


class CarehqPatient(BasePatient):
    """
    A stub implementation of the Patient model
    """

    study_id = StringProperty() # readable sequential string of patient enrollment number

    start_date = DateProperty(verbose_name='Date of trial start')
    device_id = StringProperty()
    checkin_time = TimeProperty(verbose_name='Preferred survey time')

    enrolled_date = DateProperty()
    hcms_registered_date = DateProperty()

    install_date = DateProperty()
    sim_number = StringProperty() # sim card for 3g access for phone number - for refill purposes


    #time window in which avalaible
    available_start = TimeProperty(verbose_name='Start time available for contact')
    available_end = TimeProperty(verbose_name='End time available for contact')

    def is_unique(self):
        return True

    def get_absolute_url(self):
        url= reverse('patient_url', kwargs={'patient_guid': self._id, 'view_mode': ''})
        return url

    def __getattr__(self, key):
        # this hack allows this to be used in templates that expect it
        # to behave like a normal python object.
        try:
            return super(BasePatient, self).__getattr__(key)
        except KeyError:
            raise AttributeError

class CSimpleComment(Document):
    doc_fk_id = StringProperty() #is there a fk in couchdbkit
    deprecated = BooleanProperty(default=False)
    comment = StringProperty()
    created_by = StringProperty()
    created = DateTimeProperty(default=datetime.utcnow)
    class Meta:
        app_label = 'patient'

from .signals import *