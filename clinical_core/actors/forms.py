from django import forms

class AddProviderForm(forms.Form):

    first_name = forms.CharField(required=True)
    last_name = forms.CharField(required=True)
    username = forms.CharField(required=True)
    title = forms.CharField()
    department = forms.CharField(required=False)
    specialty = forms.CharField(required=False)
    