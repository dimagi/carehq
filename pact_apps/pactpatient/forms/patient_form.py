from django import forms

from couchdbkit.ext.django.forms import DocumentForm
#from the models, we have this, (couchmodels.py)
#flipping to tuple
from django.core.exceptions import ValidationError
from pactpatient.enums import REGIMEN_CHOICES, GENDER_CHOICES, PACT_ARM_CHOICES, PACT_LANGUAGE_CHOICES, PACT_HIV_CLINIC_CHOICES, PACT_RACE_CHOICES
from pactpatient.models.pactmodels import PactPatient
from django.forms import widgets
from pactconfig.constants import hack_pact_usernames
from uni_form.helpers import FormHelper
from uni_form.helpers import Layout, Fieldset, Row

#
#REGIMEN_CHOICES = (
#    ('QD', "QD"),
#    ('BID', "BID"),
#    ('QD-AM', "QD-AM"),
#    ('QD-PM', "QD-PM"),
#    ('TID', "TID"),
#    ('QID', "QID"),
#)




YES_OR_NO = (
    (1, 'Yes'),
    (0, 'No')
)



class PactPatientForm(DocumentForm):
    """
    DocumentForm
    """
    arm = forms.ChoiceField(label="PACT ARM", choices=PACT_ARM_CHOICES)
    art_regimen = forms.ChoiceField(choices=REGIMEN_CHOICES)
    non_art_regimen = forms.ChoiceField(choices=REGIMEN_CHOICES)
#    primary_hp = forms.ModelChoiceField(User.objects.filter(is_active=True, username__in=hack_pact_usernames), required=False)
    primary_hp = forms.ChoiceField(label="Primary health promoter", choices=tuple([(x, x) for x in hack_pact_usernames]))
    notes = forms.CharField(widget = widgets.Textarea(attrs={'cols':80,'rows':5}), required=False)
    #source: http://stackoverflow.com/questions/1513502/django-how-to-format-a-datefields-date-representation
    birthdate = forms.DateField(input_formats=['%m/%d/%Y'], widget=forms.DateInput(format = '%m/%d/%Y', attrs={'class': 'jqui-dtpk'}))
    gender = forms.ChoiceField(choices=GENDER_CHOICES)


    race = forms.ChoiceField(choices=PACT_RACE_CHOICES)
    hiv_care_clinic = forms.ChoiceField(choices=PACT_HIV_CLINIC_CHOICES)
    preferred_language = forms.ChoiceField(choices=PACT_LANGUAGE_CHOICES)

    mass_health_expiration = forms.DateField(label = "Mass Health expiration Date", input_formats=['%m/%d/%Y',''], widget=forms.DateInput(format = '%m/%d/%Y'), required=False)
    ssn = forms.CharField(label="Social Security Number", required=False)



    def __init__(self, mode, *args, **kwargs):
        super(PactPatientForm, self).__init__(*args, **kwargs)
        includes = []
        if mode == "new":
            includes = ['pact_id','first_name', 'middle_name', 'last_name', 'gender', 'birthdate', 'race', 'is_latino',
                        'preferred_language', 'mass_health_expiration', 'hiv_care_clinic', 'ssn', 'notes',
                        'primary_hp', 'arm', 'art_regimen', 'non_art_regimen',]
        elif mode == 'edit':
            includes = ['first_name', 'middle_name', 'last_name', 'gender', 'birthdate', 'notes', 'primary_hp', 'arm',
                         'race', 'is_latino', 'preferred_language', 'mass_health_expiration', 'hiv_care_clinic', 'ssn',
                        'art_regimen', 'non_art_regimen',]
        elif mode == "regimen":
            includes = ['art_regimen','non_art_regimen',]
        elif mode == "birthdate":
            includes = ['birthdate',]
        elif mode == "arm":
            includes = ['arm',]
        elif mode == "primaryhp":
            includes = ['primary_hp',]
        elif mode == "notes":
            includes = ['notes',]
        elif mode == "gender":
            includes = ['gender',]
        all_fields = PactPatient._properties.keys()

        for field in all_fields:
            if includes.count(field) > 0:
                continue
            else:
                try:
                    del self.fields[field]
                except Exception, e:
                    #print "can't delete %s: %s" % (field, e)
                    pass

    def clean_mass_health_expiration(self):
        print "cleaning masshealth"
        print self.cleaned_data['mass_health_expiration']
        if self.cleaned_data['mass_health_expiration'] is None:
            return self.cleaned_data['mass_health_expiration']
        else:
            return self.cleaned_data['mass_health_expiration']

    def clean_pact_id(self):
       if PactPatient.check_pact_id(self.cleaned_data['pact_id']) == False:
           raise ValidationError("Error, pact id must be unique")
       else:
           return self.cleaned_data['pact_id']


    @property
    def helper(self):
        helper = FormHelper()
        helper.form_style="inline"
        # create the layout object
        layout = Layout(
            # first fieldset shows the company
            Fieldset('Basic Info',
                     'pact_id',
                     Row('last_name', 'middle_name', 'first_name'),
                     Row('gender', 'birthdate', 'ssn'),
                     ),

            Fieldset('Demographic Info',
                     Row('race', 'is_latino', 'preferred_language'),
                     ),
            Fieldset('PACT Info',
                     'arm',
                     'primary_hp',
                     'art_regimen',
                     'non_art_regimen',
                     'mass_health_expiration',
                     'hiv_care_clinic',),

                'notes',
        )

        helper.add_layout(layout)
        return helper


    class Meta:
        document = PactPatient


#
#    def clean(self):
#        cleaned_data = self.cleaned_data
#        all_null=True
#        for day in days:
#            if cleaned_data.get(day) != None:
#                all_null=False
#                break
#
#        if all_null:
#            raise forms.ValidationError("Error, at least one day must be chosen")
#        # Always return the full collection of cleaned data.
#        return cleaned_data

