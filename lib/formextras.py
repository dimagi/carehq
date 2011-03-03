from django.contrib.auth.models import User
from django import forms

class UserField(forms.CharField):
    def clean(self, value):
        super(UserField, self).clean(value)
        try:
            User.objects.get(username=value)
            raise forms.ValidationError("Someone is already using this username. Please pick another.")
        except User.DoesNotExist:
            return value
