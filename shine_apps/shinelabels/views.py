from django.contrib.auth.decorators import login_required
from django.shortcuts import render_to_response
from django.template.context import RequestContext
from patient.models.patientmodels import BasePatient
from shinelabels.label_form import PrintLabelForm
from shinelabels.models import ZebraPrinter, LabelQueue
from shinelabels.signals import generate_case_barcode

def printer_status(request, template="shinelabels/printer_status.html"):
    printers = ZebraPrinter.objects.all()



@login_required
def print_jobs(request, patient_guid, template_name="shinelabels/printer_jobs.html"):
    """
    Display outstanding jobs for the printer
    """

    context = RequestContext(request)
    context['printform']  = PrintLabelForm()
    context['patient_guid'] = patient_guid
    patient = BasePatient.get_typed_from_dict(BasePatient.get_db().get(patient_guid))


    old_jobs = LabelQueue.objects.all().filter(case_guid = patient.latest_case._id)
    context['jobs'] = old_jobs

    if request.method == "POST":
        form = PrintLabelForm(data=request.POST)
        if form.is_valid():
            num = form.cleaned_data['number']
            printer = form.cleaned_data['printer']
            barcode_zpl = generate_case_barcode(patient.latest_case._id, num=num)
            print barcode_zpl
        else:
            context['printform'] = form
        #submit a new print job
        #request.POST.get('printer_id')
        #request.POST.get('case_id')
        #generate a new print job, generate ZPL, and make a new LabelQueue
        pass
    return render_to_response(template_name, context_instance=context)




