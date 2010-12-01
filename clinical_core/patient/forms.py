from django import forms
from django.forms import widgets

class BasicPatientForm(forms.Form):
    GENDER_CHOICES =(
        ('m', 'Male'),
        ('f', 'Female')
    )


    first_name = forms.CharField(required=True)
    middle_name = forms.CharField()
    last_name = forms.CharField(required=True)
    gender = forms.ChoiceField(choices=GENDER_CHOICES, required=True)
    birthdate = forms.DateField(required=True)



class PactPatientForm(BasicPatientForm):
    PACT_ARM_CHOICES = (
        ('HP', 'HP - Health Promoter'),
        ('DOT', 'DOT - Directly Observed Therapy'),
        ('Discharged', 'Discharged'),
    )
    REGIMEN_CHOICES = (
        (None, '-- None --'),
        ('qd', 'QD - Once a day'),
        ('bid', 'BID - Twice a day'),
        ('qd-am', 'QD - Once a day (Morning)'),
        ('qd-pm', 'QD - Once a day (Evening)'),
        ('tid', 'TID - Three times a day'),
        ('qid', 'QID - Four times a day'),
    )

    pact_id = forms.CharField(required=True, label="PACT ID") 
    arm = forms.ChoiceField(choices=PACT_ARM_CHOICES, required=True)
    art_regimen = forms.ChoiceField(choices=REGIMEN_CHOICES)
    non_art_regimen = forms.ChoiceField(choices=REGIMEN_CHOICES)


    primary_hp = forms.CharField() #this is the sketchy, hacky way in which we link patients to providers for pact pilot

