from django import forms
from django.forms import widgets
from django.contrib.auth.models import User
from pactpatient.models.pactmodels import PactPatient

days = ['sunday','monday','tuesday','wednesday','thursday','friday','saturday']

from pactconfig.constants import hack_pact_usernames

#pact_id = StringProperty() #pact_id of patient being supervised for
#supervision_topics = ListProperty() # topics discussed
#notes = StringProperty()
#
#supervision_by = StringProperty()
#supervision_date = DateTimeProperty() #actor doc_id

def get_pact_ids():
    patient_docs = PactPatient.view('pactcarehq/patient_pact_ids', include_docs=True).all()
    patient_docs = sorted(patient_docs, key=lambda x: int(x.pact_id))
    for pdoc in patient_docs:
        display = "(%s) %s %s" % (pdoc.pact_id, pdoc.first_name, pdoc.last_name)
        pact_id = pdoc.pact_id
        yield (display, pact_id)

SUPERVISION_TOPICS= (
   ('foo', 'foo'),
   ('bar', 'bar'),
)


class SupervisionForm(forms.Form):
    """
    Form to provide for simple editing/commentnig on an inbound progrssnote for PACT
    """
    active_date = forms.DateField(help_text="Date this schedule should be made active.  Note active time is 12:01am the day you choose.", required=False, widget=widgets.TextInput(attrs={'class':'activedatepicker'}))
    pact_id = forms.ChoiceField(choices=get_pact_ids(), required=True, help_text="Patient Discussed")
    supervision_topics = forms.MultipleChoiceField(choices=SUPERVISION_TOPICS, required=False, widget=forms.CheckboxSelectMultiple)

    sunday = forms.ModelChoiceField(User.objects.filter(is_active=True, username__in=hack_pact_usernames), required=False)
    monday = forms.ModelChoiceField(User.objects.filter(is_active=True, username__in=hack_pact_usernames), required=False)
    tuesday = forms.ModelChoiceField(User.objects.filter(is_active=True, username__in=hack_pact_usernames), required=False)
    wednesday = forms.ModelChoiceField(User.objects.filter(is_active=True, username__in=hack_pact_usernames), required=False)
    thursday = forms.ModelChoiceField(User.objects.filter(is_active=True, username__in=hack_pact_usernames), required=False)
    friday = forms.ModelChoiceField(User.objects.filter(is_active=True, username__in=hack_pact_usernames), required=False)
    saturday = forms.ModelChoiceField(User.objects.filter(is_active=True, username__in=hack_pact_usernames), required=False)

    comment = forms.CharField(required=False)



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


