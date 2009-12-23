from django.db import models
from django.utils.translation import ugettext_lazy as _
import uuid
from django.contrib.auth.models import User
from djcaching.models import CachedModel
from djcaching.managers import CachingManager


# Create your models here.

#class IdentifierType(models.Model):
class IdentifierType(CachedModel):
    """
    Placeholder for differing identifiers that may be attached to a patient
    """    
    description = models.CharField(max_length=64)
    shortname = models.CharField(max_length=32)
    uuid = models.CharField(_('Id Type Guid'), 
                                        max_length=32, unique=True, editable=False)

    regex = models.CharField(max_length=128, blank=True, null=True)
    objects = CachingManager()
    def save(self):
        if self.id == None:
            self.uuid = uuid.uuid1().hex
        super(IdentifierType, self).save()

class PatientIdentifier(models.Model):
    id_type = models.ForeignKey("IdentifierType")
    patient = models.ForeignKey("Patient")
    
    id_value = models.CharField(max_length=128)
    
    uuid = models.CharField(_('ID instance Guid'), 
                                        max_length=32, unique=True, editable=False)

    
    #link_date = models.DateTimeField()
    #link_by = models.ForeignKey(User)
    #origin = models.CharField(max_length=160) #not sure if this linkage is where we want to put it vs an actual case

    #todo:  put an update procedure that points all the patient instances to the actual root patient
    def save(self):
        if self.id == None:
            self.uuid = uuid.uuid1().hex
        super(PatientIdentifier, self).save()


#class Patient(models.Model):    
class Patient(CachedModel):
    
    GENDER_CHOICES = (
        ('m', 'Male'),
        ('f', 'Female'),
        )
    
    
    user = models.OneToOneField(User, related_name='patient_user')
    uuid = models.CharField(_('Unique patient guid'), 
                                        max_length=32, editable=False, unique=True)

    identifiers = models.ManyToManyField(IdentifierType, through=PatientIdentifier)
    
    first_name = models.CharField(_("Patient first name"), max_length=64)
    middle_name = models.CharField(_("Patient middle name"),max_length=64)
    last_name = models.CharField(_("Patient last name"),max_length=64, db_index=True)
    dob = models.DateField(_("Date of birth"), null=True, blank=True)
    sex = models.CharField(_("Sex"), choices=GENDER_CHOICES, max_length=1)
    
    is_primary = models.BooleanField(_("Is this patient the primary, merged"), default=True)
    root_patient = models.ForeignKey("self", null=True, blank=True)
    
    objects = CachingManager()
    
    def save(self):
        if self.id == None:
            self.uuid = uuid.uuid1().hex
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
    
