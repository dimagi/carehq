from StringIO import StringIO
from django.core.management import call_command
from django.contrib.auth.decorators import user_passes_test, login_required
from django.core.servers.basehttp import FileWrapper
from django.http import HttpResponse, Http404
import simplejson
from casexml.apps.case.models import CommCareCase
from couchforms.models import XFormInstance
from pactpatient.models import PactPatient
from patient.models import Patient
from django_digest.decorators import httpdigest
import isodate
from permissions.models import Actor


@httpdigest
@user_passes_test(lambda u: u.is_superuser)
def get_cases(request):
    patients=Patient.objects.all()
    json_str = StringIO()
    def case_iterator():
        yield '['
        for ix, pt in enumerate(patients):
            patient_doc = getattr(pt, 'couchdoc', None)
            if patient_doc is not None:
                case_doc = patient_doc.get_case()
                if case_doc is not None:
                    yield '"%s"' % patient_doc.case_id
                if ix != len(patients) - 1:
                    yield ','
        yield ']'
    response = HttpResponse(case_iterator(), mimetype='application/json')
    return response



@httpdigest
@user_passes_test(lambda u: u.is_superuser)
def get_case(request, case_id):
    """
    Returns case's json, but sorts and filters the actions as we adulterated them.
    """

    if not CommCareCase.get_db().doc_exist(case_id):
        raise Http404

    casedoc = CommCareCase.get(case_id)
    if casedoc['doc_type'] != 'CommCareCase':
        raise Http404
    raw_actions = casedoc.actions
    clean_actions = sorted(set(raw_actions), key=lambda x: x.date)
    casedoc.actions = clean_actions

    raw_xforms = set(casedoc.xform_ids)
    casedoc.xform_ids = [x.xform_id for x in clean_actions]

    patient_doc = PactPatient.view('pactpatient/by_case_id', key=casedoc['case_id'], include_docs=True).first().to_json()
    casejson = casedoc.to_json()
    casejson['weekly_schedule'] = patient_doc['weekly_schedule']

    response = HttpResponse(simplejson.dumps(casejson), mimetype='application/json')
    return response


@httpdigest
@user_passes_test(lambda u: u.is_superuser)
def get_xform_xml(request, xform_id):
    db = XFormInstance.get_db()
    if not db.doc_exist(xform_id):
        raise Http404
    doc = XFormInstance.get(xform_id)
    if doc['doc_type'] != 'XFormInstance':
        raise Http404

    response = HttpResponse(XFormInstance.get(xform_id).fetch_attachment('form.xml'), mimetype='application/xml')
    return response



@httpdigest
@user_passes_test(lambda u: u.is_superuser)
def get_users(request):
    content = StringIO()
    call_command('dumpdata', 'auth.User', indent=4,stdout=content)
    content.seek(0)
    response = HttpResponse(content.read(), mimetype='application/json')
    return response

@httpdigest
@user_passes_test(lambda u: u.is_superuser)
def get_actors(request):
    actors = Actor.objects.all()
    def get_case_map(actor):
        """django actor"""
        for prr in actor.principal_roles.all().exclude(content_id=None):
            if prr.content is not None:
                yield (prr.role.name, prr.content.couchdoc.case_id)

    output_json = []
    for a in actors:
        actordoc = getattr(a, 'actordoc', None)
        if actordoc is not None:
            actor_json = a.actordoc.to_json()
            actor_json['user_id'] = a.user_id
            if a.user is not None:
                actor_json['username'] = a.user.username
            else:
                actor_json['username'] = ""

            actor_json['case_id_map'] = list(get_case_map(a))
            output_json.append(actor_json)

    response = HttpResponse(simplejson.dumps(output_json), mimetype='application/json')
    return response

