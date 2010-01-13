#!/usr/bin/env python
# vim: ai ts=4 sts=4 et sw=4

from django import forms
from django.forms import widgets
from casetracker.models import Case, CaseEvent, CaseAction, Priority, Status, Category
from ashandapp.models import CareTeam
from django.contrib.auth.models import User
from django.forms.util import ErrorList, ValidationError
from datetime import datetime


class CaseCommentForm(forms.Form):    
    comment = forms.CharField(required=True,
                           error_messages = {'required': 'You must enter a comment'},
                           widget = widgets.TextInput(attrs={'cols':70,'rows':5}),                            
                          )
    
    

class CaseModelForm(forms.ModelForm):
    
    EDIT_ASSIGN = 'assign'
    EDIT_MODIFY_ALL = 'edit'
    EDIT_RESOLVE = 'resolve'
    EDIT_CLOSE = 'close'
    EDIT_SET_ACTION = 'set_action'
    EDIT_SET_STATUS = 'status'
    
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
                     'parent_case']
        
        if mode == self.EDIT_MODIFY_ALL:
            all_fields = ('id', 'orig_description', 'resolved_date', 'resolved_by', 'closed_by', 'closed_date', 'last_edit_date', 'last_edit_by', )
        elif mode == self.EDIT_ASSIGN:
            all_fields.remove('assigned_to')        
        elif mode == self.EDIT_RESOLVE:
            all_fields.remove('resolved_by')            
        elif mode == self.EDIT_CLOSE:
            all_fields.remove('closed_by')            
        elif mode == self.EDIT_SET_STATUS:
            all_fields.remove('status')            
        elif mode == self.EDIT_SET_ACTION:
            all_fields.remove('next_action')
            all_fields.remove('next_action_date')            
        
        for field in all_fields:
            try:
                del self.fields[field]
            except:
                pass