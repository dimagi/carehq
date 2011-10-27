import os
from django.conf import settings
from django.db import models
from storages.backends.couchdb_storage import CouchDBStorage
from dimagi.utils import make_uuid
from sorl.thumbnail import ImageField
from slidesview.couchdb_doc_storage import CouchDBDocStorage


couchdb_doc_storage = CouchDBDocStorage(server=settings.COUCH_SERVER, database=settings.COUCH_DATABASE_NAME)
couchdb_storage = CouchDBStorage(server=settings.COUCH_SERVER, database=settings.COUCH_DATABASE_NAME)

class ImageAttachment(models.Model):
    id = models.CharField(max_length=32, unique=True, default=make_uuid, primary_key=True, editable=False)
    patient_guid = models.CharField(max_length=32, null=True, blank=True, db_index=True)
    xform_id = models.CharField(max_length=32, null=True, blank=True, db_index=True)
    attachment_key = models.CharField(max_length=255, db_index=True)
    content_type = models.CharField(max_length=160)
    content_length=models.IntegerField()
    image = ImageField(max_length=255,upload_to=os.path.join(settings.MEDIA_ROOT, 'attachments'))
    checksum = models.CharField(max_length=32, help_text='MD5 of the Image submitted')
    #image = ImageField(max_length=255, storage=couchdb_doc_storage, upload_to=os.path.join(settings.MEDIA_ROOT, 'attachments'))
    #image = ImageField(max_length=255, storage=couchdb_storage, upload_to=os.path.join(settings.MEDIA_ROOT, 'attachments'))



    def clean(self):
        from django.core.exceptions import ValidationError
        #Don't allow both patient_guid AND xform_id to be None
        if self.patient_guid is None and xform_id is None:
            raise ValidationError('You must either set a patient_guid or xform_id, both cannot be None')


    def __unicode__(self):
        return "%s (Filename: %s, Content-Type: %s, Size: %d)" % (self.xform_id, self.attachment_key, self.content_type, self.content_length)


