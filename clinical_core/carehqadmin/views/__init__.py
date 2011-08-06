from django.contrib.auth.decorators import login_required
from django.shortcuts import render_to_response
from django.template.context import RequestContext

@login_required
def landing(request, template='carehqadmin/landing.html'):
    context = RequestContext(request)
    context['profiles'] = []
    return render_to_response(template, context)


@login_required
def all_pact_providers(request):
    pass
@login_required
def new_pact_provider(request):
    pass

