#def get_careteam_assignment_choices(case):
#    """
#    Provides a centralized way to get the careteam list to show on an carehqapp case view.
#    """
#    careteams = case.careteam_set.all()
#    providers_set = Provider.objects.none()
#    caregivers_set = CaregiverLink.objects.none()
#
#    #get the split ids of users for caregivers and providers
#    for ct in careteams:
#        providers_qset = ct.providers.all()
#        providers_set = providers_set | providers_qset
#
#        caregivers_qset = CaregiverLink.objects.filter(careteam=ct)
#        caregivers_set = caregivers_set | caregivers_qset
#
#
#
#    #make the optgroup tuples
#    #source: http://dealingit.wordpress.com/2009/10/26/django-tip-showing-optgroup-in-a-modelform/
#    prov_tuple = [[prov.user.id, "%s - %s" % (prov.user.title(), prov.job_title)] for prov in providers_set.order_by('user__last_name')]
#    cg_tuple = [[cglink.user.id, "%s - %s" % (cglink.user.title(), cglink.relationship)] for cglink in caregivers_set.order_by('user__last_name')]
#
#    list_choices = [['Providers', prov_tuple],
#                    ['Caregivers',cg_tuple]]
#
#    return list_choices
#
#def ashand_case_context(case, request, context):
#    context['case'] = case
#    context['can_edit'] = False
#    context['can_assign'] = False
#    context['can_resolve'] = False
#    context['can_close'] = False
#
#    if request.user == case.opened_by:
#        context['can_edit'] = True
#
#    if request.is_provider:
#        context['can_assign'] = True
#        context['can_resolve'] = True
#        context['can_close'] = True
#
#    context['case_careteams'] = case.careteam_set.all()
#    context['careplan'] = TemplateCarePlan.objects.all()[0]
#    context['plan_items'] = context['careplan'].templatecareplanitemlink_set.all()
#    context['show_children'] = True
#    return context