from django.utils.translation import ugettext_lazy as _
from django.contrib.auth.models import User
from django.db import models
from datetime import datetime
import simplejson
from dimagi.utils.couch.database import get_db
from patient.models.couchmodels import BasePatient

import settings
import logging
from dimagi.utils import make_uuid, make_time
from django.core.cache import cache


class DuplicateIdentifierException(Exception):
    pass

#preload all subclasses of BasePatient into a dictionary for easy access for casting documents to their instance class

base_subclass_dict = {}
def get_subclass_dict():
    if len(base_subclass_dict.keys()) == 0:
        for cls in BasePatient.__subclasses__():
            base_subclass_dict[unicode(cls.__name__)] = cls
    return base_subclass_dict


def _get_typed_patient_from_dict(doc_dict):
    doc_type = doc_dict['doc_type']
    if get_subclass_dict().has_key(doc_type):
        cast_class = get_subclass_dict()[doc_type]
    else:
        cast_class = BasePatient
        logging.warning("Warning, unable to retrieve and cast the stored doc_type of the patient model.")
    return cast_class.wrap(doc_dict)

def _get_typed_patient(doc_id):
    """
    Using the doc's stored doc_type, cast the retrieved document to the requisite couch model
    """
    #todo this is hacky in a multitenant environment
    db = get_db()
    doc_dict = db.open_doc(doc_id)
    return _get_typed_patient_from_dict(doc_dict)


class Patient(models.Model):
    """ The patient object now is a stub to point to a couch model in couchmodels.py
    This object is retained to provide a Relational foreign key for traditional django models.

    Also, permissions via the Actor framework and other permission/integration/security features will link to this object rather.

    All differentiations of roles and patient types for this should be determined by the underlying couchmodel.  This model is just a placeholder for the
    actors permission framework which uses the django orm.
    """
    id = models.CharField(_('Unique Patient uuid PK'), max_length=32, unique=True, default=make_uuid, primary_key=True, editable=False)
    doc_id = models.CharField(help_text="CouchDB Document _id", max_length=32, unique=True, editable=False, db_index=True, blank=True, null=True)
    user = models.ForeignKey(User, blank=True, null=True) #note it's note unique, possibly that they could be multi enrolled, so multiple notions of patient should exist

    class Meta:
        app_label = 'patient'

    @property
    def couchdoc(self):
        #next, do a memcached lookup
        if self.isnew:
            return self._couchdoc

        couchjson = cache.get('%s_couchdoc' % (self.id), None)
        #couchjson = None
        if couchjson == None:
            try:
                self._couchdoc = _get_typed_patient(self.doc_id)
                couchjson = simplejson.dumps(self._couchdoc.to_json())
                cache.set('%s_couchdoc' % (self.id), couchjson)
            except Exception, ex:
                self._couchdoc = None
        else:
            return self._couchdoc
            #self._couchdoc = _get_typed_patient_from_dict(simplejson.loads(couchjson))

        if self._couchdoc == None:
            print "Error, this is None: %s->%s" % (self.id, self.doc_id)
        return self._couchdoc


#        if hasattr(self, '_couchdoc'):
#            return self._couchdoc
#        else:
#            try:
#                self._couchdoc =  BasePatient.view('patient/all', key=self.doc_id, include_docs=True).first()
#            except:
#                self._couchdoc = None
#            return self._couchdoc

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

    def __init__(self, *args, **kwargs):
        super(Patient, self).__init__(*args, **kwargs)
        if self.doc_id == None:
            self._couchdoc = BasePatient()
            self._couchdoc.django_uuid = self.id #the id is set at init
            self.isnew = True
        else:
            self.isnew=False

    def save(self, *args, **kwargs):
        #time to do some error checking
        if self.isnew:
            if not BasePatient.is_pact_id_unique(self.couchdoc.pact_id):
                raise DuplicateIdentifierException()

        if self.doc_id == None and self.isnew:
            self._couchdoc.save()
            self.doc_id = self._couchdoc._id


        super(Patient, self).save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        super(Patient, self).delete(*args, **kwargs)

    def __unicode__(self):
        if self.couchdoc:
            return self.full_name
        else:
            return "Patient [%s]" % (self.id)

    @property
    def full_name(self):
        if self.couchdoc:
            return "%s %s" % (self.couchdoc.first_name, self.couchdoc.last_name)

    def grant_care_access(self, actor):
        pass

    def add_role(self, role):
        from actors.models.roles import PatientLink
        pal = PatientLink(patient=self, role=role, active=True)
        pal.save()

    def add_provider(self, role):
        self.add_role(role)

    def add_caregiver(self, role):
        self.add_role(role)

    def get_caregivers(self):
        """Returns a queryset of actors for this given patient whose role is a caregiver"""
        from actors.models.roles import Role, PatientLink
        all_roles = PatientLink.objects.filter(patient=self)
        cg_roles = Role.objects.CaregiverRoles()
        caregivers = all_roles.filter(role__role_type__in=cg_roles)
        return caregivers

    def get_caregivers(self):
        """Returns a queryset of actors for this given patient whose role is a caregiver"""
        from actors.models.roles import Role, PatientLink
        all_roles = PatientLink.objects.filter(patient=self)
        pr_roles = Role.objects.ProviderRoles()
        providers = all_roles.filter(role__role_type__in=pr_roles)
        return providers


class MergedPatient(models.Model):
    """
    For multi tenancy, or multi context patients, we will merge them via django
    """
    id = models.CharField(_('Unique Patient uuid PK'), max_length=32, unique=True, default=make_uuid, primary_key=True, editable=False)
    patients = models.ManyToManyField(Patient)



from patient.models.signals import *