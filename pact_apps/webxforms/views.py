# -*- coding: utf-8 -*-
from datetime import datetime
import os
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect, HttpResponse
import urllib2
import tempfile
import logging
from django.shortcuts import get_object_or_404, render_to_response
from django.template.context import RequestContext
from couchforms.util import post_xform_to_couch
import settings
import uuid
from touchforms.formplayer.models import XForm, PlaySession

try:
    import simplejson as json
except:
    import json

def temp_landing(request):
    resp = HttpResponse()
    resp.write('<html><body><a href="/webxforms/progress_note/new/">New Progress Note</a></body></html>')
    return resp
    

def play(request, xform_id, callback=None, preloader_data={}):
    """
    Play an XForm.

    If you specify callback, instead of returning a response this view
    will call back to your method upon completion (POST).  This allows
    you to call the view from your own view, but specify a callback
    method afterwards to do custom processing and responding.

    The callback method should have the following signature:
        response = <method>(xform, document)
    where:
        xform = the django model of the form
        document = the couch object created by the instance data
        response = a valid http response
    """
    xform = get_object_or_404(XForm, id=xform_id)
    if request.method == "POST":
        if request.POST["type"] == 'form-complete':
            # get the instance
            instance = request.POST["output"]

            # post to couch
            doc = post_xform_to_couch(instance)
        else:
            doc = None

        # call the callback, if there, otherwise route back to the
        # xforms list
        if callback:
            return callback(xform, doc)
        else:
            return HttpResponseRedirect(reverse("webxforms.views.temp_landing"))

    preloader_data_js = json.dumps(preloader_data)


    return render_to_response("touchforms/touchscreen.html",
                              {"form": xform,
                               "mode": 'xform',
                               "preloader_data": preloader_data_js},
                              context_instance=RequestContext(request))

def new_progress_note(request): #patient_id
    """
    Fill out a NEW progress note
    """

    def callback(xform, doc):
        return HttpResponseRedirect(reverse('webxforms.views.temp_landing')) #go to patient page

    url_resp = urllib2.urlopen('http://build.dimagi.com/commcare/pact/pact_progress_note.xml')
    #url_resp = urllib2.urlopen('http://xforms.dimagi.com/download/48')
    xform_str = url_resp.read()
    try:
        tmp_file_handle, tmp_file_path = tempfile.mkstemp()
        tmp_file = os.fdopen(tmp_file_handle, 'w')
        tmp_file.write(xform_str.decode('utf-8').encode('utf-8'))
        tmp_file.close()
        new_form = XForm.from_file(tmp_file_path, str(file))
        notice = "Created form: %s " % file
    except Exception, e:
        logging.error("Problem creating xform from %s: %s" % (file, e))
        success = False
        notice = "Problem creating xform from %s: %s" % (file, e)
        raise e

    preloader_data = {
        "case": {"case-id": "0000000",
                 "pactid": "foo",
                 },
        "property": { "DeviceID": "touchforms"},
        "meta": {
                               "UserID": '0000000',
                               "UserName": '00000000000me',
                               }
    }
    #preloader_data = {}
    return play(request, new_form.id, callback, preloader_data)