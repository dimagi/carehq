#!/usr/bin/env python
# vim: ai ts=4 sts=4 et sw=4
from couchdbkit.ext.django.forms import DocumentForm
from django import forms
from careplan.models import     CarePlanInstance, BaseCarePlan, BaseCarePlanItem

class BaseCarePlanForm(DocumentForm):
    class Meta:
        document = BaseCarePlan
        exclude = ('created_by', 'created_date', 'modified_by', 'modified_date')


class BaseCarePlanItemForm(DocumentForm):
    class Meta:
        document = BaseCarePlanItem
        exclude = ('created_by', 'created_date', 'modified_by', 'modified_date')


class ChooseBaseCarePlanForm(forms.Form):
    base_item = forms.ChoiceField(choices=())

    def _do_get_base_items(self):
        plans = BaseCarePlanItem.view('careplan/template_items', include_docs=True).all()
        return [(x._id, x.title) for x in plans]



    def __init__(self, *args, **kwargs):
        super(ChooseBaseCarePlanForm, self).__init__(*args, **kwargs)
        self.fields['base_item'].choices = self._do_get_base_items()
