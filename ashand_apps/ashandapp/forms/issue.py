#!/usr/bin/env python
# vim: ai ts=4 sts=4 et sw=4

from datetime import datetime, timedelta
from django import forms
from casetracker.models import Case, Priority, Status, Category
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
                                  widget = widgets.Textarea(attrs={'maxlength':160, 'cols':100, 'rows':2}))
    
    body = forms.CharField(label="Message", required=True,
                           help_text="Please provide some more details on this issue (required)",
                           error_messages = {'required': 'You must enter a description'},
                           widget = widgets.Textarea(attrs={'cols':100,'rows':10}))         
    

#    source = forms.ChoiceField(choices=ISSUE_CHOICES, required=True)
    
    def __init__(self, careteam=None, *args, **kwargs):
        super(NewIssueForm, self).__init__(careteam=careteam, *args, **kwargs)        
    
    def clean(self):
        return self.cleaned_data
    
    def get_case(self, request):
        if not self.is_valid():
            raise Exception("Error, trying to generate case from issue form when form is not valid!")
        
        category = Category.objects.get(category='issue')
        newcase = Case.objects.create_case(category,
                                           Priority.objects.get(id=4),
                                           request.actor, 
                                           self.cleaned_data['description'],
                                           self.cleaned_data['body'],
                                           status=Status.objects.filter(category=category).filter(state_class=constants.CASE_STATE_OPEN)[0],
                                           commit=False)
        
        td = timedelta(hours=1)        
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