from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.contrib.auth.models import User
from tracking.models import Visitor
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes import generic
from clincore.utils import make_uuid, make_time


class DeepTracking(models.Model):
    """
    A persistent session store for the access logging system for your site. 
    """    
    visitor = models.ForeignKey(Visitor)

class AuditEvent(models.Model):    
    id = models.CharField(_('Access guid'), max_length=32, unique=True, default=make_uuid, primary_key=True) #primary_key override?
    object_type = models.ForeignKey(ContentType, verbose_name='Case linking content type', blank=True, null=True)
    object_uuid = models.CharField('object_uuid', max_length=32, db_index=True, blank=True, null=True)
    content_object = generic.GenericForeignKey('object_type', 'object_uuid')
    
    user = models.ForeignKey(User)
    accessed = models.DateTimeField(default=make_time)
    
class FieldAccess(models.Model):
    object_type = models.ForeignKey(ContentType, verbose_name='Case linking content type', blank=True, null=True)
    field = models.CharField(max_length=64, blank=True, null=True)
    
    class Meta:
        unique_together = ('object_type', 'field')    

class ModelAccessLog(models.Model):    
    id = models.CharField(_('Access guid'), max_length=32, unique=True, default=make_uuid, primary_key=True) #primary_key override?
    
    object_type = models.ForeignKey(ContentType, verbose_name='Case linking content type', blank=True, null=True)
    object_uuid = models.CharField('object_uuid', max_length=32, db_index=True, blank=True, null=True)
    content_object = generic.GenericForeignKey('object_type', 'object_uuid')
    
    properties = models.ManyToManyField(FieldAccess, blank=True, null=True)
    property_data = models.TextField() #json of the actual fields accessed
    
    user = models.ForeignKey(User)
    accessed = models.DateTimeField(default = make_time)


