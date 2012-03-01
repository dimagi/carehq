from django.forms import forms, fields
from hutch.forms import AuxImageUploadForm

FILE_CHOICES = (
    ('consent_form', 'Consent Form'),
    ('hcms_activation_letter', 'HCMS Form'),
    ('install_instructions', 'Install Instructions'),
    ('vnab_request_fax', 'VNAB Request Fax'),
    )


class ASHandStudyFileUploadForm(AuxImageUploadForm):
    file_type = fields.ChoiceField(label="Image Upload Type", choices=FILE_CHOICES)
    notes = fields.CharField(required=False)

