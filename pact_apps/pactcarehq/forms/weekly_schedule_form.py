from datetime import datetime
from django import forms
from django.forms.util import ValidationError
from django.forms import widgets

from casetracker import constants
from django.contrib.auth.models import User
days = ['sunday','monday','tuesday','wednesday','thursday','friday','saturday']
hack_pact_usernames = ['-- unassigned --', u'ac381', u'an907', u'ao970', u'cm326', u'cs783', u'godfrey', u'ink', u'ink2', u'isaac', u'lm723', u'lnb9', u'ma651', u'nc903', u'rachel', u'ss524','gj093']



class ScheduleForm(forms.Form):
    """
    Form to provide for simple editing/commentnig on an inbound progrssnote for PACT
    """

    active_date = forms.DateField(help_text="Date this schedule should be made active.  Note active time is 12:01am the day you choose.", required=False, widget=widgets.TextInput(attrs={'class':'activedatepicker'}))
    sunday = forms.ModelChoiceField(User.objects.filter(is_active=True, username__in=hack_pact_usernames), required=False)
    monday = forms.ModelChoiceField(User.objects.filter(is_active=True, username__in=hack_pact_usernames), required=False)
    tuesday = forms.ModelChoiceField(User.objects.filter(is_active=True, username__in=hack_pact_usernames), required=False)
    wednesday = forms.ModelChoiceField(User.objects.filter(is_active=True, username__in=hack_pact_usernames), required=False)
    thursday = forms.ModelChoiceField(User.objects.filter(is_active=True, username__in=hack_pact_usernames), required=False)
    friday = forms.ModelChoiceField(User.objects.filter(is_active=True, username__in=hack_pact_usernames), required=False)
    saturday = forms.ModelChoiceField(User.objects.filter(is_active=True, username__in=hack_pact_usernames), required=False)

    comment = forms.CharField(required=False)


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

