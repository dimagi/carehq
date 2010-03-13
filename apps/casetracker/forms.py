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
    state = forms.ModelChoiceField(label="Reason", queryset = Status.objects.all(), required=True)
    comment = forms.CharField(required=True,
                           error_messages = {'required': 'You must enter a comment'},
                           widget = widgets.Textarea(attrs={'cols':70,'rows':5}),                            
                          )
    
    def __init__(self, case=None, activity=None, *args, **kwargs):
        super(CaseResolveCloseForm, self).__init__(*args, **kwargs)
        event_class = activity.event_class
        
        if event_class != constants.CASE_STATE_RESOLVED and event_class != constants.CASE_STATE_CLOSED:
            raise Exception("Error, the event_class %s being called is invalid!" % (event_class))        
        if event_class == constants.CASE_STATE_RESOLVED:
            self.fields['comment'].help_text='Please enter an explanation for this closure (required)'
        if event_class == constants.CASE_STATE_CLOSED:
            self.fields['comment'].help_text='Please enter an explanation for this resolving (required)'
        
        if case is None:
            raise Exception("Error, you must pass in a valid case to process this form") 
        
        self.fields['state'].queryset = Status.objects.filter(category=case.category).filter(state_class=event_class)        
        

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
    def __init__(self, editor_user=None, activity=None, * args, **kwargs):      
        super(CaseModelForm, self).__init__(*args, **kwargs)
        #print self.instance.category
        event_activity = activity
        event_class = activity.event_class
          
        fields_to_exclude = ['id',
                     'description',
                     'orig_description',
                     'category',
                     'status',
                     'body',
                     'priority',
                     'opened_date',
                     'opened_by',
                     'last_edit_by',
                     'last_edit_date',
                     'resolved_date',
                     'resolved_by',
                     'closed_date',
                     'closed_by',
                     'assigned_to',
                     'assigned_date',
                     'parent_case',
                     ]
        
        if event_class == self.EDIT_MODIFY_ALL:
            fields_to_exclude = ['id',
                     'orig_description',
                     'category',
                     'status',
                     'opened_date',
                     'opened_by',
                     'last_edit_by',
                     'last_edit_date',
                     'resolved_date',
                     'resolved_by',
                     'closed_date',
                     'closed_by',
                     'assigned_to',
                     'assigned_date',
                     'parent_case',
                     ]
            self.fields['comment'].help_text = 'Please comment on the changes just made (required)'           
        
        elif event_class == self.EDIT_ASSIGN:
            fields_to_exclude.remove('assigned_to')   
            
            self.fields['assigned_to'].label = 'Assign to'             
            
            self.fields['comment'].help_text = 'Please enter a short note'
            
                       
        elif event_class == self.EDIT_SET_ACTION:
            pass            
        
        for field in fields_to_exclude:
            try:
                del self.fields[field]
            except:
                pass
            
        if self.instance:
            #set all the User FK's to use a different choice system as defined by the 
    
            user_list_choices = self.instance.category.bridge.get_user_list_choices(self.instance)
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
                    
                    
    def clean(self):
        """
        Do a default clean and validation, but then set other properties on the case instance before it's saved.
        """
        super(CaseModelForm, self).clean()
        #self.instance.edit_comment = '' #set the property to modify                                        
        if self.cleaned_data.has_key('comment') and self.cleaned_data['comment'] != '':
            self.instance.edit_comment = self.cleaned_data["comment"]
        self.instance.last_edit_by = self.editor_user
                            
        #next, we need to see the mode and flip the fields depending on who does what.
        if self.activity.event_class == constants.CASE_EVENT_ASSIGN:
            self.instance.assigned_date = datetime.utcnow()
            self.instance.assigned_by = self.editor_user            
            self.instance.edit_comment += " (Assigned to %s by %s)" % (self.instance.assigned_to.get_full_name(), self.editor_user.get_full_name())
            
            if self.instance.status.state_class == constants.CASE_STATE_NEW:
                #This is admittedly nasty because there could be different ways of state openement                
                self.instance.status = Status.objects.filter(category=self.instance.category).filter(state_class=constants.CASE_STATE_OPEN)[0]
        self.instance.event_activity = self.activity
        return self.cleaned_data