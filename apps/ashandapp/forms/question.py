#!/usr/bin/env python
# vim: ai ts=4 sts=4 et sw=4
from datetime import datetime, timedelta
from django import forms
from django.forms import widgets
from casetracker.models import Case, CaseEvent, CaseAction, Priority, Status, Category
from ashandapp.models import CareTeam
from django.contrib.auth.models import User
from django.forms.util import ErrorList, ValidationError
from datetime import datetime

from ashandapp.forms import CareTeamCaseFormBase
from casetracker import constants

from ashandapp.caseregistry.question import CATEGORY_SLUG

class NewQuestionForm(CareTeamCaseFormBase):
    """Initial creation of an question case will be governed by this form"""
    
    description = forms.CharField(label="Subject", 
                                  help_text="For best tracking of questions, make sure that your question has \
                                  one focused subject matter. (required)",
                                  widget = widgets.Textarea(attrs={'cols':100, 'rows':2, 'maxlength':160}))
    body = forms.CharField(label="Message", required=True,
                           help_text="Full message body (required)",
                           error_messages = {'required': 'You must enter a description'},
                           widget = widgets.Textarea(attrs={'cols':100,'rows':10}))    
    
   
    
    def __init__(self, careteam=None, *args, **kwargs):
        super(NewQuestionForm, self).__init__(careteam=careteam,*args, **kwargs)   
           
    def clean(self):
        return self.cleaned_data
    
        
    
    def get_case(self, request):
        if not self.is_valid():
            raise Exception("Error, trying to generate case from question form when form is not valid!")
        newcase = Case()
        newcase.category = Category.objects.get(slug=CATEGORY_SLUG)
        newcase.priority = self.cleaned_data['priority']
        newcase.priority = Priority.objects.get(id=4)
        newcase.opened_by = request.user
        newcase.status = Status.objects.filter(category=newcase.category).filter(state_class=constants.CASE_STATE_OPEN)[0] #get the default opener - this is a bit sketchy
        newcase.description = self.cleaned_data['description']
        newcase.body = self.cleaned_data['body']
        
        newcase.assigned_to = self.cleaned_data['recipient']
#        if self.cleaned_data['recipient'] == 'primary':            
#            if self._careteam.primary_provider:
#                newcase.assigned_to = self._careteam.primary_provider.user
#            else:                        
#                newcase.assigned_to = request.user
#        elif self.cleaned_data['recipient'] == 'specific':            
#            newcase.assigned_to = self.cleaned_data['other_recipient']

        newcase.assigned_date = datetime.utcnow()
                
        #newcase.next_action = CaseAction.objects.get(id=7) #triage                
        td = timedelta(hours=1)
        newcase.next_action_date = datetime.utcnow() + td
        
        return newcase
    
class QuestionResponseForm(forms.Form):
    forms.CharField(required=True, 
                              error_messages = {'required': 
                                                'You must enter a message'}) 
    
    def __init__(self, case, *args, **kwargs):
        
        pass