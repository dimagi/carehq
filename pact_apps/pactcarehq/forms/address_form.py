from django import forms

from couchdbkit.ext.django.forms import DocumentForm
from patient.models.couchmodels import CAddress

class AddressForm(DocumentForm):
    """
    DocumentForm
    """

    class Meta:
        document = CAddress
        exclude = ('edited_by','created_by', 'started', 'ended', 'deprecated', 'address_id')
        
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

