from django import forms

from couchdbkit.ext.django.forms import DocumentForm
from patient.models import CAddress


class SimpleAddressForm(forms.Form):
    """
    Form to provide for simple editing/commentnig on an inbound progrssnote for PACT
    """
    description = forms.CharField(required=True, widget=forms.Textarea(attrs={'cols': 32, 'rows': 1}))
    address = forms.CharField(required=True, widget=forms.Textarea(attrs={'cols':32, 'rows': 5}))
    address_id = forms.CharField(required=False, widget=forms.HiddenInput()) #integer


    def __init__(self, instance=None, *args, **kwargs):
        """
        instance is a CAddress model
        """

        if instance != None:
            initial = {'description': instance.description, 'address': instance.full_address, 'address_id':instance.address_id}
            super(SimpleAddressForm, self).__init__(*args, **{'initial': initial})
        else:
            super(SimpleAddressForm, self).__init__(*args, **kwargs)



class AddressForm(forms.Form):
    """
    Form to provide for simple editing/commentnig on an inbound progrssnote for PACT
    """
    description = forms.CharField(required=True, widget=forms.Textarea(attrs={'cols': 32, 'rows': 1}))
    street = forms.CharField(required=True, widget=forms.Textarea(attrs={'cols': 32, 'rows': 1}))
    city = forms.CharField(required=True, widget=forms.Textarea(attrs={'cols': 32, 'rows': 1}))
    state = forms.CharField(required=True, widget=forms.Textarea(attrs={'cols': 32, 'rows': 1}))
    postal_code = forms.CharField(required=True, widget=forms.Textarea(attrs={'cols': 32, 'rows': 1}))
#    address_id = forms.CharField(required=False, widget=forms.HiddenInput())


    def __init__(self, instance=None, *args, **kwargs):
        if instance != None:
            initial = {'description': instance.description, 'street': instance.street, 'city': instance.city, 'state': instance.state, 'postal_code': instance.postal_code, 'address_id':instance.address_id}
            super(AddressForm, self).__init__(*args, **{'initial': initial})
        else:
            super(AddressForm, self).__init__(*args, **kwargs)

