# Create your views here.
from django.contrib.auth.decorators import permission_required
import json
from django.http import HttpResponseRedirect
from patient.models.couchmodels import CPhone, CAddress
import settings
from django.core.urlresolvers import reverse
from django.shortcuts import render_to_response

def patient_select(request):
    """
    Entry point for patient select/registration workflow
    """
    if request.method == "POST":
        # TODO: handle + redirect
        # {'new': True, 'patient': { <patient_blob> }
        data = json.loads(request.POST.get('result'))
        create_new = data.get("new")
        pat_dict = data.get("patient")

        if not data:
            return HttpResponseRedirect('/')
        elif create_new:

            # Here's an example format:
            # u'patient': {u'dob': u'2000-02-02', u'sex': u'm',
            #              u'lname': u'alskdjf', u'phone': None,
            #              u'fname': u'f8rask', u'village': u'PP'f,
            #              u'dob_est': False, u'id': u'727272727272'}}
            #
            def map_basic_data(pat_dict):
                # let's use the same keys, for now this will have to suffice
                new_dict = {}
                mapping = (("dob",  "birthdate"),
                           ("fname",  "first_name"),
                           ("lname",  "last_name"),
                           ("dob_est",  "birthdate_estimated"),
                           ("sex",  "gender"),
                           ("id",  "patient_id")
                           )
                for oldkey, newkey in mapping:
                    new_dict[newkey] = pat_dict.get(oldkey)
                return new_dict
            clean_data = map_basic_data(pat_dict)
            patient = patient_from_instance(clean_data)
            if pat_dict.get("phone"):
                patient.phones=[CPhone(is_default=True, number=pat_dict["phone"])]
            else:
                patient.phones = []

#            patient.address = CAddress(village=pat_dict.get("village"),
#                                       clinic_id=settings.BHOMA_CLINIC_ID,
#                                       zone=pat_dict.get("chw_zone"),
#                                       zone_empty_reason=pat_dict.get("chw_zone_na"))
#            patient.clinic_ids = [settings.BHOMA_CLINIC_ID,]

            patient.save()
            return HttpResponseRedirect(reverse("single_patient", args=(patient.get_id,)))
        elif pat_dict is not None:
            # we get a real couch patient object in this case
            pat_uid = pat_dict["_id"]
            return HttpResponseRedirect(reverse("single_patient", args=(pat_uid,)))

    return render_to_response(request, "touchscreen.html",
                              {'form': {'name': 'patient reg',
                                        'wfobj': 'wfGetPatient'},
                               'mode': 'workflow',
                               'dynamic_scripts': ["patient/javascripts/patient_reg.js",] })

def render_content (request, template):
    if template == 'single-patient':
        pat_uuid = request.POST.get('uuid')
        patient = loader.get_patient(pat_uuid)
        return render_to_response(request, 'patient/single_patient_block.html', {'patient': patient})
    else:
        #error
        pass