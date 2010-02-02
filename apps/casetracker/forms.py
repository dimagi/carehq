#!/usr/bin/env python
# vim: ai ts=4 sts=4 et sw=4

from django import forms
from django.forms import widgets
from casetracker.models import Case, CaseEvent, CaseAction, Priority, Status, Category, EventActivity
from ashandapp.models import CareTeam
from django.contrib.auth.models import User
from django.forms.util import ErrorList, ValidationError
from datetime import datetime

from casetracker import constants

class CaseCommentForm(forms.Form):    
    comment = forms.CharField(required=True,
                           error_messages = {'required': 'You must enter a comment'},
                           widget = widgets.TextInput(attrs={'cols':70,'rows':5}),                            
                          )
    

class CaseResolveCloseForm(forms.Form):    
    event_activity = forms.ModelChoiceField(queryset=EventActivity.objects.all(), required=True)
    state = forms.ModelChoiceField(queryset = Status.objects.all(), required=True)
    comment = forms.CharField(required=True,
                           error_messages = {'required': 'You must enter a comment'},
                           widget = widgets.TextInput(attrs={'cols':70,'rows':5}),                            
                          )
    
    def __init__(self, case=None, mode=None, *args, **kwargs):
        super(CaseResolveCloseForm, self).__init__(*args, **kwargs)
        
        if mode != constants.CASE_STATE_RESOLVED and mode != constants.CASE_STATE_CLOSED:
            raise Exception("Error, the mode %s being called is invalid!" % (mode))
        
        if case is None:
            raise Exception("Error, you must pass in a valid case to process this form") 
        
        self.fields['state'].queryset = Status.objects.filter(category=case.category).filter(state_class=mode)
        self.fields['event_activity'].queryset = EventActivity.objects.filter(category=case.category).filter(event_class=mode)
        

class CaseModelForm(forms.ModelForm):
    """
    A form to modify a case instance.
    The constants below try to establish a way to flip the active fields depending on the context of how to change it.  The idea here is that not all fields should be presentable to the user.
    """
    
    EDIT_ASSIGN = 'assign'
    EDIT_MODIFY_ALL = 'edit'
    EDIT_SET_ACTION = 'set_action'
    EDIT_RESOLVE = 'resolved_by'
    
        
    description = forms.CharField(widget = widgets.Textarea(attrs={'cols':80, 'rows':1}))
    body = forms.CharField(widget = widgets.Textarea(attrs={'cols':80, 'rows':8}))
    comment = forms.CharField(required=False, widget = widgets.Textarea(attrs={'cols':80, 'rows':4}))                                                         
    
    class Meta:
        model = Case
        #default exclude for basic editing
        exclude = ()
    def __init__(self, editor_user=None, mode=None, * args, **kwargs):      
        super(CaseModelForm, self).__init__(*args, **kwargs)  
        all_fields = [#'id',
                     'description',
                     #'orig_description',
                     'category',
                     'status',
                     'body',
                     'priority',
                     'next_action',
                     'opened_date',
                     'opened_by',
                     'last_edit_by',
                     'last_edit_date',
                     'next_action_date',
                     'resolved_date',
                     'resolved_by',
                     'closed_date',
                     'closed_by',
                     'assigned_to',
                     'assigned_date',
                     'parent_case']
        
        if mode == self.EDIT_MODIFY_ALL:
            all_fields = ('id', 'orig_description', 'resolved_date', 'resolved_by', 'closed_by', 'closed_date', 'last_edit_date', 'last_edit_by', )
        elif mode == self.EDIT_ASSIGN:
            all_fields.remove('assigned_to')        
            #all_fields.remove('assigned_date')
        elif mode == self.EDIT_SET_ACTION:
            all_fields.remove('next_action')
            all_fields.remove('next_action_date')            
        
        for field in all_fields:
            try:
                del self.fields[field]
            except:
                pass