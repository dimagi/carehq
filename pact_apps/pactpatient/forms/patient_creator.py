from django.core.exceptions import ValidationError
from pactpatient.models.pactmodels import PactPatient
from patient.forms import BasicPatientForm
from django import forms

REGIMEN_CHOICES = (
        ('None', '-- No Regimen --'),
        ('QD', 'QD - Once a day'),
        ('BID', 'BID - Twice a day'),
        ('QD-AM', 'QD - Once a day (Morning)'),
        ('QD-PM', 'QD - Once a day (Evening)'),
        ('TID', 'TID - Three times a day'),
        ('QID', 'QID - Four times a day'),
    )


class NewPactPatientForm(BasicPatientForm):
    PACT_ARM_CHOICES = (
        ('HP', 'HP - Health Promoter'),
        ('DOT', 'DOT - Directly Observed Therapy'),
        ('Discharged', 'Discharged'),
        #todo: more choices
    )

    PACT_RACE_CHOICES = ()
    PACT_LANGUAGE_CHOICES = ()
    PACT_HIV_CLINIC_CHOICES = ()

    pact_id = forms.CharField(required=True, label="PACT ID")
    arm = forms.ChoiceField(choices=PACT_ARM_CHOICES, required=True)
    art_regimen = forms.ChoiceField(choices=REGIMEN_CHOICES)
    non_art_regimen = forms.ChoiceField(choices=REGIMEN_CHOICES)

    race = forms.ChoiceField(choices=PACT_RACE_CHOICES, required=True)
    is_latino = forms.BooleanField()
    preferred_language = forms.ChoiceField(choices=PACT_LANGUAGE_CHOICES)
    mass_health_expiration = forms.DateField()
    hiv_care_clinic = forms.ChoiceField(choices=PACT_HIV_CLINIC_CHOICES)
    ssn = forms.CharField()

    def clean_pact_id(self):
        if PactPatient.check_pact_id(self.cleaned_data['pact_id']) == False:
            raise ValidationError("Error, pact id must be unique")
        else:
            return self.cleaned_data['pact_id']
    primary_hp = forms.CharField(required=True)
