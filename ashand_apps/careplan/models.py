from django.db import models
from django.contrib.auth.models import User
from issuetracker.models import Case
from patient.models import Patient
from datetime import datetime
from django.utils.translation import ugettext_lazy as _
from django.core.urlresolvers import reverse


# Create your models here.
from dimagi.utils import make_uuid, make_time

class PlanCategory(models.Model):
    """
    A plan category describes a plan section, whether it deals with medications, risks or other big buckets of information.
    """
    name = models.CharField(max_length=32)
    description = models.TextField()    
    #parent = models.ForeignKey('self', null=True, blank=True, related_name = 'plancategory_parent')
    
    def __unicode__(self):
        return "[Category] " + self.name
    
    class Meta:
        verbose_name = "Plan Category"
        verbose_name_plural = "Plan Categories"
        ordering = ['name']

class PlanTag(models.Model):
    """
    A particular Plan Item probably has tag classification too with regard to related pieces of information.      
    """
    tag = models.SlugField()
    
    def __unicode__(self):
        return self.tag
    
    class Meta:
        verbose_name = "Plan Tag Metadata"
        verbose_name_plural = "Plan Tags"


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
    
    class Meta:
        verbose_name = "Plan Rule"
        verbose_name_plural = "Plan Rules"
        ordering = ['name',]

class TemplateCarePlanItemLink(models.Model):
    plan = models.ForeignKey("TemplateCarePlan")
    item = models.ForeignKey("TemplateCarePlanItem")
    order = models.PositiveIntegerField()
    class Meta:
        ordering  =['order',]
    
class CarePlanItemLink(models.Model):
    plan = models.ForeignKey("CarePlan")
    item = models.ForeignKey("CarePlanItem")
    order = models.PositiveIntegerField()
    
    class Meta:
        ordering  =['order',]


#make this a reversion counter
class TemplateCarePlan(models.Model):
    """Main Container for the care plan and is the actual instance that links
    back to a patient.
    
    A CarePlan is comprised of an owner (the user in question), and the sections it is filled with
    At the root, a care plan that is described as a template will not be linkable to a user.  If it needs to be linked
    to a user, then a brand new instance will be generated from it.
    """
    
    id = models.CharField(max_length=32, unique=True, default=make_uuid, primary_key=True, editable=False)
    
    version = models.PositiveIntegerField(default=1)
        
    title = models.CharField(max_length=160)
    plan_items = models.ManyToManyField("TemplateCarePlanItem", through=TemplateCarePlanItemLink) #make this a through?
    
    created_by = models.ForeignKey(User, blank=True, null=True, related_name='templatecareplan_created_by')
    created_date = models.DateTimeField(default=make_time)
    
    modified_by =  models.ForeignKey(User, blank=True, null=True, related_name='templatecareplan_modified_by')
    modified_date = models.DateTimeField(default=make_time)
    
    
    def get_absolute_url(self):
        return reverse('careplan.views.caretemplates.single_careplan', kwargs={"plan_id":self.id})
    
    def __unicode__(self):
        return "[Plan Template] %s" % (self.title)
    
    class Meta:
        verbose_name = "Template Care Plan"
        verbose_name_plural = "Template Care Plans"
        ordering = ['title','created_date']



class TemplateCarePlanItem(models.Model):
    """Substantive actionable items within a careplan.  ie, take medication directly.  """
    id = models.CharField(max_length=32, unique=True, default=make_uuid, primary_key=True, editable=False)
    name = models.CharField(max_length=160)
    category = models.ManyToManyField(PlanCategory, related_name="templatecareplanitem_category", null=True, blank=True)    
    tags = models.ManyToManyField(PlanTag, blank=True, null=True)
    description = models.TextField()
    parent = models.ForeignKey('self', null=True, blank=True, related_name = 'child_template_items')  
    
    @property
    def children(self):
        if not hasattr(self, '_children'):
            self._children = self.child_template_items.all()
        return self._children
    
    def get_absolute_url(self):
        return reverse('careplan.views.caretemplates.single_careplan_item', kwargs={"item_id":self.id})
    
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
    
    class Meta:
        verbose_name = "Template Care Plan Item"
        verbose_name_plural = "Template Care Plan Items"
        ordering = ['name']
    
    

#section, specific instances of careplans.
class CarePlanCaseLink(models.Model):
    careplan_item = models.ForeignKey("CarePlanItem")
    case = models.ForeignKey(Case)
    

class CarePlanItem(models.Model):
    CAREPLAN_ITEM_STATES = (
                            ('new', 'New'),
                            ('active', 'Active'),                            
                            ('closed-completed','Completed'),
                            ('closed-resolved', 'Resolved'),
                            ('closed-cancelled', 'Cancelled'),
                            ('removed', 'Removed'),
                            )
    
    #subclassing PlanItem makes it tricky with the foriegnkey parentage, so we're copying verbatim
    id = models.CharField(max_length=32, unique=True, default=make_uuid, primary_key=True)
    name = models.CharField(max_length=160)
    category = models.ManyToManyField(PlanCategory, related_name="careplanitem_category", null=True, blank=True)    
    tags = models.ManyToManyField(PlanTag, null=True, blank=True)
    description = models.TextField()
    parent = models.ForeignKey('self', null=True, blank=True, related_name = 'child_plans')    
    
    cases = models.ManyToManyField(Case, through="CarePlanCaseLink")
    from_template = models.ForeignKey(TemplateCarePlanItem, blank=True, null=True, 
                                      related_name='template_inheritors')
    
    state = models.CharField(choices=CAREPLAN_ITEM_STATES, max_length=16)

    def get_absolute_url(self):
        return reverse('careplan.views.planinstances.view_careplan_item', kwargs={"item_id":self.id})

    def __unicode__(self):
        return "[Template Item] " + self.name
    
    class Meta:
        verbose_name = "Care Plan Instance Item"
        verbose_name_plural = "Care Plan Instance Items"
        ordering = ['name']
    
    @property
    def children(self):
        if not hasattr(self, '_children'):
            self._children = self.child_plans.all()
        return self._children


    @staticmethod
    def create_from_template(base_item, parent_item=None):
        """
        Factory method to generate a new plan item from a template
        base_item is the TemplateCarePlanItem instance
        parent_item is a PlanItem instance parent if you're generating this programmatically
        save = do we save this to db before returning?
        """
        new_item = CarePlanItem()
        new_item.id = uuid.uuid4().hex
        new_item.category.add(*list(base_item.category.all()))
        new_item.tags.add(*list(base_item.tags.all()))
        new_item.description = base_item.description        
        new_item.from_template = base_item
        if parent_item != None:
            new_item.parent = parent_item 

        new_item.save()
        
        if base_item.children.count > 0:
            for child_item in base_item.children:
                CarePlanItem.create_from_template(child_item, parent_item=new_item)        
        
        return new_item

class CarePlan(models.Model):
    id = models.CharField(_('CarePlan Unique id'), max_length=32, unique=True, default=make_uuid, primary_key=True)
    
    patient = models.ForeignKey(Patient)    
    from_template = models.ForeignKey(TemplateCarePlan, null=True, blank=True)    
        
    version = models.PositiveIntegerField(default=1)
        
    title = models.CharField(max_length=160)
    plan_items = models.ManyToManyField("CarePlanItem", through=CarePlanItemLink) #overide the base classes definition
    
    created_by = models.ForeignKey(User, blank=True, null=True, related_name='careplan_created_by')
    created_date = models.DateTimeField(default=make_time)
    
    modified_by =  models.ForeignKey(User, blank=True, null=True, related_name='careplan_modified_by')
    modified_date = models.DateTimeField(default=make_time)
    
    
    def get_absolute_url(self):
        return reverse('careplan.views.planinstances.single_careplan', kwargs={"plan_id":self.id})
    
    def __unicode__(self):
        return "[Care Plan] %s" % (self.title)
    
    class Meta:
        verbose_name = "Care Plan Instance"
        verbose_name_plural = "Care Plan Instances"
        ordering = ['title','modified_date']
    
    @staticmethod
    def create_from_template(base_plan, patient, title=None, save_data=False, creator_user=None):
        """
        Generate a careplan from a TemplateCarePlan template
        """
        
        if save_data:
            if creator_user==None:
                raise Exception("Error, if you are saving this on creation from a template, you must enter a user")
        
        new_plan = CarePlan()
        new_plan.id = uuid.uuid4().hex
        new_plan.from_template = base_plan
        new_plan.version = 1
        new_plan.patient = patient
        
        if not title:
            new_plan.title=base_plan.title + " from template"
        
        links = []
        
        new_plan.title = base_plan.title
        for temp_item_link in base_plan.templatecareplanitemlink_set.all():            
            base_item = temp_item_link.item
            new_item= CarePlanItem.create_from_template(base_item, parent_item=None)
            links.append(CarePlanItemLink(plan=new_plan, item=new_item, order=temp_item_link.order))
        
        if creator_user:
            new_plan.created_by = creator_user
            new_plan.created_date = datetime.utcnow()
            
            new_plan.modified_by = creator_user
            new_plan.modified_date= datetime.utcnow()        
        
        if save_data:
            new_plan.save()
            for link in links:
                link.save()
        return new_plan
    

    
