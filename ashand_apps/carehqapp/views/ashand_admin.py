from django.contrib.auth.forms import PasswordResetForm
from django.contrib.auth.models import User
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.contrib.auth.views import password_reset
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect, Http404
from django.shortcuts import render_to_response
from django.template.context import RequestContext
from django.test.client import Client
from carehqapp.models import CCDSubmission
from patient.models import Patient
from django.contrib.auth.decorators import login_required, user_passes_test


@login_required
@user_passes_test(lambda u: u.is_superuser)
def admin_invite_activate_actor_user(request, user_id):
    """
    For a given user send a custom activation/invitation email that sends a password reset email with a template
    that says their account is ready for use.
    """

    user = User.objects.get(id=user_id)
    form = PasswordResetForm({'email': user.email})
    if form.is_valid():
        opts = {
            'use_https': True,
            'token_generator': PasswordResetTokenGenerator(),
            'from_email': "ashand-system@dimagi.com",
            'email_template_name': 'carehqapp/invite_password_reset_email_carehq.html',
            'request': request,
        }
        form.save(**opts)
        return HttpResponseRedirect(reverse('carehqapp.views.ashand_admin.admin_patient_list'))
    else:
        raise Http404


@login_required
@user_passes_test(lambda u: u.is_superuser)
def admin_study_landing(request, template_name="carehqapp/admin_study_landing.html"):
    context = RequestContext(request)
    return render_to_response(template_name, context, context_instance=RequestContext(request))

@login_required
@user_passes_test(lambda u: u.is_superuser)
def admin_patient_list(request, template_name="carehqapp/admin_patient_list.html"):
    context = RequestContext(request)
    patients = Patient.objects.all()
    context['django_patients'] = patients
    return render_to_response(template_name, context, context_instance=RequestContext(request))

@login_required
@user_passes_test(lambda u: u.is_superuser)
def admin_provider_list(request, template_name="carehqapp/admin_provider_list.html"):
    pass

@login_required
@user_passes_test(lambda u: u.is_superuser)
def admin_caregiver_list(request, template_name="carehqapp/admin_caregiver_list.html"):
    pass

@login_required
@user_passes_test(lambda u: u.is_superuser)
def admin_ccd_submissions(request, template_name="carehqapp/admin_ccd_submissions.html"):
    context = RequestContext(request)
    submissions = CCDSubmission.view('carehqapp/ccd_submits_by_patient_doc', include_docs=True).all()
    context['submissions'] = submissions
    return render_to_response(template_name, context, context_instance=RequestContext(request))


@login_required
@user_passes_test(lambda u: u.is_superuser)
def admin_user_activity(request, template_name="carehqapp/admin_user_activity.html"):
    context = RequestContext(request)
    submissions = []
    context['activities'] = submissions
    return render_to_response(template_name, context, context_instance=RequestContext(request))


