#!/usr/bin/env python
# vim: ai ts=4 sts=4 et sw=4
from couchdbkit.ext.django.forms import DocumentForm

from django import forms
from django.forms import widgets
from django.forms.models import ModelForm, ModelChoiceField
from uni_form.helpers import FormHelper, Layout, Fieldset, Row
from carehq_core import carehq_api
from issuetracker.issue_constants import STATUS_CHOICES, STATUS_RESOLVE_CHOICES, STATUS_CLOSE_CHOICES, PRIORITY_CHOICES
from issuetracker.models import Issue
from issuetracker import issue_constants
from issuetracker.models.issuecore import IssueCategory
from permissions.models import Actor

class CareteamActorIterator(forms.models.ModelChoiceIterator):
    def __init__(self, careteam_dict, *args, **kwargs):
        super(forms.models.ModelChoiceIterator, self).__init__(*args, **kwargs)
        self.careteam_dict = careteam_dict
    def __iter__(self):
        for category, actors in self.careteam_dict.items():
            yield (category.display, [(x.id, x.actordoc.get_name()) for x in actors])
        #yield ('food', [(1L, u'burger'), (2L, u'pizza')])
        #yield ('drinks', [(3L, u'coke'), (4L, u'pepsi')])
        pass


class ActorModelChoiceField(ModelChoiceField):
    def label_from_instance(self, obj):
        return obj.get_full_name()

#class ListMenuOrderForm(forms.ModelForm):
    #def __init__(self, *args, **kwargs):
        #super(ListMenuOrderForm, self).__init__(*args, **kwargs)
        #self.fields['itemWanted'].choices = FooIterator()
    #class Meta:
        #model = PatronOrder


class IssueCommentForm(forms.Form):
    comment = forms.CharField(required=True, label="Update message",
        error_messages = {'required': 'You must enter a comment'},
        widget = widgets.Textarea(attrs={'class':'input-xlarge span12', 'rows':4,})
    )

    

class IssueResolveCloseForm(forms.Form):
    #state = forms.ModelChoiceField(label="Reason", queryset = Status.objects.all(), required=True, widget=widgets.RadioSelect())
    #state = forms.CharField(required=True)
    state=forms.ChoiceField(choices=STATUS_CHOICES)
    comment = forms.CharField(required=True,
                            label="Reason",
                            error_messages = {'required': 'You must enter a comment'},
                            widget = widgets.Textarea(attrs={'class':'input-xlarge span12', 'rows':4})
                          )

    def __init__(self, issue=None, activity=None, *args, **kwargs):
        super(IssueResolveCloseForm, self).__init__(*args, **kwargs)
        event_class = activity

        if event_class == issue_constants.ISSUE_EVENT_RESOLVE:
            state_class = issue_constants.ISSUE_STATE_RESOLVED
            self.fields['comment'].label='Reason for resolving (required)'
            self.fields['state'].choices=STATUS_RESOLVE_CHOICES
        if event_class == issue_constants.ISSUE_EVENT_CLOSE:
            self.fields['comment'].label='Reason for closing (required)'
            state_class = issue_constants.ISSUE_STATE_CLOSED
            self.fields['state'].choices=STATUS_CLOSE_CHOICES

        if issue is None:
            raise Exception("Error, you must pass in a valid issue to process this form")

        #self.fields['state'].choices = [(x.id, x.display.title()) for x in state_qset]

        #Thanks Django documentation to help set the initial value of the RadioSelect widget.
        #oh wait, yeah, THE DOC FOR THIS DOES NOT EXIST!!!
        #self.fields['state'].initial =


class NewIssueForm(ModelForm):
    description = forms.CharField(label="Subject", widget = widgets.Textarea(attrs={'rows':1, 'class':'span6'}))
    body = forms.CharField(label="Message", widget = widgets.Textarea(attrs={'rows':8, 'class':'span6'}))
    priority = forms.CharField(widget=widgets.RadioSelect(choices=PRIORITY_CHOICES, attrs={"style":"list-style-type:none;"}))
    #category = forms.ModelChoiceField(queryset = IssueCategory.objects.all(), widget=widgets.RadioSelect())

    def __init__(self, patient, creator_actor, *args, **kwargs):
        super(NewIssueForm, self).__init__(*args, **kwargs)
        self.patient = patient
        self.creator_actor=creator_actor
        self.fields['assigned_to'].choices = CareteamActorIterator(carehq_api.get_careteam_dict(patient.couchdoc))

    class Meta:
        model=Issue
        exclude = ('id','patient','status','last_edit_date','last_edit_by','closed_date','closed_by','parent_issue','resolved_by','resolved_date', 'opened_date', 'opened_by','assigned_date')

    @property
    def helper(self):
        helper = FormHelper()
        helper.form_style="inline"
        # create the layout object
        layout = Layout(
                    Row('description',css_class="row"),
                    Row('body',css_class="row"),
                    Row('category', css_class="row"),
                    Row('priority', css_class="row"),
                    Row('assigned_to', css_class="row"),
                    Row('due_date', css_class="row"),
            )


        helper.add_layout(layout)
        return helper


class IssueModelForm(ModelForm):
    """
    A form to modify a issue instance.
    The constants below try to establish a way to flip the active fields depending on the context of how to change it.  The idea here is that not all fields should be presentable to the user.
    """
        
    description = forms.CharField(widget = widgets.Textarea(attrs={'cols':80, 'rows':1}))
    body = forms.CharField(widget = widgets.Textarea(attrs={'cols':80, 'rows':8}))
    comment = forms.CharField(required=False, label="Reason",
#        widget = widgets.Textarea(attrs={'cols':80, 'rows':4})
        widget = widgets.Textarea(attrs={'class':'input-xlarge span12', 'rows':4})
    )
    
    class Meta:
        model = Issue
        #default exclude for basic editing
        exclude=()
    def __init__(self, editor_actor=None, activity=None, * args, **kwargs):
        super(IssueModelForm, self).__init__(*args, **kwargs)
        self.editor_actor = editor_actor
        self.activity = activity
        instance = kwargs.get('instance', None)
        if instance is not None:
            if instance.patient is not None:
                self.fields['assigned_to'].choices = CareteamActorIterator(carehq_api.get_careteam_dict(instance.patient.couchdoc))
        #event_class = activity.event_class

        
        #These are all the fields in this modelform, both the newly added ones and the ones
        #within the issue model.
        #To make the display different depending on the activity, pare down the exclusion list
        #and then the form will display the fields you remove from the exclusion list.
        fields_to_exclude = ['id',
                             'patient',
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
                     'parent_issue',
                     'due_date',
                     ]


        if self.activity == issue_constants.ISSUE_EVENT_EDIT:
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
                                 'parent_issue',
                                 ]
            self.fields['comment'].help_text = 'Please comment on the changes just made (required)'

        elif self.activity == issue_constants.ISSUE_EVENT_ASSIGN:
            fields_to_exclude.remove('assigned_to')
            self.fields['assigned_to'].label = 'Assign to'
            self.fields['comment'].help_text = 'Please enter a short note'
        for field in fields_to_exclude:
            try:
                del self.fields[field]
            except:
                pass
            
        if self.instance:
            user_list_choices = Actor.objects.all()
            if user_list_choices:
                if self.fields.has_key('assigned_to'):                
                    self.fields['assigned_to'].queryset = user_list_choices
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
        Do a default clean and validation, but then set other properties on the issue instance before it's saved.
        """
        super(IssueModelForm, self).clean()
        return self.cleaned_data