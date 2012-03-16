import uuid
from couchdbkit.ext.django.schema import Document, StringProperty, SchemaListProperty, DateTimeProperty, ListProperty, StringListProperty, SchemaProperty, BooleanProperty, DateProperty, DocumentSchema
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

#    due_date = DateTimeProperty() #these are put in the instances

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
    plan_items = SchemaListProperty(DocumentSchema)

    tags = StringListProperty()

    created_by = StringProperty()
    created_date = DateTimeProperty()
    
    modified_by =  StringProperty()
    modified_date = DateTimeProperty()

    def get_absolute_url(self):
        return reverse('careplan.views.caretemplates.single_template_careplan', kwargs={"plan_id":self._id})
    
    def __unicode__(self):
        return "[Plan Template] %s" % (self.title)


class BaseCarePlanGroup(Document):
    title = StringProperty()
    template_plans = SchemaListProperty(BaseCarePlan)
    tags = StringListProperty()

    created_by = StringProperty()
    created_date = DateTimeProperty()

    modified_by =  StringProperty()
    modified_date = DateTimeProperty()

    def __unicode__(self):
        return "[Plan Template Group] %s" % (self.title)



CAREPLAN_ITEM_STATES = ( ('open', 'Open'),
                         ('closed-completed', 'Completed'),
                         ('closed-cancelled', 'Cancelled'),
    )

class CarePlanItem(BaseCarePlanItem):
    status = StringProperty(choices=CAREPLAN_ITEM_STATES)
    issues = StringListProperty(verbose_name="A list of the Issue django ids that belong to this CarePlanItem")
    due_date=DateProperty(verbose_name="Item due date")

    origin_id = StringProperty(verbose_name='The doc id of the BaseCarePlanItem that this instance is originated from')
    origin_rev = StringProperty(verbose_name='The rev_id of the BaseCarePlanItem that this instance originated from')

    def get_absolute_url(self):
        return reverse('careplan.views.planinstances.view_careplan_item', kwargs={"item_id":self.id})

    def __unicode__(self):
        return "[CarePlanItem] %s" % self.title
    
    @staticmethod
    def create_from_template(base_item):
        """
        Factory method to generate a new plan item from a template
        base_plan is the BaseCarePlanItem instance
        parent_item is a PlanItem instance parent if you're generating this programmatically
        save = do we save this to db before returning?
        """
        new_item = CarePlanItem()
        new_item._id = uuid.uuid4().hex
        new_item.title = base_item.title
        new_item.tags.extend(base_item.tags)
        new_item.description = base_item.description
        new_item.status = CAREPLAN_ITEM_STATES[0][0]
        new_item.issue_container = base_item.issue_container

        new_item.origin_id = base_item['_id']
        new_item.origin_rev = base_item['_rev']

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
    def create_from_template(base_plan):
        """
        Generate a careplan from a BaseCarePlan template
        This does not save to the database.
        """
        
        new_plan = CarePlanInstance()
        new_plan._id = uuid.uuid4().hex

        new_plan.origin_id = base_plan._id
        new_plan.origin_rev = base_plan._rev

        new_plan.created_date = make_time()
        new_plan.modified_date = make_time()

        new_plan.title = base_plan.title
        new_plan.description = base_plan.description

        for base_item in base_plan.plan_items:
            new_plan.plan_items.append(CarePlanItem.create_from_template(base_item))

        return new_plan
    

    
