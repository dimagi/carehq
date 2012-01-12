from django.db import models
from django.contrib.auth.models import User
from dimagi.utils.make_time import make_time
from dimagi.utils.make_uuid import make_uuid
from permissions.models import Actor
from django.utils.translation import ugettext_lazy as _

class BaseNewsEvent(models.Model):
    id = models.CharField(_('Unique News Event ID'), max_length=32, unique=True, default=make_uuid, primary_key=True, editable=False)
    message = models.CharField(max_length=350)
    created = models.DateTimeField(default=make_time, auto_now_add=True)
    class Meta:
        abstract = True

class FeedEvent(models.Model):
    # Examples:
    # subject = patient, actor = doctor, action = "Edited care plan"
    # Feed Event is the piece of information, the visibility of it to other people is governed by those who subscribe to it
    creator = models.ForeignKey(Actor, related_name="feed_actor", help_text="Who did the action")
    subject = models.ForeignKey(Actor, related_name="feed_subject", help_text="Who is the primary recipient of this action", null=True, blank=True)
    body = models.TextField(help_text="The content of this news event")
    created = models.DateTimeField(default=make_time)


# foo has added bar to patient X's careteam
# actor = foo, feedinbox  bar and X, potentially everyone on careteam actually.
#
class FeedInbox(models.Model):
    actor_inbox = models.ForeignKey(Actor, related_name="feed_inbox", help_text='The actor inbox')
    event = models.ForeignKey(FeedEvent)
    read = models.BooleanField(default=False)
    archived = models.BooleanField(default=False)


#feed manager:
#accessor for user (all actors)
#per actor
#get read vs. unread
#inbox vs. all (archived or not archived)

#make dispatcher.  make feedinbox entries for everyone in careteam for stuff pertaining to patient.
#added/removed from careteam
#changes to models, add/remove careplan



def notify(subject, actor, action, type_id=None):
    f = FeedEvent(subject=subject,actor=actor,action=action,type_id=type_id)
    f.save()
    
