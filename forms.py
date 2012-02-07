from django import forms
from django.contrib.auth.forms import AuthenticationForm

class RememberAuthForm(AuthenticationForm):
    remember_me = forms.BooleanField(required=False, label = "Keep me logged in", help_text="Remember me!")