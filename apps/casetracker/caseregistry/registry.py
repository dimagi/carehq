from casetracker.models import Category, EventActivity, Status, StatusActivityLink

#
#class CategoryStruct(object):
#    def __init__(self, slug=None, display=None, plural=None):
#        self.slug = slug
#        self.display = display
#        self.plural = plural
#
#class ActivityStruct(object):
#    def __init__(self, slug=None, past_tense=None, active_tense=None, event_class=None):
#        self.slug = slug
#        self.past_tense = past_tense
#        self.active_tense = active_tense
#        self.event_class = event_class
#
#class StatusStruct(object):
#    def __init__(self, slug=None, display=None):        
#        self.slug = slug
#        self.display = display

#from the django admin for inspiration
#def register(self, model_or_iterable, admin_class=None, **options):
#        """
#        Registers the given model(s) with the given admin class.
#
#        The model(s) should be Model classes, not instances.
#
#        If an admin class isn't given, it will use ModelAdmin (the default
#        admin options). If keyword arguments are given -- e.g., list_display --
#        they'll be applied as options to the admin class.
#
#        If a model is already registered, this will raise AlreadyRegistered.
#        """
#        if not admin_class:
#            admin_class = ModelAdmin
#
#        # Don't import the humongous validation code unless required
#        if admin_class and settings.DEBUG:
#            from django.contrib.admin.validation import validate
#        else:
#            validate = lambda model, adminclass: None
#
#        if isinstance(model_or_iterable, ModelBase):
#            model_or_iterable = [model_or_iterable]
#        for model in model_or_iterable:
#            if model in self._registry:
#                raise AlreadyRegistered('The model %s is already registered' % model.__name__)
#
#            # If we got **options then dynamically construct a subclass of
#            # admin_class with those **options.
#            if options:
#                # For reasons I don't quite understand, without a __module__
#                # the created class appears to "live" in the wrong place,
#                # which causes issues later on.
#                options['__module__'] = __name__
#                admin_class = type("%sAdmin" % model.__name__, (admin_class,), options)
#
#            # Validate (which might be a no-op)
#            validate(admin_class, model)
#
#            # Instantiate the admin class to save in the registry
#            self._registry[model] = admin_class(model, self)


def RegisterCategory(category_bridge_class, overwrite = False, except_on_collision = False):
    bridge = category_bridge_class()
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
        
        

def RegisterStatus(status_bridge_class):
    bridge = status_bridge_class()    
    exists=False
    try:    
        status = Status.objects.get(slug=bridge.slug)
        exists = True
    except:     
        stat = Status()        
        stat.slug = bridge.slug
        stat.display = bridge.display
        stat.category = Category.objects.get(slug=bridge.category_bridge().slug)
        stat.state_class = bridge.state_class
        stat.save()
        exists = False        
    
    
def RegisterDefaultStates(category_bridge_class):
    #raise Exception("not implemented")
    pass

def RegisterDefaultActivities(status_bridge_class):
    #raise Exception("not implemented")
    pass

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
    
    
                        

def RegisterActivity(status_bridge_class, activity_bridge_class):    
    status = Status.objects.get(slug=status_bridge_class().slug)
    activity_bridge = activity_bridge_class()
    
    _do_register_activity(status, activity_bridge)  
    
#def InitRegistrar():
#    for cls in CategoryRegistrar.__subclasses__():
#        print cls