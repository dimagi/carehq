from django import forms


class SimpleAddressForm(forms.Form):
    """
    Form to provide for simple editing/commentnig on an inbound progrssnote for PACT
    """
    description = forms.CharField(required=True, widget=forms.Textarea(attrs={'cols': 32, 'rows': 1}))
    address = forms.CharField(required=True, widget=forms.Textarea(attrs={'cols':32, 'rows': 5}))
    address_id = forms.CharField(required=False, widget=forms.HiddenInput()) #integer


class FullAddressForm(forms.Form):
    """
    Form to provide for simple editing/commentnig on an inbound progrssnote for PACT
    """
    description = forms.CharField(required=True, widget=forms.Textarea(attrs={'cols': 32, 'rows': 1}))
    street = forms.CharField(required=True, widget=forms.Textarea(attrs={'cols': 32, 'rows': 1}))
    city = forms.CharField(required=True, widget=forms.Textarea(attrs={'cols': 32, 'rows': 1}))
    state = forms.CharField(required=True, widget=forms.Textarea(attrs={'cols': 32, 'rows': 1}))
    postal_code = forms.CharField(required=True, widget=forms.Textarea(attrs={'cols': 32, 'rows': 1}))
    address_id = forms.CharField(required=False, widget=forms.HiddenInput())


    def __init__(self, instance=None, *args, **kwargs):
        if instance != None:
            initial = {'description': instance.description, 'street': instance.street, 'city': instance.city, 'state': instance.state, 'postal_code': instance.postal_code, 'address_id':instance.address_id}
            super(FullAddressForm, self).__init__(*args, **{'initial': initial})
        else:
            super(FullAddressForm, self).__init__(*args, **kwargs)

