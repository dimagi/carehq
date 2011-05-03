from django import forms
from django.forms.util import ValidationError
from django.forms import widgets

from casetracker import constants
from patient.models import CPhone

class PhoneForm(forms.Form):
    """
    Form to provide for simple editing/commentnig on an inbound progrssnote for PACT
    """
#    PHONE_CHOICES = (
#        ('home', 'Home'),
#        ('mobile', 'Mobile'),
#        ('work', 'Work'),
#        ('relative', 'Relative'),
#        ('health', 'Health Facility'),
#        ('other', 'Other'),
#    )
    description = forms.CharField(required=True)
    number = forms.CharField(required=True)
    notes = forms.CharField(required=False)
