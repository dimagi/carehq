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
        
        category = Category.objects.get(category='issue')
        status=Status.objects.filter(category=category).filter(state_class=constants.CASE_STATE_OPEN)[0]
        newcase = Case.objects.create_case(category,
                                           Priority.objects.get(id=4),
                                           request.actor, 
                                           self.cleaned_data['description'],
                                           self.cleaned_data['body'],
                                           status = status,
                                           commit=False)
        
        td = timedelta(hours=1)        
        if self._careteam.primary_provider:
            newcase.assigned_to = self._careteam.primary_provider.user
        else:
            newcase.assigned_to = request.user
        newcase.assigned_date = datetime.utcnow()
        
        return newcase
    
class QuestionResponseForm(forms.Form):
    forms.CharField(required=True, 
                              error_messages = {'required': 
                                                'You must enter a message'}) 
    
    def __init__(self, case, *args, **kwargs):
        
        pass