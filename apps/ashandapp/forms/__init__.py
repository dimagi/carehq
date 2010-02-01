#!/usr/bin/env python
# vim: ai ts=4 sts=4 et sw=4

from django import forms
from casetracker.models import Case, CaseEvent, CaseAction, Priority, Status, Category
from ashandapp.models import CareTeam
from django.contrib.auth.models import User
from django.forms.util import ErrorList, ValidationError
from datetime import datetime
from django.forms import widgets

from casetracker import constants 

class CareTeamCaseFormBase(forms.Form):
    """
    Base form for Case forms for linking to a careteam
    """  
    
    #basic fields for a case form
    description = forms.CharField(max_length=160,
                                  required=True, 
                              error_messages = {'required': 
                                                'You must enter a short description'})
    body = forms.CharField(required=True,
                           error_messages = {'required': 'You must enter a message body'},
                           widget = widgets.Textarea(attrs={'cols':50,'rows':10}))          
    
    priority = forms.ModelChoiceField(queryset=Priority.objects.all(), required=True,
                                      error_messages = {'required': 'Please select a priority for this issue'})
    
    
    def __init__(self, careteam=None, *args, **kwargs):
        super(CareTeamCaseFormBase, self).__init__(*args, **kwargs)
        if careteam != None:
            self._careteam = careteam    
    
    def clean(self):
        return self.cleaned_data
    
    def get_case(self, request):
        raise Exception("This method has not been implemented by the subclass")