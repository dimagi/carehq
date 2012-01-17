import uuid
from couchdbkit.ext.django.schema import Document, StringProperty, SchemaListProperty, DateTimeProperty, ListProperty, StringListProperty, SchemaProperty, BooleanProperty, DateProperty
from couchdbkit.schema.properties_proxy import SchemaDictProperty
from django.db import models
from django.contrib.auth.models import User
from issuetracker.models import Issue
from patient.models import Patient
from datetime import datetime
from django.utils.translation import ugettext_lazy as _
from django.core.urlresolvers import reverse


# Create your models here.
from dimagi.utils import make_uuid, make_time

#class PlanRule(models.Model):
#    """
#    A Plan Rule is a container for custom code to operate upon a plan.
#    The example for a plan rule would be scheduling recurring visits based on a certain condition,
#    or scheduling visits for a pregnancy 2,4,6,8 months from the expected conception date.
#    """
#    name = models.CharField(max_length=160)
#    description = models.TextField()
#    module = models.CharField(max_length=255)
#    method = models.CharField(max_length=128)
#
#    class Meta:
#        verbose_name = "Plan Rule"
#        verbose_name_plural = "Plan Rules"
#        ordering = ['name',]

class BaseCarePlanItem(Document):
    """
    Instances of directives and recommendations and milestones that would be within a care plan.
    These can and will be stored as individal documents to be assembled later in BaseCarePlans
    """
    tenant = StringProperty() #tenant membership of this careplan
    title = StringProperty()
    description = StringProperty()
    tags = StringListProperty()

    created_by = StringProperty()
    created_date = DateTimeProperty()

    modified_by =  StringProperty()
    modified_date = DateTimeProperty()

    issue_container = BooleanProperty(default=True, verbose_name="Will this care plan item be something that tracks against Issues")

    def get_absolute_url(self):
        return reverse('careplan.views.caretemplates.single_template_item', kwargs={"item_id":self._id})

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
        return self.title

class BaseCarePlan(Document):
    """
    A container for BaseCarePlanItems to show a template grouping of care plan items to make a larger care plan document.
    A Care Plan is comprised of a one-deep listing of CarePlan items.
    """
    tenant = StringProperty() #who does this careplan template belong to
    title = StringProperty()
    description = StringProperty()
    plan_items = SchemaListProperty(BaseCarePlanItem)

    tags = StringListProperty()

    created_by = StringProperty()
    created_date = DateTimeProperty()
    
    modified_by =  StringProperty()
    modified_date = DateTimeProperty()

    
    def get_absolute_url(self):
        return reverse('careplan.views.caretemplates.single_template_careplan', kwargs={"plan_id":self._id})
    
    def __unicode__(self):
        return "[Plan Template] %s" % (self.title)


CAREPLAN_ITEM_STATES = ( ('open', 'Open'),
                         ('closed-completed', 'Completed'),
                         ('closed-cancelled', 'Cancelled'),
    )

class CarePlanItem(BaseCarePlanItem):
    status = StringProperty(choices=CAREPLAN_ITEM_STATES)
    issues = StringListProperty(verbose_name="A list of the Issue django ids that belong to this CarePlanItem")
    due_date=DateProperty(verbose_name="An optional field indicating whether or not this has a due date.")

    origin_id = StringProperty(verbose_name='The doc id of the BaseCarePlanItem that this instance is originated from')
    origin_rev = StringProperty(verbose_name='The rev_id of the BaseCarePlanItem that this instance originated from')

    def get_absolute_url(self):
        return reverse('careplan.views.planinstances.view_careplan_item', kwargs={"item_id":self.id})

    def __unicode__(self):
        return "[CarePlanItem] %s" % self.title
    
    @staticmethod
    def create_from_template(base_item, parent_item=None):
        """
        Factory method to generate a new plan item from a template
        base_item is the BaseCarePlanItem instance
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

class CarePlanInstance(BaseCarePlan):
    patient_guid = StringProperty(verbose_name="The Patient GUID to whom this is assigned to")
    status = StringProperty(choices=CAREPLAN_ITEM_STATES)

    origin_id = StringProperty(verbose_name='The doc id of the BaseCarePlan that this instance is originated from')
    origin_rev = StringProperty(verbose_name='The rev_id of the BaseCarePlan that this instance originated from')

    def get_absolute_url(self):
        return reverse('careplan.views.planinstances.single_template_careplan', kwargs={"plan_id":self.id})
    
    def __unicode__(self):
        return "[CarePlanInstance] %s" % self.title
    
    @staticmethod
    def create_from_template(base_plan, patient, title=None, save_data=False, creator_user=None):
        """
        Generate a careplan from a BaseCarePlan template
        """
        
        if save_data:
            if creator_user==None:
                raise Exception("Error, if you are saving this on creation from a template, you must enter a user")
        
        new_plan = CarePlanInstance()
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
    

    
