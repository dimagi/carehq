#!/usr/bin/env python
# vim: ai ts=4 sts=4 et sw=4

from django import forms
from django.contrib.auth.models import User
from django.forms.util import ErrorList, ValidationError
from datetime import datetime
from django.forms import widgets

#ashand specific applications
from casetracker.models import Case, CaseEvent, CaseAction, Priority, Status, Category
from patient.models import Patient

from careplan.models import PlanCategory, PlanRule, TemplateCarePlan, TemplateCarePlanItem, CarePlan, CarePlanItem 


class CareplanForm(forms.ModelForm):
    class Meta:
        model = CarePlan 
