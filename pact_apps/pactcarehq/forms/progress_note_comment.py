from django import forms
from django.forms.util import ValidationError
from django.forms import widgets

from casetracker import constants

class ProgressNoteComment(forms.Form):
    """
    Form to provide for simple editing/commentnig on an inbound progrssnote for PACT
    """
    comment = forms.CharField(required=True, error_messages = {'required': 'You must provide some comment'}, widget=forms.Textarea)

    def __init__(self, progress_note_instance=None, *args, **kwargs):
        super(ProgressNoteComment, self).__init__(*args, **kwargs)

    def clean(self):
        return self.cleaned_data
