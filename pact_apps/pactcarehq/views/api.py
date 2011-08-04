import urllib
from pactcarehq.forms.weekly_schedule_form import ScheduleForm
from pactpatient.forms.address_form import SimpleAddressForm
from pactpatient.forms.patient_form import PactPatientForm
from pactpatient.forms.phone_form import PhoneForm
from pactpatient.updater import update_patient_casexml
from patient.models.patientmodels import  BasePatient
from receiver.util import spoof_submission
from .util import DAYS_OF_WEEK
from datetime import datetime, time
from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect, HttpResponse
from django.shortcuts import render_to_response
from django.template.context import RequestContext
from django.views.decorators.http import require_POST
import logging
from pactpatient.models.pactmodels import PactPatient, CDotWeeklySchedule
from patient.models.patientmodels import  Patient

@login_required
@require_POST
def remove_phone(request):
    resp = HttpResponse()
    try:
        patient_guid = urllib.unquote(request.POST['patient_guid']).encode('ascii', 'ignore')
        pdoc = PactPatient.get(patient_guid)
        phone_id = int(urllib.unquote(request.POST['phone_id']).encode('ascii', 'ignore'))
        new_phones = pdoc.active_phones
        new_phones[phone_id] = {'phone':'', 'description': ''}

        xml_body = update_patient_casexml(request.user, pdoc, new_phones, pdoc.active_addresses)
        spoof_submission(reverse("receiver.views.post"), xml_body, hqsubmission=False)
        resp.status_code = 204
    except Exception, e:
        logging.error("Error getting args:" + str(e))
        #return HttpResponse("Error: %s" % (e))
    return resp



@login_required
@require_POST
def remove_address(request):
    resp = HttpResponse()
    try:
        patient_guid = urllib.unquote(request.POST['patient_guid']).encode('ascii', 'ignore')
        pdoc = PactPatient.get(patient_guid)
        address_id = int(urllib.unquote(request.POST['address_id']).encode('ascii', 'ignore'))
        new_addrs = pdoc.active_addresses
        new_addrs[address_id] = {'address': '', 'description': ''}
#        new_addrs.pop(address_id)

        xml_body = update_patient_casexml(request.user, pdoc, pdoc.active_phones, new_addrs)
        spoof_submission(reverse("receiver.views.post"), xml_body, hqsubmission=False)
        resp.status_code = 204
    except Exception, e:
        logging.error("Error getting args:" + str(e))
        raise
    return resp


@login_required
def ajax_get_form(request, template='pactcarehq/partials/ajax_form.html'):
    patient_guid = request.GET.get('patient_guid', None)
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
            form = SimpleAddressForm()
            title = "New Address"
        elif form_name == 'phone':
            form = PhoneForm()
            title = "New Phone"
        elif form_name == 'schedule':
            form = ScheduleForm()
            title = "New Schedule"
        elif form_name == 'ptedit':
            title = "Edit Patient Info"
            form = PactPatientForm('edit', instance=pdoc)
            template='pactcarehq/partials/ajax_pactpatient_uni_form.html'
    else:
        #this really is only just for phones and addresses
        if form_name == 'address':
            addr = pdoc.active_addresses[int(edit_id)]
            form = SimpleAddressForm(initial=addr)
            title = "Change Address"
        elif form_name == 'phone':
            p = pdoc.active_phones[int(edit_id)]
            form = PhoneForm(initial=p)
            title = "New Phone"


    context['form'] = form
    context['title'] = title
    return render_to_response(template, context_instance=context)

@login_required
@require_POST
def ajax_post_form(request, patient_guid, form_name):
    context=RequestContext(request)
    resp = HttpResponse()
    pdoc = PactPatient.get(patient_guid)
    context['patient_guid'] = patient_guid
    context['form_name'] = form_name

    if form_name == 'address':
        title = "New Address"
        #if idx, pull instance and preopoulate
    elif form_name == 'phone':
        title = "New Phone"
    elif form_name == 'schedule':
        title = "New Schedule"
    elif form_name == 'ptedit':
        title = "Edit Patient Info"
    context['title'] = title

    if form_name == "schedule":
        form = ScheduleForm(data=request.POST)
        if form.is_valid():
            sched = CDotWeeklySchedule()
            for day in DAYS_OF_WEEK:
                if form.cleaned_data[day] != None:
                    setattr(sched, day, form.cleaned_data[day].username)
            if form.cleaned_data['active_date'] == None:
                sched.started=datetime.utcnow()
            else:
                sched.started = datetime.combine(form.cleaned_data['active_date'], time.min)
            sched.comment=form.cleaned_data['comment']
            sched.created_by = request.user.username
            sched.deprecated=False
            pdoc.set_schedule(sched)
            resp.status_code = 204
            return resp
        else:
            context['form'] = form
    elif form_name == 'address':
        form = SimpleAddressForm(data=request.POST)
        if form.is_valid():
            addr_dict = {}
            address_edit_id = form.cleaned_data['address_id']
            addr_dict['description'] = form.cleaned_data['description']
            addr_dict['address'] = form.cleaned_data['address']

            if address_edit_id == '':
                is_new_addr=True
            else:
                is_new_addr=False

            active_addresses = pdoc.active_addresses
            if is_new_addr:
                active_addresses.append(addr_dict)
            else:
                active_addresses[int(address_edit_id)-1] = addr_dict

            xml_body = update_patient_casexml(request.user, pdoc, pdoc.active_phones, active_addresses)
            spoof_submission(reverse("receiver.views.post"), xml_body, hqsubmission=False)
            print xml_body

            resp.status_code = 204
            return resp
        else:
            context['form'] = form
    elif form_name == "phone":
        form = PhoneForm(data=request.POST)
        if form.is_valid():
            new_phone = CPhone()
            phone_dict = {}
            phone_edit_id = form.cleaned_data['phone_id']
            phone_dict['number'] = form.cleaned_data['number']
            phone_dict['description'] = form.cleaned_data['description']

            if phone_edit_id == '':
                is_new_phone = True
            else:
                is_new_phone = False

            active_phones = pdoc.active_phones
            if is_new_phone:
                active_phones.append(phone_dict)
            else:
                active_phones[int(phone_edit_id)-1] = phone_dict

            xml_body = update_patient_casexml(request.user, pdoc, active_phones, pdoc.active_addresses)
            spoof_submission(reverse("receiver.views.post"), xml_body, hqsubmission=False)
            resp.status_code = 204
            return resp
        else:
            context['form'] = form
    elif form_name=="ptedit":
        form = PactPatientForm('edit', instance=pdoc, data=request.POST)
        if form.is_valid():
            instance = form.save(commit=True)
            resp.status_code=204
            return resp
        else:
            context['form']=form
    resp.write(context['form'].as_table())
    return resp

@login_required
def remove_schedule(request):
    if request.method == "POST":
        try:
            patient_id = urllib.unquote(request.POST['patient_id']).encode('ascii', 'ignore')
            patient = Patient.objects.get(id=patient_id)
            schedule_id = urllib.unquote(request.POST['schedule_id']).encode('ascii', 'ignore')
            remove_id = -1
            for i in range(0, len(patient.couchdoc.weekly_schedule)):
                sched = patient.couchdoc.weekly_schedule[i]
                if sched.schedule_id == schedule_id:
                    remove_id = i
                    break

            new_schedules = []
            couchdoc = patient.couchdoc
            if remove_id != -1:
                #note the idiocy of me needing to iterate through the list in order to delete it.
                #a simple remove() or a pop(i) could not work for some reason
                for i in range(0, len(couchdoc.weekly_schedule)):
                    if i == remove_id:
                        continue
                    new_schedules.append(couchdoc.weekly_schedule[i])

                couchdoc.weekly_schedule = new_schedules
                couchdoc.save()
            return HttpResponseRedirect(reverse('view_pactpatient', kwargs={'patient_guid':patient_id}))
        except Exception, e:
            logging.error("Error getting args:" + str(e))
            return HttpResponse("Error: %s" % (e))
    else:
        pass

