from django import forms
from couchdbkit.ext.django.forms import DocumentForm
from pactpatient.enums import  GENDER_CHOICES
from patient.models import CarehqPatient


class BasicPatientForm(DocumentForm):
    birthdate = forms.DateField(input_formats=['%m/%d/%Y'], widget=forms.DateInput(format = '%m/%d/%Y', attrs={'class': 'jqui-dtpk'}))
    gender = forms.ChoiceField(choices=GENDER_CHOICES)
    class Meta:
        document = CarehqPatient

