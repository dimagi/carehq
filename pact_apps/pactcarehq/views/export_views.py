import uuid
from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse
from django import forms
from django.shortcuts import render_to_response
from django.template.context import RequestContext
from django.http import HttpResponse, HttpResponseRedirect
from couchexport.schema import get_docs
from pactcarehq.tasks import schema_export


@login_required
def export_excel_file(request):
    """
    Download all data for a couchdbkit model
    """

    namespace = request.GET.get("export_tag", "")
    if not namespace:
        return HttpResponse("You must specify a model to download")
    docs = get_docs(namespace)
    if not docs:
        return HttpResponse("Error, no documents for that schema exist")
    download_id = uuid.uuid4().hex
    schema_export.delay(namespace, download_id)
    return HttpResponseRedirect(reverse('downloader.downloaderviews.retrieve_download', kwargs={'download_id': download_id}))

@login_required()
def export_landing(request, template_name="pactcarehq/export_landing.html"):

    class RequestDownloadForm(forms.Form):
        email_address = forms.CharField(error_messages = {'required':
                                                'You must enter an email'})

    context = RequestContext(request)
    if request.method == "POST":
        form = RequestDownloadForm(data=request.POST)
        if form.is_valid():
            email = form.cleaned_data['email_address']
            download_id = uuid.uuid4().hex
            namespace = "http://dev.commcarehq.org/pact/progress_note"
            context['email'] = email
            context['download_id'] = download_id

            schema_export.delay(namespace, download_id, email=email)

        else:
            context['form'] = form
    else:
        context['form'] = RequestDownloadForm()

    return render_to_response(template_name, context_instance=context)
