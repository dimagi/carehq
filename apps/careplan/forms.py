#!/usr/bin/env python
# vim: ai ts=4 sts=4 et sw=4

from django import forms
from careplan.models import     CarePlan

class CareplanForm(forms.ModelForm):
    class Meta:
        model = CarePlan 
