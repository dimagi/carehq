#!/usr/bin/env python
# vim: ai ts=4 sts=4 et sw=4

from django import forms
from casetracker.models import Priority
from ashandapp.models import CaregiverLink
from django.forms.util import ValidationError
from django.forms import widgets

from casetracker import constants 

class CareTeamCaseFormBase(forms.Form):
    """
    Base form for Case forms for linking to a careteam
    """  
    RECIPIENT_CHOICES = (('primary', "Care Team Primary" ),                         
                     ('specific', "Specific Care Team member" ),
                     )

    recipient = forms.ChoiceField(choices=RECIPIENT_CHOICES,
                                  label="To", 
                                  required=True)

    #basic fields for a case form
    description = forms.CharField(max_length=160,
                                  required=True, 
                                  
                              error_messages = {'required': 
                                                'You must enter a short description'})
    body = forms.CharField(required=True,
                           help_text="Enter a short description (required)",
                           error_messages = {'required': 'You must enter a message body'},
                           widget = widgets.Textarea(attrs={'cols':80,'rows':10}))         
    

    
 
    
    priority = forms.ModelChoiceField(queryset=Priority.objects.all(), required=True,
                                      initial=Priority.objects.get(id=4), #this is dangerous since priorities are not necessarily linked to IDs
                                      help_text="How important is this? 1-High priority to 7-Low priority (required)",
                                      error_messages = {'required': 'Please select a priority for this issue'})
    
    
    def __init__(self, careteam=None, *args, **kwargs):
        super(CareTeamCaseFormBase, self).__init__(*args, **kwargs)
        if careteam == None:
            raise ValidationError("You must set a careteam to instantiate this form")

        
        self._careteam = careteam
        
        providers_qset = careteam.providers.all().order_by('user__last_name')
        provs = []
        for prov in providers_qset:
            provs.append(("prov-" + prov.id, prov.user.get_full_name() + " - " + prov.job_title))
        
        
        cgives = []
        caregivers_qset = careteam.caregivers.all().order_by('last_name')
        for cgive in caregivers_qset:
            cgives.append(("cg-" + str(cgive.id), "%s - %s" % (cgive.get_full_name(), CaregiverLink.objects.get(careteam=careteam, user=cgive).relationship)))
        

        assignment_choices = [ ('primary','Care Team Primary or Triage Nurse'), 
                                ('Providers',
                                    (tuple(provs))),
                                ('Caregivers',
                                    (tuple(cgives))), ] 
        
        self.fields['recipient'].choices = assignment_choices

            
    
    def clean(self):
        return self.cleaned_data
    
    def clean_recipient(self):
        if self.cleaned_data['recipient'] == 'primary':
            if self._careteam.primary_provider:
                self.cleaned_data['recipient'] = self._careteam.primary_provider.user
            else:
                #ok, if things really break down, let's cascade through the options
                if self._careteam.providers.all().count() > 0: #if no primary, just send it to the first provider
                    self.cleaned_data['recipient'] = self._careteam.providers.all()[0].user
                elif self._careteam.caregivers.all().count() > 0: #
                    self.cleaned_data['recipient'] = self._careteam.caregivers.all()[0]
                else:
                    raise ValidationError("Error, there are no suitable people on this patient's care team to assign a case")
        else:
            #it's someone else
            recipient_str = self.cleaned_data['recipient']
            if recipient_str.startswith('cg-'):
                #it's a caregiver
                cg_id = recipient_str[3:]
                try:
                    self.cleaned_data['recipient'] = self._careteam.caregivers.get(id=cg_id)
                except:
                    raise ValidationError("Error, the form input is now invalid for the recipient choice:  Caregiver ID invalid")
                
            elif recipient_str.startswith('prov-'):
                #it's a provider
                prov_id = recipient_str[5:]
                try:
                    self.cleaned_data['recipient'] = self._careteam.providers.get(id=prov_id).user
                except:
                    raise ValidationError("Error, the form input is now invalid for the recipient choice:  Provider ID invalid")
            else:
                raise ValidationError("Error, the form input is now invalid for the recipient choice")
            
        return self.cleaned_data['recipient']

    
    
    def get_case(self, request):
        raise Exception("This method has not been implemented by the subclass")