import uuid
from django.http import HttpResponse
from django.shortcuts import render_to_response
from django.template.context import RequestContext
from django_digest.decorators import httpdigest
from pactpatient.models.pactmodels import PactPatient

@httpdigest()
def debug_casexml_new(request):
    """
    Use the standard way for dimagi.case casexml generation method to get casexml.  This is case OTA Restore for Pact.
    """
    regblock = get_ghetto_registration_block(request.user)
    patient_blocks = [pt.ghetto_xml() for pt in PactPatient.view('patient/search', include_docs=True).all()]
    resp_text = "<restoredata>%s %s</restoredata>" % (regblock, '\n'.join(patient_blocks))
    template_name="pactcarehq/debug_casexml.html"
    context = RequestContext(request)
    context['casexml'] = resp_text
    return render_to_response(template_name, context_instance=context)

@httpdigest()
#@profile('/home/dmyung/workspaces/pycharm/ashand-project/carehq/caselist.profile')
#@devserver_profile(follow=[PactPatient.ghetto_xml, PactPatient.get_ghetto_regimen_xml, PactPatient._cache_case])
def get_caselist(request):
    """Intermediary/ghetto way of producing casexml, to be deprecated.
    """
    regblock= get_ghetto_registration_block(request.user)
    patient_block = ""
    patients = PactPatient.view("patient/search", include_docs=True)
    for pt in patients:
        if pt.arm == "Discharged":
            continue
        patient_block += pt.ghetto_xml()
    resp_text = "<restoredata>%s %s</restoredata>" % (regblock, patient_block)
    #logging.error(resp_text)

    response = HttpResponse(mimetype='text/xml')
    response.write(resp_text)
    response['Content-Length'] = len(resp_text)
    from guppy import hpy
    h = hpy()
    print h.heap()
    return response



def get_ghetto_registration_block(user):
    registration_block = """
    <Registration xmlns="http://openrosa.org/user/registration">
        <username>%s</username>
        <password>%s</password>
        <uuid>%s</uuid>
        <date>%s</date>
        <registering_phone_id>%s</registering_phone_id>
        <user_data>
            <data key="promoter_id">%s</data>
            <data key="promoter_name">%s</data>
            <data key="promoter_member_id">%s</data>
        </user_data>
   </Registration>
   """
    #promoter_member_id is the nasty id from the csv, this should be fixed to match the Partners id -->
    resp_txt = ""
    #prov = Provider.objects.filter(user=user)[0] #hacky nasty
    return registration_block % (user.username, user.password, user.id, user.date_joined.strftime("%Y-%m-%dT%H:%M:%S.000"), uuid.uuid4().hex, user.id, user.username, "blah")




@httpdigest()
def xml_download(request):
#    username = request.user.username
#
#    if username == "ctsims":
#        username = 'cs783'
#    offset =0
#    limit_count=100
#    temp_xml = tempfile.TemporaryFile()
#    temp_xml.write("<restoredata>\n")
#    total_count = 0
#    db = get_db()
#    xforms = XFormInstance.view("pactcarehq/all_submits", key=username).all()
#    for form in xforms:
#        try:
#            xml_str = db.fetch_attachment(form['id'], 'form.xml').replace("<?xml version=\'1.0\' ?>", '')
#            temp_xml.write(xml_str)
#            temp_xml.write("\n")
#            total_count += 1
#        except ResourceNotFound:
#            logging.error("Error, xform submission %s does not have a form.xml attachment." % (form._id))
#    temp_xml.write("</restoredata>")
#    length = temp_xml.tell()
#    temp_xml.seek(0)
#    wrapper = FileWrapper(temp_xml)
#    response = HttpResponse(wrapper, mimetype='text/xml')
#    response['Content-Length'] = length
#    return response
    regblock= get_ghetto_registration_block(request.user)
    patient_block = ""
    patients = PactPatient.view("patient/search", include_docs=True)
    for pt in patients:
        if pt.arm == "Discharged":
            continue
        patient_block += pt.ghetto_xml()
    resp_text = "<restoredata>%s %s</restoredata>" % (regblock, patient_block)

    response = HttpResponse()
    context=RequestContext(request)
    context['casexml'] = resp_text
    print len(resp_text)
    return render_to_response('pactcarehq/debug_casexml.html', context_instance=context)

