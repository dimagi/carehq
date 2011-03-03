from django.contrib import admin
from models import *
from clinical_core.feed.models import FeedEvent

class FeedEventAdmin(admin.ModelAdmin):
    list_display=('subject', 'actor', 'action', 'created')
    list_filter = ['subject', 'actor']
admin.site.register(FeedEvent, FeedEventAdmin)

