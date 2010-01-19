#!/usr/bin/env python
# vim: ai ts=4 sts=4 et sw=4

from django import forms
from django.forms import widgets
from casetracker.models import Case, CaseEvent, CaseAction, Priority, Status, Category
from ashandapp.models import CareTeam
from django.contrib.auth.models import User
from django.forms.util import ErrorList, ValidationError
from datetime import datetime


class NewQuestionForm(forms.Form):
    """Initial creation of an question case will be governed by this form"""
    RECIPIENT_CHOICES = (('careteam', "Entire Care Team" ),
                         ('providers', "Just Providers" ),
                         ('caregivers', "Just Caregivers" ),
                         ('specific', "Specific Target" ),
                         )
    description = forms.CharField(max_length=160,
                              required = True, 
                              error_messages = {'required': 
                                                'You must enter a message'})
    
    body = forms.CharField(required=True,
                           error_messages = {'required': 'You must enter a message'},
                           widget = widgets.Textarea(attrs={'cols':50,'rows':10}),                            
                          )
    
    priority = forms.ModelChoiceField(queryset=Priority.objects.all(), required=True,
                                      error_messages = {'required': 'Please select a priority for this question'})    
    
    recipient = forms.ChoiceField(choices=RECIPIENT_CHOICES, required=True)
    other_recipient = forms.ModelChoiceField(queryset=User.objects.all(), required=False)    
    
    def __init__(self, careteam=None, *args, **kwargs):
        super(NewQuestionForm, self).__init__(*args, **kwargs)                
        if careteam != None:
            self.fields['other_recipient'].queryset = careteam.get_careteam_user_qset()
        
   
    def clean(self):
        return self.cleaned_data
    
    def get_case(self, request):
        if not self.is_valid():
            raise Exception("Error, trying to generate case from question form when form is not valid!")
        newcase = Case()
        newcase.category = Category.objects.get(category='question')
        newcase.priority = self.cleaned_data['priority']
        newcase.opened_by = request.user
        newcase.status = Status.objects.filter(category=newcase.category).get(description='Active')
        newcase.description = self.cleaned_data['description']
        newcase.body = self.cleaned_data['body']
        
        return newcase
    
class QuestionResponseForm(forms.Form):
    forms.CharField(required=True, 
                              error_messages = {'required': 
                                                'You must enter a message'}) 
    
    def __init__(self, case, *args, **kwargs):
        
        pass