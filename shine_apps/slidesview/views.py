from django.contrib.auth.decorators import login_required
from django.core.files.base import ContentFile, File
from django.core.files.uploadedfile import InMemoryUploadedFile
from django.core.servers.basehttp import FileWrapper
from django.core.urlresolvers import reverse
from django.db.models.fields.files import FileField
from django.http import HttpResponse
from django.shortcuts import render_to_response
from django.template.context import RequestContext
import simplejson
from functools import partial
from sorl.thumbnail.shortcuts import get_thumbnail
from couchforms.models import XFormInstance
import tempfile
from dimagi.utils.couch.database import get_db
from hutch.models import AttachmentImage


@login_required
def slideform(request, doc_id, template_name="slidesview/view_slide_form.html"):
    """
    View an actual slideform, this default view currently includes some client side eye candy.
    To dynamically manage the images in the browser, use the thumbsize url param or the crop param.
    """

    thumbsize = int(request.GET.get('thumbsize', 100))
    crop = request.GET.get('crop','center')

    def mk_thumbnail(slide, k):
        attach = AttachmentImage.objects.get(xform_id=slide._id, attachment_key=k)
        im = get_thumbnail(attach.image, '%sx%s' % (thumbsize, thumbsize), crop=crop, quality=90)
        return im

    context = RequestContext(request)
    xform = XFormInstance.get(doc_id)
    case = xform.form['case']
    thumbs = [mk_thumbnail(xform, k) for k, v in xform._attachments.iteritems() if k != 'form.xml']

    context['thumbs'] = thumbs
    context['case'] = case
    return render_to_response(template_name, context_instance=context)

@login_required
def all_slideforms(request, template_name="slidesview/all_slide_forms.html"):
    context = RequestContext(request)

    slides = XFormInstance.view('slidesview/all_bloodwork_slides', include_docs=True).all()
    context['submits'] = slides
    return render_to_response(template_name, context_instance=context)


