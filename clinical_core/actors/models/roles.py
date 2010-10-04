from django.db import models
from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes import generic
from clinical_core.patient.models import Patient
from django.db.models import Q

from clincore.utils import make_uuid, make_time

class Role(models.Model):
    """
    A role is a base class for defining some type of affiliation/description of an individual in the system.
    A role by itself is actually quite meaningless in what data it contains.
    
    The instance of the role acts as a differentiator to aide in querying permissions.
    The data contained within the role instance itself *should be specific* to the role  you're creating for a given user.
    The role you define *will* be bound via the Actor object to the user you want to create an actor for.  Be specific!
    
    Roles 
    """
    id = models.CharField(max_length=32, unique=True, default=make_uuid, primary_key=True, editable=False)
    
    role_type = models.ForeignKey(ContentType, verbose_name='Role Subclass Content Type', blank=True, null=True)
    role_uuid = models.CharField('role_uuid', max_length=32, db_index=True, blank=True, null=True)
    role_object = generic.GenericForeignKey('role_type', 'role_uuid')    
    
    def save(self):
        #self.id = uuid.uuid1().hex
        self.role_type = self.child_contenttype()        
        self.role_uuid = self.id
        super(Role, self).save()

    
    @classmethod
    def child_contenttype(cls):
        ct = ContentType.objects.get(model=cls.__name__.lower())
        return ct
    
    def __unicode__(self):
        return "Role Base: %s: %s" % (self.role_type, self.role_object)    

class CHW(Role):
    title = models.CharField(max_length=64)
    specialty = models.CharField(max_length=64)
    
    def __unicode__(self):
        return "CHW: %s at %s" % (self.title, self.specialty)
    
class TriageNurse(Role):
    title = models.CharField(max_length=64)
    department= models.CharField(max_length=64)
    
    def __unicode__(self):
        return "TriageNurse: %s at %s" % (self.title, self.department)
    
class Doctor(Role):
    title = models.CharField(max_length=64)
    department = models.CharField(max_length=64)
    specialty = models.CharField(max_length=64)
    
    def __unicode__(self):
        return "Doctor: %s - %s at %s" % (self.title, self.specialty, self.department)
    
    
class Caregiver(Role):    
    RELATIONSHIP_CHOICES = (
                      ('guardian', 'Guardian'),
                      ('child', 'Child'),
                      ('parent', 'Parent'),
                      ('relative', 'Relative'),
                      ('spouse', 'Spouse'),
                      ('nextofkin', 'Next of kin'),
                      ('friend', 'Friend'),
                      ('neighbor', 'Neighbor'),
                      ('other', 'Other'),
    )
    relationship_type = models.CharField(choices=RELATIONSHIP_CHOICES,max_length=32)
    notes = models.CharField(max_length=512, null=True, blank=True)

    def __unicode__(self):
        return "Caregiver: %s" % (self.get_relationship_type_display())
