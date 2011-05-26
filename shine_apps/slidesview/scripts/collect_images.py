from functools import partial
import os
from django.core.files.base import ContentFile
from sorl.thumbnail.models import KVStore
from couchforms.models import XFormInstance
from slidesview.models import ImageAttachment
from django.conf import settings

def run():
    ImageAttachment.objects.all().delete()
    KVStore.objects.all().delete()
    slides = XFormInstance.view('slidesview/all_bloodwork_slides', include_docs=True).all()
    for slide in slides:
        #attachments = dict((k, partial(attachment_getter, xform, k)) for k, v in xform._attachments.iteritems() if k != "form.xml")
        for k, v in slide._attachments.items():
            if k == 'form.xml':
                continue
            img = ImageAttachment()
            img.xform_id = slide._id
            img.attachment_key = k
            img.content_length = v['length']
            img.content_type = v['content_type']


            imgfile = ContentFile(slide.fetch_attachment(k, stream=True).read())
            img.image.save(k, imgfile)
            img.save()

