from django.db import models
#from userprofile.models import BaseProfile
from django.contrib.auth.models import User
from django.utils.translation import ugettext_lazy as _
from django.db.models import Q
from casetracker.models import Case, Filter
import datetime

GENDER_CHOICES = ( ('F', _('Female')), ('M', _('Male')),)
# Create your models here.
#class AshandProfile(BaseProfile):
#    firstname = models.CharField(max_length=255, blank=True)
#    middlename = models.CharField(max_length=255, blank=True)
#    surname = models.CharField(max_length=255, blank=True)
#    gender = models.CharField(max_length=1, choices=GENDER_CHOICES, blank=True)
#    birthdate = models.DateField(default=datetime.date.today(), blank=True)    
#    about = models.TextField(blank=True)

#providers are individual entities set as "profiles" from the django user

class CaseProfile(models.Model):
    """Proof of concept case/filter view stuff for user profile
    This will need to be replaced by a more sophisticated tracking (for login and sessions)
    as well as user profile management
    """
    user = models.ForeignKey(User)
    last_filter = models.ForeignKey(Filter)
    last_login = models.DateTimeField()
    last_login_from = models.IPAddressField()
    
class ProviderRole(models.Model):
    """
    Define a particular providers' role for the given patient.  This is different from their actual title
    Though the actual roles may need to be made into their own model
    """
    ROLE_CHOICES = (
                      ('oncologist', 'Oncologist'),
                      ('pcp', 'Primary Care Physician'),
                      ('socialworker', 'Social Worker'),
                      ('other-doctor', 'Other Doctor'),
                      ('other-nurse', 'Other Nurse'),
                      ('nurse', 'Nurse'),
                      ('nurse-triage', 'Triage Nurse'),
                      ('lab', 'Laboratory'),
                      ('other', 'Other'),
                      )
    role = models.CharField(choices = ROLE_CHOICES, max_length=32)
    role_description = models.CharField(max_length=64, null=True, blank=True) 
    notes = models.CharField(max_length=512, null=True, blank=True)


class ProviderLink(models.Model):
    care_team = models.ForeignKey("CareTeam")
    provider = models.ForeignKey(User)
    role = models.ForeignKey("ProviderRole")
    notes = models.CharField(max_length=512, null=True, blank=True)
    
    def save(self):
        #todo:  do a lookup of the proposed provider
        #and use a lookup or security service of some type to validate that the said provider is 
        #who they are, and are able to actually be attached/saved in this way
        super(ProviderLink, self).save()
    
class CareRelationship(models.Model):
    """
    Define a particular caregivers' relationship for the given patient.  This is different from their actual title
    Though the actual roles may need to be made into their own model
    """
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
#    RELATIONSHIP_CHOICES = (
#        ('Family', (
#            ('vinyl', 'Vinyl'),
#            ('cd', 'CD'),
#            )
#            ),
#        ('Video', (
#                   ('vhs', 'VHS Tape'),
#                   ('dvd', 'DVD'),
#                   )
#            ),
#        ('unknown', 'Unknown'),
#    )
    
    relationship_type = models.CharField(choices=RELATIONSHIP_CHOICES,max_length=32)    
    other_description = models.CharField(max_length=64, null=True, blank=True) 
    notes = models.CharField(max_length=512, null=True, blank=True)
    
class CaregiverLink(models.Model):
    care_team = models.ForeignKey("CareTeam")
    caregiver = models.ForeignKey(User)
    relationship = models.ForeignKey(CareRelationship)
    notes = models.CharField(max_length=512, null=True, blank=True)
    
    
    
    def save(self):
        #todo:  do a lookup of the proposed caregiver
        #and use a lookup or security service of some type to validate that the said provider is 
        #who they are, and are able to actually be attached/saved in this way
        super(CaregiverLink, self).save()

class CareTeam(models.Model):
    """
    A care team revolves around a patient.  It will contain providers and caregivers with their linked roles
    on their linkage.
    
    Cases for this patient will be linked as well thorugh this model.
    """
    patient = models.ForeignKey(User, related_name='careteam_patient')
    providers = models.ManyToManyField(User, through='ProviderLink', related_name="provider_users")
    caregivers = models.ManyToManyField(User, through='CaregiverLink', related_name="caregiver_users")
    cases = models.ManyToManyField(Case)
    