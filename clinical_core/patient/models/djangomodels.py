from django.utils.translation import ugettext_lazy as _
from django.contrib.auth.models import User
from django.db import models
from datetime import datetime
import simplejson

import settings
import logging
from dimagi.utils import make_uuid, make_time
from django.core.cache import cache
from patient.models.couchmodels import CPatient
class DuplicateIdentifierException(Exception):
    pass



class Patient(models.Model):
    """ The patient object now is a stub to point to a couch model in couchmodels.py
    This object is retained to provide a Relational foreign key for traditional django models.

    Also, permissions via the Actor framework and other permission/integration/security features will link to this object rather.
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
                self._couchdoc = CPatient.view('patient/all', key=self.doc_id, include_docs=True).first()
                couchjson = simplejson.dumps(self._couchdoc.to_json())
                cache.set('%s_couchdoc' % (self.id), couchjson)
            except Exception, ex:
                self._couchdoc = None
        else:
            return self._couchdoc
            self._couchdoc = CPatient.wrap(simplejson.loads(couchjson))

        return self._couchdoc


#        if hasattr(self, '_couchdoc'):
#            return self._couchdoc
#        else:
#            try:
#                self._couchdoc =  CPatient.view('patient/all', key=self.doc_id, include_docs=True).first()
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
            self._couchdoc = CPatient()
            self._couchdoc.django_uuid = self.id #the id is set at init
            self.isnew = True
        else:
            self.isnew=False

    @staticmethod
    def is_pact_id_unique(pact_id):
        #print "checking pact_id: " + str(pact_id)
        if CPatient.view('patient/pact_ids', key=pact_id, include_docs=True).count() > 0:
            return False
        else:
            return True

    def save(self, *args, **kwargs):
        #time to do some error checking
        if not Patient.is_pact_id_unique(self.couchdoc.pact_id):
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

    def add_actor(self, actor):
        from actors.models.actors import PatientActorLink
        pal = PatientActorLink(patient=self, actor=actor, active=True)
        pal.save()

    def add_provider(self, actor):
        self.add_actor(actor)

    def add_caregiver(self, actor):
        self.add_actor(actor)

    def get_caregivers(self):
        """Returns a queryset of actors for this given patient whose role is a caregiver"""
        from actors.models.actors import PatientActorLink
        from actors.models.roles import Role
        all_actors = PatientActorLink.objects.filter(patient=self)
        cg_roles = Role.objects.CaregiverRoles()
        caregivers = all_actors.filter(actor__role__role_type__in=cg_roles)
        return caregivers

    def get_providers(self):
        """Returns a queryset of actors for this given patient whose role is a provider"""
        from actors.models.actors import PatientActorLink
        from actors.models.roles import Role
        all_actors = PatientActorLink.objects.filter(patient=self)
        prov_roles = Role.objects.ProviderRoles()

        providers = all_actors.filter(actor__role__role_type__in=prov_roles)
        return providers




from patient.models.signals import *