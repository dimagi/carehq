from django.db import models

from django.utils.translation import ugettext_lazy as _
import uuid
from django.contrib.auth.models import User

from djcaching.models import CachedModel
from djcaching.managers import CachingManager


#class Provider(models.Model):
class Provider(CachedModel):
    """
    In this current iteration, the provider is *really* dumb and simple.
    """
    user = models.ForeignKey(User, blank=True, null=True) #note, you can be multiple providers for a given user.
    uuid = models.CharField(_('Unique provider guid'), 
                                        max_length=32, unique=True, editable=False)

    first_name = models.CharField(_("Provider first name"), max_length=64)
    middle_name = models.CharField(_("Provider middle name"),max_length=64, blank=True, null=True)
    last_name = models.CharField(_("Provider last name"),max_length=64, db_index=True)
    
    #lame example fields
    job_title = models.CharField(max_length=64)
    affiliation = models.CharField(max_length=64)
    
    objects = CachingManager()
    
    def __unicode__(self):
        return "%s %s" % (self.first_name, self.last_name)
    
    
    def save(self):
        if self.id == None:
            self.uuid = uuid.uuid1().hex
        super(Provider, self).save()
