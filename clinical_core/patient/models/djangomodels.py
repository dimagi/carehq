from django.utils.translation import ugettext_lazy as _
from django.contrib.auth.models import User
from django.db import models
from datetime import datetime

import settings
import logging
from dimagi.utils import make_uuid, make_time
from patient.models.couchmodels import CPatient


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
        try:
            return CPatient.view('patient/ids', key=self.doc_id).first()
        except:
            return None

    @property
    def cases(self):
        return self.case_set.all()

    def _get_COUCHDATA(self, propertyname):
        """
        Return a generic top level property of a patient couch object.
        """
        if self.couchdoc != None:
            return self.couchdoc[propertyname]

    def _set_COUCHDATA(self, propertyname, setvalue):
        """
        Generic setter for top level property of a patient couch object
        """
        if self.couchdoc != None:
            doc = self.couchdoc
            doc[propertyname] = setvalue
            doc.save()


    def __unicode__(self):
        return self.full_name

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