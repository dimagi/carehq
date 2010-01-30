from django.db import models
#from userprofile.models import BaseProfile
from django.contrib.auth.models import User
from django.utils.translation import ugettext_lazy as _
from django.db.models import Q
from casetracker.models import Case, Filter
from patient.models import Patient
from provider.models import Provider
import datetime
import uuid

from djcaching.models import CachedModel
from djcaching.managers import CachingManager

def make_uuid():
    return uuid.uuid1().hex


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
    user = models.ForeignKey(User, unique=True)
    last_filter = models.ForeignKey(Filter, null=True)
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
    
    id = models.CharField(max_length=32, unique=True, default=make_uuid, primary_key=True, editable=False)
    role = models.CharField(choices = ROLE_CHOICES, max_length=32)
    role_description = models.CharField(max_length=64, null=True, blank=True) 
    notes = models.CharField(max_length=512, null=True, blank=True)

    def __unicode__(self):
        return "%s" % (self.role)



class ProviderLink(CachedModel):
#class ProviderLink(models.Model):
    """
    Simple link of a provider object to a careteam.
    """
    id = models.CharField(max_length=32, unique=True, default=make_uuid, primary_key=True, editable=False)
    
    objects = CachingManager()
    
    careteam = models.ForeignKey("CareTeam")
    provider = models.ForeignKey(Provider, related_name='providerlink_provider')
    
    role = models.ForeignKey("ProviderRole")
    notes = models.CharField(max_length=512, null=True, blank=True)
    
    def __unicode__(self):
        return "%s - %s" % (self.provider, self.role)
    
    @property
    def info(self):
        return Provider.objects.get(user=self.provider)
    
    def save(self):
        #todo:  do a lookup of the proposed provider
        #and use a lookup or security service of some type to validate that the said provider is 
        #who they are, and are able to actually be attached/saved in this way
        super(ProviderLink, self).save()
    
#class CareRelationship(models.Model):
class CareRelationship(CachedModel):
    """
    Define a particular caregivers' relationship for the given patient.  This is different from their actual title
    Though the actual roles may need to be made into their own model, as should permissions and such.
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
    objects = CachingManager()
    
    id = models.CharField(max_length=32, unique=True, default=make_uuid, primary_key=True, editable=False)
    relationship_type = models.CharField(choices=RELATIONSHIP_CHOICES,max_length=32)    
    other_description = models.CharField(max_length=64, null=True, blank=True) 
    notes = models.CharField(max_length=512, null=True, blank=True)
    
    def __unicode__(self):
        return self.get_relationship_type_display()
  
class CaregiverLink(CachedModel):
#class CaregiverLink(models.Model):
    """
    The actual link for a user object to be come a caregiver.
    """
    
    objects = CachingManager()
    
    id = models.CharField(max_length=32, unique=True, default=make_uuid, primary_key=True, editable=False)
    careteam = models.ForeignKey("CareTeam")
    user = models.ForeignKey(User, related_name="caregiverlink_user")
    relationship = models.ForeignKey(CareRelationship)
    notes = models.CharField(max_length=512, null=True, blank=True)    
    
    def save(self):
        #todo:  do a lookup of the proposed caregiver
        #and use a lookup or security service of some type to validate that the said provider is 
        #who they are, and are able to actually be attached/saved in this way
        super(CaregiverLink, self).save()

class CareTeamCaseLink(models.Model):
    """
    This is a through model to facilitate the querying of cases in a careteam.
    """
    id = models.CharField(max_length=32, unique=True, default=make_uuid, primary_key=True, editable=False)
    careteam = models.ForeignKey('CareTeam')
    case = models.ForeignKey(Case)

#class CareTeam(models.Model):
class CareTeam(CachedModel):
    """
    A care team revolves around a patient.  It will contain providers and caregivers with their linked roles
    on their linkage.
    
    Cases for this patient will be linked as well thorugh this model.
    """
    objects = CachingManager()
    
    id = models.CharField(max_length=32, unique=True, default=make_uuid, primary_key=True, editable=False)
    patient = models.ForeignKey(Patient, related_name='my_careteam')
    providers = models.ManyToManyField(Provider, through='ProviderLink', related_name="careteam_providers")
    caregivers = models.ManyToManyField(User, through='CaregiverLink', related_name="careteam_caregiver_users")
    cases = models.ManyToManyField(Case, through='CareTeamCaseLink')
    
    def add_case(self, case):
        CareTeamCaseLink(case=case, careteam=self).save()
        
    
    @property
    def primary_provider(self):
        """The primary provider for new cases going to this careteam for assignment"""
        #somewhat arbitrary notion here, but there should be a "gatekeeper" provider for new cases
        #in the future this probably should be defined by a more fully fleshed out in the ProviderRole/Link model
        
        if hasattr(self, '_primary_provider'):
            return self._primary_provider
        
        if self.providerlink_set.all().count() == 1:
            self._primary_provider = self.providerlink_set.all()[0].provider
        
        triage_nurse = self.providerlink_set.all().filter(role__role='nurse-triage')
        if len(triage_nurse) > 0:
            self._primary_provider = triage_nurse[0].provider
        
        pcp = self.providerlink_set.all().filter(role__role='pcp')
        if len(pcp) > 0:            
            self._primary_provider = pcp[0].provider
        else:
            self._primary_provider = None
        
        return self._primary_provider
    
    @property
    def provider_data(self):
        if not hasattr(self, '_provider_data'):
            self._provider_data = self.providerlink_set.select_related().all()
        else:
            return self._provider_data

    @property
    def caregiver_data(self):
        if not hasattr(self,'_caregiver_data'):
            self._caregiver_data = self.caregiverlink_set.all()
        return self._caregiver_data        
    
    def get_careteam_user_qset(self):
        """
        Really hackish way of getting a union of all the caregivers and providers in the careteam
        into one queryset
        """
        if not hasattr(self,'_careteam_qset'):
            caregiver_ids = self.caregivers.all().values_list('id',flat=True)
            q_caregivers = Q(id__in=caregiver_ids)
            
            provider_ids = self.providers.all().values_list('id',flat=True)
            q_providers = Q(id__in=provider_ids)
            
            self._careteam_qset = User.objects.filter(q_caregivers | q_providers).exclude(username='ashand-reflexive')
        return self._careteam_qset


    #Region, convenience functions for cases
    def resolved_cases(self):
        """
        Return a queryset of the cases in this careteam that are resolved
        """
        return self.cases.all().filter(status__state_class='resolve')
        
    
    def closed_cases(self):
        """
        Return a queryset of all closed cases for this careteam
        """
        return self.cases.all().filter(status__state_class='close')
    
    
    def all_cases(self):
        """
        return all cases for this careteam
        """
        return self.cases.all()
        
    
    def __unicode__(self):
        if not hasattr(self, '_stringname'):            
            self._stringname = "Careteam for %s" % self.patient.user.username
        return self._stringname
    