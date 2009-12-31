#!/usr/bin/env python
# vim: ai ts=4 sts=4 et sw=4

from django import forms
from casetracker.models import Case, CaseEvent, CaseAction, Priority, Status
from ashandapp.models import CareTeam
from django.contrib.auth.models import User
from django.forms.util import ErrorList, ValidationError
from datetime import datetime


class NewIssueForm(forms.Form):
    """Initial creation of an inquiry case will be governed by this form"""
    ISSUE_CHOICES = (('caregiver', "Caregiver Concern" ),
                         ('careplan', "Care Plan Issue" ),
                         ('healthmonitor', "Health Monitor" ),
                         ('other', "Other" ),
                         )
    message = forms.CharField(required=True, 
                              error_messages = {'required': 
                                                'You must enter a message'})
    
    priority = forms.ModelChoiceField(queryset=Priority.objects.all(), required=True,
                                      error_messages = {'required': 
                                                'Please select a priority for this inquiry'})    
    source = forms.ChoiceField(choices=ISSUE_CHOICES, required=True)
    
    def __init__(self, careteam=None, *args, **kwargs):
        super(NewIssueForm, self).__init__(*args, **kwargs)
        self.careteam = careteam
        

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