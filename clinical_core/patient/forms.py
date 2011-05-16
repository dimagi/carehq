from django import forms

class BasicPatientForm(forms.Form):
    """
    A really basic form implementation.
    """
    GENDER_CHOICES =(
        ('m', 'Male'),
        ('f', 'Female')
    )


    first_name = forms.CharField(required=True)
    middle_name = forms.CharField()
    last_name = forms.CharField(required=True)
    gender = forms.ChoiceField(choices=GENDER_CHOICES, required=True)
    birthdate = forms.DateField(required=True)




