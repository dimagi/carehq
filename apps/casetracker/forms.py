#!/usr/bin/env python
# vim: ai ts=4 sts=4 et sw=4

from django import forms
from django.forms import widgets
from casetracker.models import Case, CaseEvent, CaseAction, Priority, Status, Category, EventActivity
from ashandapp.models import CareTeam
from django.contrib.auth.models import User
from django.forms.util import ErrorList, ValidationError
from datetime import datetime
import settings
from django.contrib.admin import widgets as admwidgets                                       


from django.utils.safestring import mark_safe

from casetracker import constants

class CaseCommentForm(forms.Form):    
    comment = forms.CharField(required=True,
                           error_messages = {'required': 'You must enter a comment'},
                           widget = widgets.TextInput(attrs={'cols':70,'rows':5}),                            
                          )
    

class CaseResolveCloseForm(forms.Form):    
    #event_activity = forms.ModelChoiceField(label='Reason', queryset=EventActivity.objects.all(), required=True)
    state = forms.ModelChoiceField(label="Reason", queryset = Status.objects.all(), required=True)
    comment = forms.CharField(required=True,
                           error_messages = {'required': 'You must enter a comment'},
                           widget = widgets.Textarea(attrs={'cols':70,'rows':5}),                            
                          )
    
    def __init__(self, case=None, mode=None, *args, **kwargs):
        super(CaseResolveCloseForm, self).__init__(*args, **kwargs)
        
        if mode != constants.CASE_STATE_RESOLVED and mode != constants.CASE_STATE_CLOSED:
            raise Exception("Error, the mode %s being called is invalid!" % (mode))
        
        if mode == constants.CASE_STATE_RESOLVED:
            self.fields['comment'].help_text='Please enter an explanation for this closure (required)'
        if mode == constants.CASE_STATE_CLOSED:
            self.fields['comment'].help_text='Please enter an explanation for this resolving (required)'

        
        if case is None:
            raise Exception("Error, you must pass in a valid case to process this form") 
        
        self.fields['state'].queryset = Status.objects.filter(category=case.category).filter(state_class=mode)
        #self.fields['event_activity'].queryset = EventActivity.objects.filter(category=case.category)
        

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
        #print self.instance.category  
        fields_to_exclude = ['id',
                     'description',
                     'orig_description',
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
                     'parent_case',
                     ]
        
        if mode == self.EDIT_MODIFY_ALL:
            fields_to_exclude = ['id',
                     'orig_description',
                     'category',
                     'status',
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
                     'parent_case',
                     ]
            self.fields['comment'].help_text = 'Please comment on the changes just made (required)'           
        
        elif mode == self.EDIT_ASSIGN:
            fields_to_exclude.remove('assigned_to')
            fields_to_exclude.remove('next_action_date')
            fields_to_exclude.remove('next_action')
               
            
            self.fields['assigned_to'].label = 'Assign to'             
            #self.fields['next_action'].label = 'Action Requested'
            #self.fields['next_action'].help_text = 'What is the action you ask of this assignment (required)'
            
            self.fields['next_action_date'].label = 'Action Due Date'
            self.fields['next_action_date'].widget = admwidgets.AdminSplitDateTime()
            self.fields['next_action_date'].help_text = 'Set a due date for this requested action (required)'
            
            self.fields['comment'].help_text = 'Please enter a short note'
            
                       
        elif mode == self.EDIT_SET_ACTION:
            fields_to_exclude.remove('next_action')
            fields_to_exclude.remove('next_action_date')            
        
        for field in fields_to_exclude:
            try:
                del self.fields[field]
            except:
                pass
            
        if self.instance:
            #set all the User FK's to use a different choice system as defined by the 
            #categoryhandler
            user_list_choices = self.instance.category.handler.get_user_list_choices(self.instance)
            if user_list_choices:
                if self.fields.has_key('assigned_to'):                
                    self.fields['assigned_to'].choices = user_list_choices
                if self.fields.has_key('resolved_by'):
                    self.fields['resolved_by'].choices = user_list_choices
                if self.fields.has_key('closed_by'):
                    self.fields['closed_by'].choices = user_list_choices
                if self.fields.has_key('opened_by'):
                    self.fields['opened_by'].choices = user_list_choices
                if self.fields.has_key('last_edit_by'):
                    self.fields['last_edit_by'].choices = user_list_choices