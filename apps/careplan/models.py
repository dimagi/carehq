from django.db import models
from django.contrib.auth.models import User
import uuid

# Create your models here.

def make_uuid():
    return uuid.uuid1().hex


class CarePlan(models.Model):
    """Main Container for the care plan and is the actual instance that links
    back to a patient.
    
    A CarePlan is comprised of an owner (the user in question), and the sections it is filled with
    At the root, a care plan that is described as a template will not be linkable to a user.  If it needs to be linked
    to a user, then a brand new instance will be generated from it.
    """
    
    id = models.CharField(_('CarePlan Unique id'), max_length=32, unique=True, default=make_uuid, primary_key=True)
    title = models.CharField(max_length=160, required=True)
    plans = models.ManyToManyField("PlanSection")
    owner = models.ForeignKey(User, blank=True, null=True)
    is_template = models.BooleanField(default=False)
    
    from_template = models.ForeignKey("self") #limit_choices_to is_template=True
    


class PlanCategory(models.Model):
    """
    A plan category describes a plan section, whether it deals with medications, risks or other big buckets of information.
    """
    name = models.CharField(max_length=32, required=True)
    description = models.TextField()    
    parent = models.ForeignKey('self', null=True, blank=True, related_name = 'plancategory_parent')
    
    

class PlanTag(models.Model):
    """
    A particular Plan Item probably has tag classification too with regard to related pieces of information.      
    """
    tag = models.SlugField()

class PlanItem(models.Model):
    """Substantive actionable items within a careplan.  ie, take medication directly.  """
            
    name = models.CharField(max_length=160)    
    tags = models.ManyToManyField(PlanTag)
    description = models.TextField()    


class PlanSection(models.Model):
    """
    A container with classification of a plan, comprised of multiple items.
    """        
    name = models.CharField(max_length=160)
    category = models.ManyToManyField(PlanCategory, related_name="plansection_category")    
    items = models.ManyToManyField(PlanItem)    
    parent = models.ForeignKey('self', null=True, blank=True, related_name = 'planitem_parent')
