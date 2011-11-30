from django.shortcuts import render_to_response
from django.contrib.auth.decorators import login_required
from django.template import RequestContext

@login_required
def my_network(request, template_name='carehqapp/care_network.html'):
    """
    If current user is a patient, get all providers surrounding my care.
    """
#    context = {}
#    user = request.user
#    is_patient=False
#    is_provider=False
#    try:
#        careteam = CareTeam.objects.get(patient=user)
#        is_patient=True
#        context['my_careteam'] = careteam
#    except:
#        pass
#
#    #if i'm a provider, get my patients and show them
#    providers = Provider.objects.select_related('user').filter(user=request.user)
#    if len(providers) > 0:
#        is_provider = True
#        #careteam_membership = ProviderLink.objects.select_related('careteam','provider','role').filter(provider__id=user.id).values_list("careteam__id",flat=True)
#        careteam_membership = CareTeam.objects.select_related().filter(providers__in=providers)
#        context['my_patients_careteams'] = careteam_membership
#
#    context['is_patient'] = is_patient
#    context['is_provider'] = is_provider
#    return render_to_response(template_name, context, context_instance=RequestContext(request))
    raise Exception("not implemented with new actor framework")

@login_required
#@provider_only
def my_patients(request, template_name='carehqapp/my_patients.html'):
    """
    View for providers caring for multiple patients.
    """
#    context = {}
#    careteam_membership = CareTeam.objects.select_related().filter(providers=request.provider).order_by('patient__user__last_name')
#    context['my_patients'] = careteam_membership
#    return render_to_response(template_name, context, context_instance=RequestContext(request))
    raise Exception("not implemented with new actor framework")


@login_required
#@caregiver_only
def my_care_recipients(request, template_name='carehqapp/my_care_recipients.html'):
    """
    View for caregivers caring for multiple patients.  effectively this should be similar to the providers "my patients" view
    """
#    context = {}
#    careteam_membership = CareTeam.objects.select_related().filter(caregivers=request.user)
#    context['my_care_recipients'] = careteam_membership
#    return render_to_response(template_name, context, context_instance=RequestContext(request))
    raise Exception("not implemented with new actor framework")

@login_required
#@patient_only
def my_careteam(request, template_name='carehqapp/careteam/view_careteam.html'):
#    #i'm a patient, get my careteam and show providers
#    context = {}
#    try:
#        careteam = CareTeam.objects.get(patient__user=request.user)
#        context['careteam'] = careteam
#
#        cases = careteam.cases.all()
#        context['cases'] = cases
#        context['patient']= careteam.patient
#
#        provider_links_raw = careteam.providerlink_set.all()
#        provider_dict = {}
#
#        for plink in provider_links_raw:
#            prov = plink.provider
#            provider_dict[prov] = plink
#            context['provider_dict'] = provider_dict
#    except:
#        pass
#
#    return render_to_response(template_name, context, context_instance=RequestContext(request))
    raise Exception("not implemented with new actor framework")