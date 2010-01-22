from django.db import models
from django.contrib.auth.models import User
import uuid
from casetracker.models import Case
from patient.models import Patient
from datetime import datetime
from django.utils.translation import ugettext_lazy as _

# Create your models here.

def make_uuid():
    return uuid.uuid1().hex

def make_time():
    return datetime.utcnow()


#make this a reversion counter
class BasePlan(models.Model):
    """Main Container for the care plan and is the actual instance that links
    back to a patient.
    
    A CarePlan is comprised of an owner (the user in question), and the sections it is filled with
    At the root, a care plan that is described as a template will not be linkable to a user.  If it needs to be linked
    to a user, then a brand new instance will be generated from it.
    """
    
    id = models.CharField(_('BasePlan Unique id'), max_length=32, unique=True, default=make_uuid, primary_key=True)
    
    version = models.PositiveIntegerField(default=1)
        
    title = models.CharField(max_length=160)
    plan_items = models.ManyToManyField("BasePlanItem") #make this a through?
    
    created_by = models.ForeignKey(User, blank=True, null=True, related_name='baseplan_created_by')
    created_date = models.DateTimeField(default=make_time)
    
    modified_by =  models.ForeignKey(User, blank=True, null=True, related_name='baseplan_modified_by')
    modified_date = models.DateTimeField(default=make_time)
    
    def __unicode__(self):
        return "[Plan Template] %s" % (self.title)


class PlanCategory(models.Model):
    """
    A plan category describes a plan section, whether it deals with medications, risks or other big buckets of information.
    """
    name = models.CharField(max_length=32)
    description = models.TextField()    
    #parent = models.ForeignKey('self', null=True, blank=True, related_name = 'plancategory_parent')
    
    def __unicode__(self):
        return "[Category] " + self.name


class PlanTag(models.Model):
    """
    A particular Plan Item probably has tag classification too with regard to related pieces of information.      
    """
    tag = models.SlugField()
    
    def __unicode__(self):
        return self.tag


class BasePlanItem(models.Model):
    """Substantive actionable items within a careplan.  ie, take medication directly.  """
    name = models.CharField(max_length=160)
    category = models.ManyToManyField(PlanCategory, related_name="baseplan_category", null=True, blank=True)    
    tags = models.ManyToManyField(PlanTag, blank=True, null=True)
    description = models.TextField()
    parent = models.ForeignKey('self', null=True, blank=True, related_name = 'child_base_plans')  
    
    
    def indent_name(self):
        indent = ''
        if self.parent == None:
            indent = ''
        else:
            prev = self.parent
            while prev != None:
                indent += "%s->" % (prev.name)
                prev=prev.parent
        indent += self.name
        return indent
                
            
    
    def __unicode__(self):
        return self.name  
    
    
class PlanRule(models.Model):
    """
    A Plan Rule is a container for custom code to operate upon a plan.
    The example for a plan rule would be scheduling recurring visits based on a certain condition,
    or scheduling visits for a pregnancy 2,4,6,8 months from the expected conception date.
    """
    name = models.CharField(max_length=160)
    description = models.TextField()
    module = models.CharField(max_length=255)
    method = models.CharField(max_length=128)


#section, specific instances of careplans.
class CarePlanCaseLink(models.Model):
    plan_item = models.ForeignKey("PlanItem")
    case = models.ForeignKey(Case)

class PlanItem(models.Model):
    
    #subclassing PlanItem makes it tricky with the foriegnkey parentage, so we're copying verbatim
    name = models.CharField(max_length=160)
    category = models.ManyToManyField(PlanCategory, related_name="planitem_category", null=True, blank=True)    
    tags = models.ManyToManyField(PlanTag, null=True, blank=True)
    description = models.TextField()
    parent = models.ForeignKey('self', null=True, blank=True, related_name = 'child_plans')    
    
    cases = models.ManyToManyField(Case, through="CarePlanCaseLink")
    from_template = models.ForeignKey(BasePlanItem, blank=True, null=True, 
                                      related_name='baseplan_inheritors')
    def __unicode__(self):
        return "[Template Item] " + self.name


    #@staticmethod
    @classmethod
    def create_from_template(base_item, parent_item=None):
        """
        Factory method to generate a new plan item from a template
        base_item is the BasePlanItem instance
        parent_item is a PlanItem instance parent if you're generating this programmatically
        save = do we save this to db before returning?
        """
        new_item = PlanItem()
        new_item.id = uuid.uuid1().hex
        new_item.category = base_item.category
        new_item.tags.add(base_item.tags.all())
        new_item.description = base_item.description        
        new_item.from_template = base_item
        if parent_item != None:
            new_item.parent = parent_item 

        new_item.save()
        
        if base_item.child_plans.all().count > 0:
            for child_item in base_item.child_plans.all():
                PlanItem.create_from_template(child_item, parent_item=base_item)        
        
        return new_item

class CarePlan(models.Model):
    id = models.CharField(_('CarePlan Unique id'), max_length=32, unique=True, default=make_uuid, primary_key=True)
    
    patient = models.ForeignKey(Patient)    
    from_template = models.ForeignKey(BasePlan, null=True, blank=True)    
        
    version = models.PositiveIntegerField(default=1)
        
    title = models.CharField(max_length=160)
    plan_items = models.ManyToManyField("PlanItem") #overide the base classes definition
    
    created_by = models.ForeignKey(User, blank=True, null=True, related_name='careplan_created_by')
    created_date = models.DateTimeField(default=make_time)
    
    modified_by =  models.ForeignKey(User, blank=True, null=True, related_name='careplan_modified_by')
    modified_date = models.DateTimeField(default=make_time)
    
    def __unicode__(self):
        return "[Care Plan] %s" % (self.title)
    
    @classmethod
    def create_from_template(base_plan, save=False, creator_user=None):
        """
        Generate a careplan from a BasePlan template
        """
        
        if save:
            if creator_user==None:
                raise Exception("Error, if you are saving this on creation from a template, you must enter a user")
        
        new_plan = CarePlan()
        new_plan.id = uuid.uuid1().hex
        new_plan.from_template = base_plan
        new_plan.version = 1
        
        new_plan.title = base_plan.title
        for base_item in base_plan.plan_items.all():            
            new_item= PlanItem.create_from_template(base_item, parent_item=None)            
            new_plan.plans.add(new_item)
        
        if creator_user:
            new_plan.created_by = creator_user
            new_plan.created_date = datetime.utcnow()
            
            new_plan.modified_by = creator_user
            new_plan.modified_date= datetime.utcnow()        
        
        if save:
            new_plan.save()
        return new_plan
    

    
