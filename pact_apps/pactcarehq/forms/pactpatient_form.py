from django import forms

from couchdbkit.ext.django.forms import DocumentForm
#from the models, we have this, (couchmodels.py)
#flipping to tuple
from pactpatient.models.pactmodels import PactPatient
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


#from basepatient class, can't import from here due to circular dependency
GENDER_CHOICES = (
       ('m','Male'),
       ('f','Female'),
       ('u','Undefined'),
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

class PactPatientForm(DocumentForm):
    """
    DocumentForm
    """
    arm = forms.ChoiceField(choices=ARM_CHOICES)
    art_regimen = forms.ChoiceField(choices=REGIMEN_CHOICES)
    non_art_regimen = forms.ChoiceField(choices=REGIMEN_CHOICES)
#    primary_hp = forms.ModelChoiceField(User.objects.filter(is_active=True, username__in=hack_pact_usernames), required=False)
    primary_hp = forms.ChoiceField(choices=tuple([(x, x) for x in hack_pact_usernames]))
    notes = forms.CharField(widget = widgets.Textarea(attrs={'cols':80,'rows':5}))
    #source: http://stackoverflow.com/questions/1513502/django-how-to-format-a-datefields-date-representation
    birthdate = forms.DateField(input_formats=['%m/%d/%Y'], widget=forms.DateInput(format = '%m/%d/%Y'))
    gender = forms.ChoiceField(choices=GENDER_CHOICES)



    def __init__(self, mode, *args, **kwargs):
        super(PactPatientForm, self).__init__(*args, **kwargs)
        includes = []
        if mode == "regimen":
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

