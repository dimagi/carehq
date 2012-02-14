from django.contrib.contenttypes.models import ContentType
from django.shortcuts import render_to_response
from django.template.context import  RequestContext
from carehqapp.models import CCDSubmission
from clinical_shared.decorators import actor_required
from issuetracker.models.issuecore import Issue
from clinical_core.feed.models import FeedEvent
from django.contrib.auth.decorators import login_required
from patient.models import Patient
from permissions.models import PrincipalRoleRelation

@login_required
@actor_required
def home_news(request, template_name='carehqapp/home.html'):
    context = RequestContext(request)
    context['title'] = "News Feed"
    if request.current_actor.is_patient:
        patient = request.current_actor.actordoc.get_django_patient()
        context['issues'] = Issue.objects.filter(patient=patient)
        #hack till we get it all stitched up
        study_id=patient.couchdoc.study_id
        sk=[study_id, 0000]
        ek = [study_id, 3000]
        context['submissions']=CCDSubmission.view('carehqapp/ccd_submits_by_patient_doc', startkey=sk, endkey=ek, include_docs=True).all()
    else:
        context['issues'] = Issue.objects.care_issues(request.current_actor)
        flat_permissions = PrincipalRoleRelation.objects.filter(actor=request.current_actor)
        ptype = ContentType.objects.get_for_model(Patient)
        patient_prrs = flat_permissions.filter(content_type=ptype)
        patient_ids = set(patient_prrs.values_list('content_id', flat=True))
        my_django_patients = Patient.objects.all().filter(id__in=patient_ids)

        patient_study_ids = set([x.couchdoc.study_id for x in my_django_patients])
        all_submissions = []
        for study_id in patient_study_ids:
            sk=[study_id, 0000]
            ek = [study_id, 3000]
            submissions =CCDSubmission.view('carehqapp/ccd_submits_by_patient_doc', startkey=sk, endkey=ek, include_docs=True).all()
            all_submissions.extend(submissions)
        context['submissions'] = all_submissions
    return render_to_response(template_name, context_instance=context)

