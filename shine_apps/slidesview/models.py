import os
from django.conf import settings
from django.db import models
from dimagi.utils import make_uuid
from sorl.thumbnail import ImageField

class ImageAttachment(models.Model):
    id = models.CharField(max_length=32, unique=True, default=make_uuid, primary_key=True, editable=False)
    xform_id = models.CharField(max_length=32)
    attachment_key = models.CharField(max_length=255)
    content_type = models.CharField(max_length=160)
    content_length=models.IntegerField()
    image = ImageField(upload_to=os.path.join(settings.MEDIA_ROOT, 'attachments'))


