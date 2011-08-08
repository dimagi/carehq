#!/usr/bin/env python
# vim: ai ts=4 sts=4 et sw=4
from couchdbkit.ext.django.forms import DocumentForm

from django import forms
from django.forms import widgets
from django.forms.models import ModelForm
from casetracker.models import Case
from casetracker import constants

class CaseCommentForm(forms.Form):    
    comment = forms.CharField(required=True,
                           error_messages = {'required': 'You must enter a comment'},
                           widget = widgets.Textarea(attrs={'cols':80,'rows':5}),                            
                          )
    

class CaseResolveCloseForm(forms.Form):
    #state = forms.ModelChoiceField(label="Reason", queryset = Status.objects.all(), required=True, widget=widgets.RadioSelect())
    state = forms.CharField(required=True)
    comment = forms.CharField(required=True,
                            label="Note",
                           error_messages = {'required': 'You must enter a comment'},
                           widget = widgets.Textarea(attrs={'cols':80,'rows':5}),
                          )

    def __init__(self, case=None, activity=None, *args, **kwargs):
        super(CaseResolveCloseForm, self).__init__(*args, **kwargs)
        event_class = activity.event_class

        if event_class == constants.CASE_EVENT_RESOLVE:
            state_class = constants.CASE_STATE_RESOLVED
            self.fields['comment'].help_text='Please enter an explanation for this resolving (required)'
        if event_class == constants.CASE_EVENT_CLOSE:
            self.fields['comment'].help_text='Please enter an explanation for this closure (required)'
            state_class = constants.CASE_STATE_CLOSED

        if case is None:
            raise Exception("Error, you must pass in a valid case to process this form")

        #self.fields['state'].choices = [(x.id, x.display.title()) for x in state_qset]

        #Thanks Django documentation to help set the initial value of the RadioSelect widget.
        #oh wait, yeah, THE DOC FOR THIS DOES NOT EXIST!!!
        self.fields['state'].initial = state_qset[0].id
        

class CaseModelForm(ModelForm):
    """
    A form to modify a case instance.
    The constants below try to establish a way to flip the active fields depending on the context of how to change it.  The idea here is that not all fields should be presentable to the user.
    """
        
    description = forms.CharField(widget = widgets.Textarea(attrs={'cols':80, 'rows':1}))
    body = forms.CharField(widget = widgets.Textarea(attrs={'cols':80, 'rows':8}))
    comment = forms.CharField(required=False, label="Reason", widget = widgets.Textarea(attrs={'cols':80, 'rows':4}))    
    
    class Meta:
        model = Case
        #default exclude for basic editing
        exclude = ()
    def __init__(self, editor_user=None, activity=None, * args, **kwargs):      
        super(CaseModelForm, self).__init__(*args, **kwargs)
        self.editor_user = editor_user
        self.activity = activity
        #event_class = activity.event_class
        
        
        #These are all the fields in this modelform, both the newly added ones and the ones
        #within the case model.
        #To make the display different depending on the activity, pare down the exclusion list
        #and then the form will display the fields you remove from the exclusion list.
        fields_to_exclude = ['id',
                     'description',
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
        
        if self.activity == constants.CASE_EVENT_EDIT:
            fields_to_exclude = ['id',
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
        
        elif self.activity == constants.CASE_EVENT_ASSIGN:
            fields_to_exclude.remove('assigned_to')            
            self.fields['assigned_to'].label = 'Assign to'            
            self.fields['comment'].help_text = 'Please enter a short note'                       
        
        for field in fields_to_exclude:
            try:
                del self.fields[field]
            except:
                pass
            
        if self.instance:
            #set all the User FK's to use a different choice system as defined by the Category Bridge class
            #else, it'll default to ALL users in the system.    
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
                    
                    
    def clean(self):
        """
        Do a default clean and validation, but then set other properties on the case instance before it's saved.
        """
        super(CaseModelForm, self).clean()        
        return self.cleaned_data