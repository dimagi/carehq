#!/usr/bin/env python
# vim: ai ts=4 sts=4 et sw=4

from datetime import datetime, timedelta
from django import forms
from casetracker.models import Case, CaseEvent, CaseAction, Priority, Status, Category
from ashandapp.models import CareTeam
from django.contrib.auth.models import User
from django.forms.util import ErrorList, ValidationError
from datetime import datetime
from django.forms import widgets

from casetracker import constants 
from ashandapp.forms import CareTeamCaseFormBase

class NewIssueForm(CareTeamCaseFormBase):
    """Initial creation of an issue case will be governed by this form"""
#    ISSUE_CHOICES = (('caregiver', "Caregiver Concern" ),
#                         ('careplan', "Care Plan Issue" ),
#                         ('healthmonitor', "Health Monitor" ),
#                         ('other', "Other" ),
#                         )
    
    description = forms.CharField(label="Subject", 
                                  help_text="(required)",
                                  widget = widgets.Textarea(attrs={'cols':80, 'rows':1}))
    
    body = forms.CharField(label="Message", required=True,
                           help_text="Please provide some more details on this issue (required)",
                           error_messages = {'required': 'You must enter a description'},
                           widget = widgets.Textarea(attrs={'cols':50,'rows':10}))         
    

#    source = forms.ChoiceField(choices=ISSUE_CHOICES, required=True)
    
    def __init__(self, careteam=None, *args, **kwargs):
        super(NewIssueForm, self).__init__(careteam=careteam, *args, **kwargs)
        
    
    def clean(self):
        return self.cleaned_data
    
    def get_case(self, request):
        if not self.is_valid():
            raise Exception("Error, trying to generate case from issue form when form is not valid!")
        newcase = Case()
        newcase.category = Category.objects.get(category='issue')
        #newcase.priority = self.cleaned_data['priority']
        newcase.priority = Priority.objects.get(id=4)
        newcase.opened_by = request.user
        newcase.status = Status.objects.filter(category=newcase.category).filter(state_class=constants.CASE_STATE_OPEN)[0] #get the default opener - this is a bit sketchy
        newcase.description = self.cleaned_data['description']
        newcase.body = self.cleaned_data['body']
        
        #newcase.next_action = CaseAction.objects.get(id=3) #follow up                
        #td = timedelta(hours=newcase.priority.id)
        #newcase.next_action_date = datetime.utcnow() + td
        
        
        if self._careteam.primary_provider:
            newcase.assigned_to = self._careteam.primary_provider.user
        else:
            newcase.assigned_to = request.user
        newcase.assigned_date = datetime.utcnow()
        
        return newcase
    
    
class IssueResponseForm(forms.Form):
    forms.CharField(required=True, 
                              error_messages = {'required': 
                                                'You must enter a message'}) 
    
    def __init__(self, case, *args, **kwargs):
        
        pass