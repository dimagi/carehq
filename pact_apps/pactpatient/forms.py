from django.core.exceptions import ValidationError
from patient.forms import BasicPatientForm
from patient.models.couchmodels import CPatient

class PactPatientForm(BasicPatientForm):
    PACT_ARM_CHOICES = (
        ('HP', 'HP - Health Promoter'),
        ('DOT', 'DOT - Directly Observed Therapy'),
        ('Discharged', 'Discharged'),
    )
    REGIMEN_CHOICES = (
        (None, '-- None --'),
        ('qd', 'QD - Once a day'),
        ('bid', 'BID - Twice a day'),
        ('qd-am', 'QD - Once a day (Morning)'),
        ('qd-pm', 'QD - Once a day (Evening)'),
        ('tid', 'TID - Three times a day'),
        ('qid', 'QID - Four times a day'),
    )
    pact_id = forms.CharField(required=True, label="PACT ID")
    arm = forms.ChoiceField(choices=PACT_ARM_CHOICES, required=True)
    art_regimen = forms.ChoiceField(choices=REGIMEN_CHOICES)
    non_art_regimen = forms.ChoiceField(choices=REGIMEN_CHOICES)

    def clean_pact_id(self):
        if CPatient.is_pact_id_unique(self.cleaned_data['pact_id']) == False:
            raise ValidationError("Error, pact id must be unique")
        else:
            return self.cleaned_data['pact_id']
    primary_hp = forms.CharField(required=True) #this is the sketchy, hacky way in which we link patients to providers for pact pilot
