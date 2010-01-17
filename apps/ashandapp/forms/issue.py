#!/usr/bin/env python
# vim: ai ts=4 sts=4 et sw=4

from django import forms
from casetracker.models import Case, CaseEvent, CaseAction, Priority, Status, Category
from ashandapp.models import CareTeam
from django.contrib.auth.models import User
from django.forms.util import ErrorList, ValidationError
from datetime import datetime
from django.forms import widgets



class NewIssueForm(forms.Form):
    """Initial creation of an inquiry case will be governed by this form"""
    ISSUE_CHOICES = (('caregiver', "Caregiver Concern" ),
                         ('careplan', "Care Plan Issue" ),
                         ('healthmonitor', "Health Monitor" ),
                         ('other', "Other" ),
                         )
    description = forms.CharField(max_length=160,
                                  required=True, 
                              error_messages = {'required': 
                                                'You must enter a short description'})
    body = forms.CharField(required=True,
                           error_messages = {'required': 'You must enter a message body'},
                           widget = widgets.Textarea(attrs={'cols':50,'rows':10}))          
    
    priority = forms.ModelChoiceField(queryset=Priority.objects.all(), required=True,
                                      error_messages = {'required': 'Please select a priority for this inquiry'})    
    
    source = forms.ChoiceField(choices=ISSUE_CHOICES, required=True)
    
    def __init__(self, careteam=None, *args, **kwargs):
        super(NewIssueForm, self).__init__(*args, **kwargs)
        #self.careteam = careteam
        
    
    def clean(self):
        return self.cleaned_data
    
    def get_case(self, request):
        if not self.is_valid():
            raise Exception("Error, trying to generate case from inquiry form when form is not valid!")
        newcase = Case()
        newcase.category = Category.objects.get(category='issue')
        newcase.priority = self.cleaned_data['priority']
        newcase.opened_by = request.user
        newcase.status = Status.objects.filter(category=newcase.category).get(description='Active')
        newcase.description = self.cleaned_data['description']
        newcase.body = self.cleaned_data['body']
        
        return newcase
    
    
class InquiryResponseForm(forms.Form):
    forms.CharField(required=True, 
                              error_messages = {'required': 
                                                'You must enter a message'}) 
    
    def __init__(self, case, *args, **kwargs):
        
        pass