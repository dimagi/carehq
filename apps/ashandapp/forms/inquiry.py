#!/usr/bin/env python
# vim: ai ts=4 sts=4 et sw=4

from django import forms
from casetracker.models import Case, CaseEvent, CaseAction, Priority, Status
from ashandapp.models import CareTeam
from django.contrib.auth.models import User
from django.forms.util import ErrorList, ValidationError
from datetime import datetime


class NewInquiryForm(forms.Form):
    """Initial creation of an inquiry case will be governed by this form"""
    RECIPIENT_CHOICES = (('careteam', "Entire Care Team" ),
                         ('providers', "Just Providers" ),
                         ('caregivers', "Just Caregivers" ),
                         ('specific', "Specific Target" ),
                         )
    message = forms.CharField(required=True, 
                              error_messages = {'required': 
                                                'You must enter a message'})
    
    priority = forms.ModelChoiceField(queryset=Priority.objects.all(), required=True,
                                      error_messages = {'required': 
                                                'Please select a priority for this inquiry'})    
    recipient = forms.ChoiceField(choices=RECIPIENT_CHOICES, required=True)
    other_recipient = forms.ModelChoiceField(queryset=User.objects.all(), required=False)    
    
    def __init__(self, careteam=None, *args, **kwargs):
        super(NewInquiryForm, self).__init__(*args, **kwargs)
        self.careteam = careteam        
        self.fields['other_recipient'].queryset = self.careteam.get_careteam_user_qset()
        

    def clean_message(self):
        pass
    
    def clean(self):
        #check recipient and other_recipient validation     
        pass
    
class InquiryResponseForm(forms.Form):
    forms.CharField(required=True, 
                              error_messages = {'required': 
                                                'You must enter a message'}) 
    
    def __init__(self, case, *args, **kwargs):
        
        pass