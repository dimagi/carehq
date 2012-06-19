import tempfile
import uuid
from django.core.servers.basehttp import FileWrapper
from django.http import HttpResponse
from django.shortcuts import render_to_response
from django.template.context import RequestContext
from django_digest.decorators import httpdigest
from casexml.apps.case.xml import V2
from casexml.apps.phone.restore import  generate_restore_payload
from couchforms.models import XFormInstance
from pactcarehq.models import PactUser
from pactcarehq.views.util import ms_from_timedelta
from pactpatient.models import PactPatient
from datetime import datetime
from django.contrib.auth.models import User as DjangoUser

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
def get_caselist(request):
    """Intermediary/ghetto way of producing casexml, to be deprecated.
    """
    regblock= get_ghetto_registration_block(request.user)
    patient_block = ""
    patients = PactPatient.view("patient/search", include_docs=True)
    for pt in patients:
        #if pt.arm == "Discharged":
            #continue
        patient_block += pt.ghetto_xml()

    resp_text = "<restoredata>%s %s</restoredata>" % (regblock, patient_block)
    response = HttpResponse(mimetype='text/xml')
    response.write(resp_text)
    return response




@httpdigest
def ota_restore_casexml(request):
    """
    2.0 restore methods
    """
    #user_id=str(django_user.pk), username=django_user.username, password=django_user.password, date_joined=django_user.date_joined, user_data={})
    #(self, user_id, username, password, date_joined,  user_data=None, additional_owner_ids=[]):
    all_user_ids = list(DjangoUser.objects.all().exclude(id=request.user.id).values_list('id', flat=True))
    user = PactUser(str(request.user.id),
                    request.user.username,
                    request.user.password,
                    request.user.date_joined,
                    user_data = {'promoter_id': str(request.user.id), 'promopter_name': request.user.username, 'promoter_member_id': 'blah'},
                    additional_owner_ids = [str(x) for x in all_user_ids]
        )

    restore_id = request.GET.get('since')
    response = generate_restore_payload(user, restore_id, version=V2)
    return HttpResponse(response, mimetype="text/xml")


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
def progress_note_download(request):
    """
    Download prior progress note submissions for local access
    """
    username = request.user.username
    if request.user.username == 'admin':
        username = 'ctsims'


    offset =0
    limit_count=100
    temp_xml = tempfile.TemporaryFile()
    temp_xml.write("<restoredata>\n")
    total_count = 0
    db = XFormInstance.get_db()


    submits_iter = XFormInstance.view('pactcarehq/progress_notes_by_chw_per_patient_date', startkey=[username, None], endkey=[username, {}], include_docs=True).iterator()


    #get all patients to determine which to filter.
    all_patients = PactPatient.view('pactcarehq/chw_assigned_patients', include_docs=True).all()
    #assigned_patients = PactPatient.view('pactcarehq/chw_assigned_patients', key=username, include_docs=True).all()

    active_patients = []
    for pt in all_patients:
        #if pt.arm == "Discharged":
            #continue
        pact_id = pt.pact_id
        active_patients.append(pact_id)

    for form in submits_iter:
        if form.xmlns != 'http://dev.commcarehq.org/pact/progress_note':
            continue
        if form['form']['note']['pact_id'] not in active_patients:
            continue
        xml_str = db.fetch_attachment(form['_id'], 'form.xml').replace("<?xml version=\'1.0\' ?>", '').replace("<?xml version='1.0' encoding='UTF-8' ?>", '')
        temp_xml.write(xml_str)
        temp_xml.write("\n")
        total_count += 1

         #old code, going by patient first
#    for pact_id in active_patients:
#        sk = [pact_id, sixmonths.year, sixmonths.month, sixmonths.day, progress_xmlns]
#        ek = [pact_id, now.year, now.month, now.day, progress_xmlns]
#
#        xforms = XFormInstance.view('pactcarehq/dots_submits_by_patient_date', startkey=sk, endkey=ek, include_docs=True).all()
#        for form in xforms:
#            try:
#                if form.xmlns != 'http://dev.commcarehq.org/pact/progress_note':
#                    continue
#                xml_str = db.fetch_attachment(form['_id'], 'form.xml').replace("<?xml version=\'1.0\' ?>", '')
#                temp_xml.write(xml_str)
#                temp_xml.write("\n")
#                total_count += 1
#            except ResourceNotFound:
#                logging.error("Error, xform submission %s does not have a form.xml attachment." % (form._id))
    temp_xml.write("</restoredata>")
    length = temp_xml.tell()
    temp_xml.seek(0)
    wrapper = FileWrapper(temp_xml)
    response = HttpResponse(wrapper, mimetype='text/xml')
    response['Content-Length'] = length
    return response


