#!/usr/bin/env python
# vim: ai ts=4 sts=4 et sw=4

from django import forms
from django.forms import widgets
from casetracker.models import Case, CaseEvent, CaseAction, Priority, Status, Category
from ashandapp.models import CareTeam
from django.contrib.auth.models import User
from django.forms.util import ErrorList, ValidationError
from datetime import datetime


class NewQuestionForm(forms.ModelForm):
    """Initial creation of an question case will be governed by this form"""
    RECIPIENT_CHOICES = (('primary', "Care Team Primary" ),                         
                         ('specific', "Specific Care Team member" ),
                         )
    description = forms.CharField(max_length=160,
                              required = True, 
                              error_messages = {'required': 
                                                'You must enter a short description'})
    
    body = forms.CharField(required=True,
                           error_messages = {'required': 'You must enter a message body'},
                           widget = widgets.Textarea(attrs={'cols':50,'rows':10}),                            
                          )
    
    priority = forms.ModelChoiceField(queryset=Priority.objects.all(), required=True,
                                      error_messages = {'required': 'Please select a priority for this question'})    
    
    recipient = forms.ChoiceField(choices=RECIPIENT_CHOICES, required=True)
    other_recipient = forms.ModelChoiceField(queryset=User.objects.all(), required=False)    
    
    def __init__(self, careteam=None, *args, **kwargs):
        super(NewQuestionForm, self).__init__(*args, **kwargs)          
        if careteam != None:
            self._careteam = careteam
            self.fields['other_recipient'].queryset = careteam.get_careteam_user_qset()
        
   
    def clean(self):
        return self.cleaned_data
    
    def clean_other_recipient(self):
        if self.cleaned_data['recipient'] == 'specific':
            if self.cleaned_data.has_key('other_recipient'):
                return self.cleaned_data['other_recipient']
            else:
                raise ValidationError(message="Please choose a specific CareTeam member to target")
                
        else:
            return self.cleaned_data['recipient']
            
        
    
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
        
        if self.cleaned_data['recipient'] == 'primary':            
            newcase.assigned_to = self._careteam.primary_provider
        elif self.cleaned_data['recipient'] == 'specific':            
            newcase.assigned_to = self.cleaned_data['other_recipient']
                    
        newcase.assigned_date = datetime.utcnow()
        
        
        return newcase
    
class QuestionResponseForm(forms.Form):
    forms.CharField(required=True, 
                              error_messages = {'required': 
                                                'You must enter a message'}) 
    
    def __init__(self, case, *args, **kwargs):
        
        pass