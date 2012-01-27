from django import forms

from couchdbkit.ext.django.forms import DocumentForm
#from the models, we have this, (couchmodels.py)
#flipping to tuple
from django.core.exceptions import ValidationError
from pactpatient.enums import REGIMEN_CHOICES, GENDER_CHOICES, PACT_ARM_CHOICES, PACT_LANGUAGE_CHOICES, PACT_HIV_CLINIC_CHOICES, PACT_RACE_CHOICES
from pactpatient.models.pactmodels import PactPatient
from django.forms import widgets
from uni_form.helpers import FormHelper
from uni_form.helpers import Layout, Fieldset, Row
from django.contrib.admin import widgets as admin_widgets

#
#REGIMEN_CHOICES = (
#    ('QD', "QD"),
#    ('BID', "BID"),
#    ('QD-AM', "QD-AM"),
#    ('QD-PM', "QD-PM"),
#    ('TID', "TID"),
#    ('QID', "QID"),
#)
from patient.models import CarehqPatient


YES_OR_NO = (
    (1, 'Yes'),
    (0, 'No')
)

class CarehqPatientForm(DocumentForm):
    """
    DocumentForm
    """
    notes = forms.CharField(widget = widgets.Textarea(attrs={'cols':80,'rows':5}), required=False)
    #source: http://stackoverflow.com/questions/1513502/django-how-to-format-a-datefields-date-representation
    gender = forms.ChoiceField(choices=GENDER_CHOICES)
    preferred_language = forms.ChoiceField(choices=PACT_LANGUAGE_CHOICES)

    def __init__(self, mode, *args, **kwargs):
        super(CarehqPatientForm, self).__init__(*args, **kwargs)
        includes = []
        if mode == "new":
            includes = ['checkin_time',
                        'first_name',
                        'last_name',
                        'middle_name',
                        'available_end',
                        'date_modified',
                        'phones',
                        'notes',
                        'address',
                        'poly_types',
                        'birthdate',
                        'patient_id',
                        'case_id',
                        'start_date',
                        'django_uuid',
                        'gender',
                        'available_start',
                        'base_type',
                        'device_id']
        elif mode == 'edit':
            includes = ['first_name', 'middle_name', 'last_name', 'gender', 'birthdate', 'notes', 'primary_hp', 'arm',
                         'race', 'is_latino', 'preferred_language', 'mass_health_expiration', 'hiv_care_clinic', 'ssn',
                        'art_regimen', 'non_art_regimen',]
        elif mode == "regimen":
            includes = ['art_regimen','non_art_regimen',]
        elif mode == "birthdate":
            includes = ['birthdate',]
        elif mode == "arm":
            includes = ['arm',]
        elif mode == "primaryhp":
            includes = ['primary_hp',]
        elif mode == "notes":
            includes = ['notes',]
        elif mode == "gender":
            includes = ['gender',]
        all_fields = PactPatient._properties.keys()


        for field in all_fields:
            if includes.count(field) > 0:
                continue
            else:
                try:
                    del self.fields[field]
                except Exception, e:
                    pass

    def clean_mass_health_expiration(self):
        if self.cleaned_data['mass_health_expiration'] is None:
            return self.cleaned_data['mass_health_expiration']
        else:
            return self.cleaned_data['mass_health_expiration']

    def clean_pact_id(self):
        if PactPatient.check_pact_id(self.cleaned_data['pact_id']) == False:
            raise ValidationError("Error, pact id must be unique")
        else:
            return self.cleaned_data['pact_id']


    @property
    def helper(self):
        helper = FormHelper()
        helper.form_style="inline"
        # create the layout object
        layout = Layout(
            # first fieldset shows the company
            Fieldset('Basic Info',
                     'pact_id',
                     Row('last_name', 'middle_name', 'first_name'),
                     Row('gender', 'birthdate', 'ssn'),
                     ),

            Fieldset('Demographic Info',
                     Row('race', 'is_latino', 'preferred_language'),
                     ),
            Fieldset('PACT Info',
                     'arm',
                     'primary_hp',
                     'art_regimen',
                     'non_art_regimen',
                     'mass_health_expiration',
                     'hiv_care_clinic',),

                'notes',
        )

        helper.add_layout(layout)
        return helper


    class Meta:
        document = CarehqPatient

#
#    def clean(self):
#        cleaned_data = self.cleaned_data
#        all_null=True
#        for day in days:
#            if cleaned_data.get(day) != None:
#                all_null=False
#                break
#
#        if all_null:
#            raise forms.ValidationError("Error, at least one day must be chosen")
#        # Always return the full collection of cleaned data.
#        return cleaned_data

