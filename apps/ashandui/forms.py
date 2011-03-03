from django import forms
from lib.formextras import UserField

class AddProviderForm(forms.Form):
    first_name = forms.CharField(required=True, max_length=30)
    last_name = forms.CharField(required=True, max_length=30)
    username = UserField(required=True, max_length=30)
    password = forms.CharField(required=True,widget=forms.PasswordInput)
    password_confirm = forms.CharField(required=True,widget=forms.PasswordInput, label="Password (again)")
    title = forms.CharField()
    department = forms.CharField(required=False)
    specialty = forms.CharField(required=False)

    def clean_password(self):
        if self.data['password'] != self.data['password_confirm']:
            raise forms.ValidationError('Passwords are not the same')
        return self.data['password']

    def clean(self, *args, **kwargs):
        self.clean_password()
        return super(AddProviderForm, self).clean(*args, **kwargs)

class LinkProviderForm(forms.Form):
    doctor = forms.MultipleChoiceField(widget=forms.CheckboxSelectMultiple)
    patient = forms.HiddenInput()