from django import forms

class BasicPatientForm(forms.Form):
    """
    A really basic form implementation.
    """
    GENDER_CHOICES =(
        ('m', 'Male'),
        ('f', 'Female')
    )

    patient_id = forms.CharField(required=True)
    first_name = forms.CharField(required=True)
    middle_name = forms.CharField(required=False)
    last_name = forms.CharField(required=True)
    gender = forms.ChoiceField(choices=GENDER_CHOICES, required=True)
    birthdate = forms.DateField(required=True)




