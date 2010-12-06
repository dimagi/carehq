from django import forms
from django.forms.util import ValidationError
from django.forms import widgets

from casetracker import constants
from patient.models.couchmodels import CPhone

class PhoneForm(forms.Form):
    """
    Form to provide for simple editing/commentnig on an inbound progrssnote for PACT
    """
    PHONE_CHOICES = (
        ('home', 'Home'),
        ('mobile', 'Mobile'),
        ('work', 'Work'),
        ('relative', 'Relative'),
        ('health', 'Health Facility'),
        ('other', 'Other'),
    )
    description = forms.ChoiceField(choices=PHONE_CHOICES, required=True)
    number = forms.CharField(required=True)
    notes = forms.CharField()
