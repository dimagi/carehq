from django import forms

from couchdbkit.ext.django.forms import DocumentForm
from patient.models.couchmodels import CAddress, CPatient
#from the models, we have this, (couchmodels.py)
#flipping to tuple
from django.contrib.auth.models import User
from .weekly_schedule_form import hack_pact_usernames
from django.forms import widgets

REGIMEN_CHOICES = (
    ('QD', "QD"),
    ('BID', "BID"),
    ('QD-AM', "QD-AM"),
    ('QD-PM', "QD-PM"),
    ('TID', "TID"),
    ('QID', "QID"),
)

ARM_CHOICES = (
    ('HP', 'HP'),
    ('DOT', 'DOT'),
    ('Discharged', 'Discharged'),
)

#ghetto_regimen_map = {
#    "qd": '1',
#    "bid": '2',
#    "qd-am": '1',
#    "qd-pm": '1',
#    "tid": '3',
#    "qid": '4',
#    '': '' ,
#}

class CPatientForm(DocumentForm):
    """
    DocumentForm
    """
    arm = forms.ChoiceField(choices=ARM_CHOICES)
    art_regimen = forms.ChoiceField(choices=REGIMEN_CHOICES)
    non_art_regimen = forms.ChoiceField(choices=REGIMEN_CHOICES)
    primary_hp = forms.ModelChoiceField(User.objects.filter(is_active=True, username__in=hack_pact_usernames), required=False)
    notes = forms.CharField(widget = widgets.Textarea(attrs={'cols':80,'rows':5}))

    def __init__(self, mode, *args, **kwargs):
        super(CPatientForm, self).__init__(*args, **kwargs)
        includes = []
        if mode == "regimen":
            includes = ['art_regimen','non_art_regimen',]
        elif mode == "dob":
            includes = ['birthdate',]
        elif mode == "arm":
            includes = ['arm',]
        elif mode == "primaryhp":
            includes = ['primary_hp',]
        elif mode == "notes":
            includes = ['notes',]
        all_fields = CPatient._properties.keys()

        for field in all_fields:
            if includes.count(field) > 0:
                continue
            else:
                try:
                    del self.fields[field]
                except Exception, e:
                    #print "can't delete %s: %s" % (field, e)
                    pass

    class Meta:
        document = CPatient

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

