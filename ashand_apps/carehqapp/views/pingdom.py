from django.contrib.auth.models import User
from django.http import HttpResponse
from couchforms.models import XFormInstance
import hashlib


def uptime(request):
    users = User.objects.all().count()
    submits = XFormInstance.view('carehqapp/ccd_submits_by_patient_doc', include_docs=True, limit=5).all()
    #response = HttpResponse("success 22ff3ccfe2994d108ea8be5125d3fb88")
    response = HttpResponse(hashlib.sha1('success').hexdigest())
    return response

