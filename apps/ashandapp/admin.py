from django.contrib import admin

from models import *
from casetracker.registry import CategoryHandler
from django.contrib.contenttypes.models import ContentType

#
#try:
#    admin.site.unregister(User)
#except:
#    pass
#
#class UserRevision(VersionAdmin):
#    list_display=('id','first_name','last_name','email')
#
#admin.site.register(User, UserRevision)


##Load CategoryHandler registry
#for cls in CategoryHandler.__subclasses__():
    #ctype = ContentType.objects.get_for_model(cls)
    #model = ctype.model_class()

