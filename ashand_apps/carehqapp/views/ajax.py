import logging
import urllib
from actorpermission.models import BaseActorDocument
from carehqadmin.forms.actor_form import get_actor_form
from carehqapp.forms.carehq_pt_forms import CarehqPatientForm
from patient.forms.address_form import SimpleAddressForm, FullAddressForm
from patient.forms.phone_form import PhoneForm
from patient.models import  BasePatient, CPhone, CarehqPatient, CAddress
from receiver.util import spoof_submission
from tenant.models import Tenant
from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse
from django.http import  HttpResponse
from django.shortcuts import render_to_response
from django.template.context import RequestContext
from django.views.decorators.http import require_POST

@login_required
@require_POST
def remove_phone(request):
    """
    Remove a casexml phone by injecting a new casexml update block in to the submissions
    """
    resp = HttpResponse()
    try:
        patient_guid = urllib.unquote(request.POST['patient_guid']).encode('ascii', 'ignore')
        pdoc = CarehqPatient.get(patient_guid)
        phone_id = int(urllib.unquote(request.POST['phone_id']).encode('ascii', 'ignore'))
        pdoc.phones.pop(phone_id)
        pdoc.save()
        print "Remove phone: %s" % phone_id
        resp.status_code = 204
    except Exception, e:
        print "error removing phone"
        logging.error("Error getting args:" + str(e))
        print e
        return HttpResponse("Error: %s" % e)
    return resp


@login_required
@require_POST
def remove_address(request):
    """
    Remove a casexml address by injecting a new casexml update block into the submissions
    """
    print request.POST
    resp = HttpResponse()
    try:
        patient_guid = urllib.unquote(request.POST['patient_guid']).encode('ascii', 'ignore')
        pdoc = CarehqPatient.get(patient_guid)
        address_id = int(urllib.unquote(request.POST['address_id']).encode('ascii', 'ignore'))
        pdoc.address.pop(address_id)
        pdoc.save()

        print "Remove address: %s" % address_id
        resp.status_code = 204
    except Exception, e:
        print e
        logging.error("Error getting args:" + str(e))
        raise
    return resp



@login_required
def ajax_get_actor_form(request, template='carehqapp/partials/ajax_actor_form.html'):
    doc_id = request.GET.get('doc_id', None)
    form_name = request.GET.get('form_name', None)
    actor_doc = BaseActorDocument.get_typed_from_id(doc_id)
    context = RequestContext(request)
    context['doc_id'] = doc_id
    context['form_name'] = form_name
    title = ""
    tenant = Tenant.objects.get(name='PACT')
    if form_name == 'chweditprofile':
        form_class = get_actor_form(actor_doc.__class__)
        form = form_class(tenant, instance=actor_doc)
        title = "Edit CHW"
    context['form'] = form
    context['title'] = title
    return render_to_response(template, context_instance=context)

@login_required
@require_POST
def ajax_post_actor_form(request, doc_id, form_name):
    context=RequestContext(request)
    resp = HttpResponse()
    actor_doc = BaseActorDocument.get_typed_from_id(doc_id)
    tenant = Tenant.objects.get(name='ASHand')

    if form_name == 'chweditprofile':
        title = "Edit Profile"
        form_class=get_actor_form(actor_doc.__class__)
        form = form_class(tenant, data=request.POST, instance=actor_doc)
    context['title'] = title
    context['doc_id'] = doc_id
    context['form_name'] = form_name

    if form.is_valid():
        instance = form.save(commit=False)
        instance.save(tenant)
        resp.status_code=204
        return resp
    else:
        context['form']=form
    resp.write(context['form'].as_table())
    return resp


@login_required
def ajax_patient_form_get(request, template='carehqapp/partials/ajax_patient_form.html'):
    patient_guid = request.GET.get('doc_id', None)
    form_name = request.GET.get('form_name', None)
    edit_id = request.GET.get('edit_id', None)
    pdoc = BasePatient.get_typed_from_dict(BasePatient.get_db().get(patient_guid))

    context = RequestContext(request)

    context['patient_guid'] = patient_guid
    context['form_name'] = form_name
    title = "New Form"

    if not edit_id:
        #no edit id, just return a pristine form
        if form_name == 'address':
            form = FullAddressForm()
            title = "New Address"
        elif form_name == 'phone':
            form = PhoneForm()
            title = "New Phone"
        elif form_name == 'ptedit':
            title = "Edit Patient Info"
            form = CarehqPatientForm('edit', instance=pdoc)
            template='carehqapp/partials/ajax_pactpatient_uni_form.html'
    else:
        #this really is only just for phones and addresses
        if form_name == 'address':
            addr = pdoc.address[int(edit_id)]
            form = FullAddressForm(initial=addr.to_json())
            title = "Change Address"
        elif form_name == 'phone':
            p = pdoc.phones[int(edit_id)]
            form = PhoneForm(initial=p.to_json())
            title = "New Phone"


    context['form'] = form
    context['title'] = title
    return render_to_response(template, context_instance=context)




@login_required
@require_POST
def ajax_post_patient_form(request, patient_guid, form_name):
    context=RequestContext(request)
    resp = HttpResponse()
    pdoc = CarehqPatient.get(patient_guid)
    context['patient_guid'] = patient_guid
    context['form_name'] = form_name

    if form_name == 'address':
        title = "New Address"
        #if idx, pull instance and preopoulate
    elif form_name == 'phone':
        title = "New Phone"
    elif form_name == 'ptedit':
        title = "Edit Patient Info"
    context['title'] = title

    if form_name == 'address':
        form = FullAddressForm(data=request.POST)
        if form.is_valid():
            new_address = CAddress()
            address_edit_id = form.cleaned_data['address_id']
            new_address.description = form.cleaned_data['description']
            new_address.street = form.cleaned_data['street']
            new_address.city = form.cleaned_data['city']
            new_address.state = form.cleaned_data['state']
            new_address.postal_code = form.cleaned_data['postal_code']

            if address_edit_id == '':
                is_new_addr=True
            else:
                is_new_addr=False

            addresses = pdoc.address
            if is_new_addr:
                new_address.address_id = len(addresses)
                addresses.append(new_address)
            else:
                print request.POST
                addresses[int(address_edit_id)] = new_address
            pdoc.address = addresses
            pdoc.save()

            resp.status_code = 204
            return resp
        else:
            context['form'] = form
    elif form_name == "phone":
        form = PhoneForm(data=request.POST)
        if form.is_valid():
            inputed_phone = CPhone()
            phone_edit_id = form.cleaned_data['phone_id']
            inputed_phone.number = form.cleaned_data['number']
            inputed_phone.description = form.cleaned_data['description']

            if phone_edit_id == '':
                is_new_phone = True
            else:
                is_new_phone = False

            phones = pdoc.phones
            if is_new_phone:
                inputed_phone.phone_id = len(phones)
                phones.append(inputed_phone)
            else:
                phones[int(phone_edit_id)] = inputed_phone
            pdoc.phones = phones
            pdoc.save()
            resp.status_code = 204
            return resp
        else:
            context['form'] = form
    elif form_name=="ptedit":
        form = CarehqPatientForm('edit', instance=pdoc, data=request.POST)
        if form.is_valid():
            instance = form.save(commit=True)
            resp.status_code=204
            return resp
        else:
            context['form']=form
    resp.write(context['form'].as_table())
    return resp
