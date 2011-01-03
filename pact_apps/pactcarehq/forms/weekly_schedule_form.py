from django import forms
from django.forms.util import ValidationError
from django.forms import widgets

from casetracker import constants
from django.contrib.auth.models import User
days = ['sunday','monday','tuesday','wednesday','thursday','friday','saturday']
hack_pact_usernames = [u'godfrey', u'ac381', u'isaac', u'cm326', u'ss524', u'lm723', u'an907', u'ink2', u'lnb9', u'ao970', u'cs783', u'ma651', u'nc903', u'ink',u'rachel']


class ScheduleForm(forms.Form):
    """
    Form to provide for simple editing/commentnig on an inbound progrssnote for PACT
    """
    
    sunday = forms.ModelChoiceField(User.objects.filter(is_active=True, username__in=hack_pact_usernames), required=False)
    monday = forms.ModelChoiceField(User.objects.filter(is_active=True, username__in=hack_pact_usernames), required=False)
    tuesday = forms.ModelChoiceField(User.objects.filter(is_active=True, username__in=hack_pact_usernames), required=False)
    wednesday = forms.ModelChoiceField(User.objects.filter(is_active=True, username__in=hack_pact_usernames), required=False)
    thursday = forms.ModelChoiceField(User.objects.filter(is_active=True, username__in=hack_pact_usernames), required=False)
    friday = forms.ModelChoiceField(User.objects.filter(is_active=True, username__in=hack_pact_usernames), required=False)
    saturday = forms.ModelChoiceField(User.objects.filter(is_active=True, username__in=hack_pact_usernames), required=False)
    comment = forms.CharField( required=False)

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

