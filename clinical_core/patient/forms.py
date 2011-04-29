from django import forms
from django.forms import widgets
from patient.models.couchmodels import CPatient
from patient.models.djangomodels import Patient
from django.core.exceptions import ValidationError

class BasicPatientForm(forms.Form):
    GENDER_CHOICES =(
        ('m', 'Male'),
        ('f', 'Female')
    )


    first_name = forms.CharField(required=True)
    middle_name = forms.CharField()
    last_name = forms.CharField(required=True)
    gender = forms.ChoiceField(choices=GENDER_CHOICES, required=True)
    birthdate = forms.DateField(required=True)




