from StringIO import StringIO
from django.core.management import call_command
from django.contrib.auth.decorators import user_passes_test, login_required
from django.core.servers.basehttp import FileWrapper
from django.http import HttpResponse, Http404
import simplejson
from casexml.apps.case.models import CommCareCase, CommCareCaseAction
from couchforms.models import XFormInstance
from pactpatient.models import PactPatient
from patient.models import Patient
from django_digest.decorators import httpdigest
from dateutil.parser import parse
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

def generate_actions(delta_xform_ids):
    for xform_id in delta_xform_ids:
        xform = XFormInstance.get(xform_id)
        action = CommCareCaseAction()
        is_set = False
        if xform['form'].has_key('meta'):
            if xform['form']['meta'].has_key('timeStart'):
                if xform['form']['meta']['timeStart'] != "":
                    if isinstance(xform['form']['meta']['timeStart'], str):
                        action.date = parse(xform['form']['meta']['timeStart'])
                    else:
                        action.date = xform['form']['meta']['timeStart']
                    is_set=True
        if not is_set:
            action.date = xform.received_on
        action.xform_id = xform_id
        yield action

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
    print "## Opened CaseID: %s" % case_id
    raw_actions = casedoc.actions
    print "\traw actions: %d" % len(raw_actions)
    clean_actions = sorted(set(raw_actions), key=lambda x: x.date)
    print "\tclean actions: %d" % len(clean_actions)
    raw_xforms = set(casedoc.xform_ids)
    print "\traw_xforms set: %d" %  len(raw_xforms)

    patient_doc = PactPatient.view('pactpatient/by_case_id', key=casedoc['case_id'], include_docs=True).first().to_json()
    pact_id = patient_doc['pact_id']
    sk = [pact_id, 0]
    ek = [pact_id, 3000]
    dangling_by_pactid = XFormInstance.view('pactcarehq/all_submits_by_patient_date', startkey=sk, endkey=ek, include_docs=False).all()
    dangling_by_pactid_ids = [x['id'] for x in dangling_by_pactid]
    delta_pact = set(dangling_by_pactid_ids).difference(set(casedoc.xform_ids))

    dangling_by_case = XFormInstance.view('pactcarehq/all_submits_by_case', key=case_id, include_docs=False).all()
    dangling_by_case_ids = [x['id'] for x in dangling_by_case]
    delta_cases = set(dangling_by_case_ids).difference(set(casedoc.xform_ids))
    print "\tdelta case_id %d" % len(delta_cases)

    delta_all = delta_pact.union(delta_cases)
    print "\tdelta all: %s" % len(delta_all)

    print "\tdelta pact_ids %d" % len(delta_pact)
    combined_actions = clean_actions + list(generate_actions(delta_all))
    final_actions = sorted(set(combined_actions), key=lambda x: x.date)

    casedoc.actions = final_actions
    casedoc.xform_ids = [x.xform_id for x in final_actions]


    casejson = casedoc.to_json()
    casejson['weekly_schedule'] = patient_doc['weekly_schedule']
    casejson['primary_hp'] = patient_doc['primary_hp']
    casejson['demographics'] = {
            'race': patient_doc['race'],
            'is_latino': patient_doc['is_latino'],
            'preferred_language': patient_doc['preferred_language'],
            'mass_health_expiration': patient_doc['mass_health_expiration'],
            'hiv_care_clinic': patient_doc['hiv_care_clinic'],
            'ssn': patient_doc['ssn'],
            'first_name': patient_doc['first_name'],
            'last_name': patient_doc['last_name'],
            'middle_name': patient_doc.get('middle_name', ''),
#            'birthdate'
#gender
        }

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

