from django.core.files.base import ContentFile
from sorl.thumbnail.models import KVStore
from couchforms.models import XFormInstance
from hutch.models import AttachmentImage
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    option_list = BaseCommand.option_list + (
    )
    help = 'Precompute image attachments from couchdb to a django model for sorl-thumbnails'
    args = "script [script ...]"

    def handle(self, *scripts, **options):
        AttachmentImage.objects.all().delete()
        KVStore.objects.all().delete()
        slides = XFormInstance.view('slidesview/all_bloodwork_slides', include_docs=True).all()
        for slide in slides:
            print "Recomputing image attachment for form %s" % (slide._id)
            for k, v in slide._attachments.items():
                if k == 'form.xml':
                    continue
                img = AttachmentImage()
                img.xform_id = slide._id
                img.attachment_key = k
                img.content_length = v['length']
                img.content_type = v['content_type']

                imgfile = ContentFile(slide.fetch_attachment(k, stream=True).read())
                img.image.save(k, imgfile)
                img.save()
        print "\nRecompute done."

