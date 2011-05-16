from django.db import models
from django.contrib.auth.models import User
from permissions.models import Actor


class FeedEvent(models.Model):
    # Examples:
    # subject = patient, actor = doctor, action = "Edited care plan"
    subject = models.ForeignKey(Actor, related_name="feed_subject")
    actor = models.ForeignKey(Actor, related_name="feed_actor")
    action = models.TextField()
    created = models.DateTimeField(auto_now_add=True)
    read = models.BooleanField(default=False)
    type_id = models.TextField(null=True, blank=True) # For CSS purposes

def notify(subject, actor, action, type_id=None):
    f = FeedEvent(subject=subject,actor=actor,action=action,type_id=type_id)
    f.save()
    
