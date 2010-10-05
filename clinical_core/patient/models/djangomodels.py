from django.utils.translation import ugettext_lazy as _
from django.contrib.auth.models import User
from django.db import models
from datetime import datetime

import settings
import logging
from clincore.utils import make_uuid, make_time


if hasattr(settings, "PATIENT_DOCUMENT_MODEL"):
    #import said document model and make sure it works
    pass
else:
    logging.warning("You have not set a PATIENT_DOCUMENT_MODEL, using default django patient model only.")

# Create your models here.

class IdentifierType(models.Model):
    """
    Placeholder for differing identifiers that may be attached to a patient
    """    
    id = models.CharField(_('Identifier Type Unique id'), max_length=32, unique=True, default=make_uuid, primary_key=True, editable=False)
    description = models.CharField(max_length=64, unique=True) #should be globally unique
    shortname = models.CharField(max_length=32)
    
    regex = models.CharField(max_length=128, blank=True, null=True)


    class Meta:
        app_label = 'patient'
        verbose_name = "Identifier Type"
        verbose_name_plural = "Identifier Types"
        ordering = ['description']

    def save(self):
        super(IdentifierType, self).save()

class Address(models.Model):
    """
    US address django model object for basic addresses within a relational database using traditional django models.
    """
    id = models.CharField(_('Identifier Instance Unique id'), max_length=32, unique=True, default=make_uuid, primary_key=True, editable=False)
    type = models.CharField(max_length=24, blank=True, null=True)
    street1 = models.CharField(max_length=160, blank=True, null=True)
    street2 = models.CharField(max_length=160, blank=True, null=True)
    city = models.CharField(max_length=128, blank=True, null=True)
    state = models.CharField(max_length=16, blank=True, null=True)
    postal_code = models.CharField(max_length=12, blank=True, null=True)

    class Meta:
        app_label = 'patient'
        verbose_name = "Address"
        verbose_name_plural = "Addresses"
        ordering = ['type', 'city', 'state', 'street1', 'street2']

class PatientIdentifier(models.Model):
    """
    The patient identifier is the actual instance of an identifier linked to a patient.
    """
    id = models.CharField(_('Identifier Instance Unique id'), max_length=32, unique=True, default=make_uuid, primary_key=True, editable=False)
    id_type = models.ForeignKey("IdentifierType")
    id_value = models.CharField(max_length=128)
    
    class Meta:
        app_label = 'patient'
        verbose_name = "Patient Identifier"
        verbose_name_plural = "Patient Identifiers"
        ordering = ['id_type', 'id_value']
        unique_together = ('id_type','id_value')

    
    #todo:  put an update procedure that points all the patient instances to the actual root patient
    def save(self):
        super(PatientIdentifier, self).save()


class Patient(models.Model):
    """
    The patient object here is a django patient to help satisfy the majority of basic patient identity in a medical application context.
    
    If you wish to expand the complexity of the usage of your patient, extend your patient object with the couch_document property to refer to a couch document
    if you so wish to augment the patient data.
    """
    
    GENDER_CHOICES = (
        ('m', 'Male'),
        ('f', 'Female'),
        )
    
    id = models.CharField(_('Unique Patient uuid PK'), max_length=32, unique=True, default=make_uuid, primary_key=True, editable=False)
    first_name = models.CharField(max_length=64)
    middle_name = models.CharField(max_length=64, null=True, blank=True)
    last_name = models.CharField(max_length=64)
    
    user = models.ForeignKey(User, related_name='patient_user', null=True, unique=True, blank=True)
    
    identifiers = models.ManyToManyField(PatientIdentifier)
    address = models.ManyToManyField(Address)    
    
    dob = models.DateField(_("Date of birth"), null=True, blank=True, db_index=True)
    sex = models.CharField(_("Sex"), choices=GENDER_CHOICES, max_length=1)
    
    is_primary = models.BooleanField(_("Is this patient the primary, merged"), default=True)
    root_patient = models.ForeignKey("self", null=True, blank=True)
    
    added_date = models.DateTimeField(default=make_time)    
    notes = models.TextField()    
    couch_document = models.CharField(max_length=32, unique=True, db_index=True, blank=True, null=True)

    #objects = PatientManager()
    class Meta:
        app_label = 'patient'
        verbose_name = "Patient"
        verbose_name_plural = "Patients"
        ordering = ['last_name', 'first_name', 'dob']
    
    @property
    def document(self):
        """
        return the document instance
        """
        pass
    
    @property
    def age(self):
        if not hasattr(self, '_age'):
            td = datetime.utcnow().date() - self.dob
            self._age = int(td.days/365.2425)
        return self._age        
    
    def __unicode__(self):
        if self.user:
            return "[WebPatient] %s %s" % (self.user.first_name, self.user.last_name)
        else:
            return "[NoWebPatient] %s"  % self.id
    
    def save(self):
        super(Patient, self).save()
    
    def get_root_patient(self):
        if self.is_primary:
            return self
        else:
            if self.root_patient == None:
                raise Exception ("Error, this patient is designated as not a primary, but the root pointer is null")
            return self.root_patient
        
    def get_all_equivalents(self):
        return Patient.objects.filter(root_patient=self)
    
