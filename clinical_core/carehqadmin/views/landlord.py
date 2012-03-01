from django.contrib.auth.decorators import login_required, user_passes_test
from django.shortcuts import render_to_response
from django.template.context import RequestContext
from tenant.models import Tenant




@login_required
@user_passes_test(lambda u: u.is_superuser)
def landing(request, template="carehqadmin/landlord/landlord_landing.html"):
    context = RequestContext(request)
    context['tenants'] = Tenant.objects.all()
    return render_to_response(template, context)
