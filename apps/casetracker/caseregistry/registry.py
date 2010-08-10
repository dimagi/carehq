from casetracker.models import Category, EventActivity, Status
from django.db import transaction


@transaction.commit_manually
def RegisterCategory(category_bridge_class, overwrite = False, except_on_collision = False):
    bridge = category_bridge_class
    print 'registering: ' + bridge.slug
    exists=False
    try:    
        cat = Category.objects.get(slug=bridge.slug)
        exists = True
    except:     
        cat = Category()        
        cat.slug = bridge.slug
        cat.display = bridge.display
        cat.plural = bridge.plural
        cat.bridge_module = bridge.bridge_module
        cat.bridge_class = bridge.bridge_class
        cat.save()
        exists=False    
    
    if not overwrite and except_on_collision == True:        
        raise Exception("Error, there's a collision of an existent category with that slugname")
    elif not overwrite and except_on_collision == False:
        pass
    else:
        cat.save()
    transaction.commit()

        
        
@transaction.commit_manually
def RegisterStatus(status_bridge_class):
    bridge = status_bridge_class
    print "registering status %s" % bridge.slug
    exists=False
    try:    
        status = Status.objects.get(slug=bridge.slug)
        exists = True
    except:     
        stat = Status()        
        stat.slug = bridge.slug
        stat.display = bridge.display
        stat.category = Category.objects.get(slug=bridge.category_bridge.slug)
        stat.state_class = bridge.state_class
        stat.save()
        exists = False        
        
    print "status registered: %s %s" % (status_bridge_class.slug, exists)
    transaction.commit()
    return exists
    
    
def RegisterDefaultStates(category_bridge_class):
    #raise Exception("not implemented")
    pass

def RegisterDefaultActivities(status_bridge_class):
    #raise Exception("not implemented")
    pass

@transaction.commit_manually
def _do_register_activity(status, activity_bridge):    
    try:
        activity = EventActivity.objects.get(slug=activity_bridge.slug)
    except:
        activity = EventActivity()
        activity.slug = activity_bridge.slug
        activity.past_tense = activity_bridge.past_tense
        activity.active_tense = activity_bridge.active_tense
        activity.summary = activity_bridge.summary
        activity.event_class = activity_bridge.event_class
        
        
        activity.bridge_module = activity_bridge.bridge_module
        activity.bridge_class = activity_bridge.bridge_class
        
        activity.category = status.category
        activity.save()    
    print "\tStatus [%s]: adding Activity [%s]" % ( status.slug, activity.slug  )
        
    try:
        status.set_activity(activity)
    except:
        pass
    transaction.commit()
    
@transaction.commit_manually
def RegisterStatelessActivity(activity_bridge_class):    
    activity_bridge = activity_bridge_class    
    try:
        activity = EventActivity.objects.get(slug=activity_bridge.slug)
    except:
        activity = EventActivity()
        activity.slug = activity_bridge.slug
        activity.past_tense = activity_bridge.past_tense
        activity.active_tense = activity_bridge.active_tense
        activity.summary = activity_bridge.summary
        activity.event_class = activity_bridge.event_class
        
        activity.bridge_module = activity_bridge.bridge_module
        activity.bridge_class = activity_bridge.bridge_class
        
        activity.category = Category.objects.get(slug=activity_bridge.category_bridge.slug)
        activity.save()    
        transaction.commit()
    print "Adding Activity [%s] with no valid status" % ( activity.slug  )
        
                      
@transaction.commit_manually
def RegisterActivity(status_bridge_class, activity_bridge_class):  
    print "Registering activity: %s %s" %  (status_bridge_class.slug, activity_bridge_class)  
    
    status = Status.objects.get(slug=status_bridge_class.slug)    
    
    activity_bridge = activity_bridge_class    
    _do_register_activity(status, activity_bridge)  
    
    
    
#def InitRegistrar():
#    for cls in CategoryRegistrar.__subclasses__():
#        print cls