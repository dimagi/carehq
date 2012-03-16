#!/usr/bin/env python
# vim: ai ts=4 sts=4 et sw=4
from couchdbkit.ext.django.forms import DocumentForm
from django import forms
from django.core.exceptions import ValidationError
from careplan.models import     CarePlanInstance, BaseCarePlan, BaseCarePlanItem, CarePlanItem

class BaseCarePlanForm(DocumentForm):
    class Meta:
        document = BaseCarePlan
        exclude = ('created_by', 'created_date', 'modified_by', 'modified_date')


class BaseCarePlanItemForm(DocumentForm):
    class Meta:
        document = BaseCarePlanItem
        exclude = ('created_by', 'created_date', 'modified_by', 'modified_date')


class CarePlanInstanceForm(DocumentForm):
    #patient_guid = forms.CharField(widget=forms.HiddenInput())
    #tenant = forms.CharField(widget=forms.HiddenInput())

    class Meta:
       document = CarePlanInstance
       exclude = ('created_by', 'created_date', 'modified_by', 'modified_date', 'origin_id', 'origin_rev', 'status', 'patient_guid', 'tenant')

    def clean_title(self):
        if len(self.cleaned_data['title']) == 0:
            raise ValidationError("Error, please enter a title")
        else:
            return self.cleaned_data['title']

class CarePlanItemForm(DocumentForm):
    class Meta:
        document = CarePlanItem
        exclude = ('tenant', 'status','issues','created_by', 'created_date', 'modified_by', 'modified_date', 'origin_id', 'origin_rev')

class ChooseBaseItemForm(forms.Form):
    base_item = forms.ChoiceField(choices=())

    def _do_get_base_items(self):
        plans = BaseCarePlanItem.view('careplan/template_items', include_docs=True).all()
        return [(x._id, x.title) for x in plans]



    def __init__(self, *args, **kwargs):
        super(ChooseBaseItemForm, self).__init__(*args, **kwargs)
        self.fields['base_item'].choices = self._do_get_base_items()


class ChooseBasePlanForm(forms.Form):
    base_plan = forms.ChoiceField(choices=(), required=False)
    patient_guid = forms.CharField(widget=forms.HiddenInput())
    tenant = forms.CharField(widget=forms.HiddenInput())

    def _do_get_base_items(self):
        plans = BaseCarePlanItem.view('careplan/template_careplans', include_docs=True).all()
        return [(x._id, x.title) for x in plans]

    def __init__(self, *args, **kwargs):
        super(ChooseBasePlanForm, self).__init__(*args, **kwargs)
        self.fields['base_plan'].choices = self._do_get_base_items()