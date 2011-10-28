from django.forms import forms, fields
from hutch.forms import AuxImageUploadForm

PHOTO_CHOICES = (
    ('consent_photo','Consent Form'),
    #lab one
    ('gram_stain_photo','Gram Stain'),
    ('afb_stain_photo','AFB Stain'),



    #lab two
    ('agar_blood_photo',"Agar Blood"),
    ('agar_chocolate_photo',"Agar Chocolate"),
    ('agar_macconkey_photo',"Agar MacConkey"),
    ('agar_lowenstein-jensen_photo',"Agar Lowenstein-Jensen"),
    ('agar_middlebrook_photo',"Agar Middlebrook"),

    #lab three
    ('vitek_photo', "Vitek Result"),
    ('api_strip_photo',"API Strip"),

    #lab four
    ('plate_image','Plate Image'),
)


class ClinicalImageUploadForm(AuxImageUploadForm):
    image_type = fields.ChoiceField(label="Image Upload Type", choices=PHOTO_CHOICES)
    notes = fields.CharField(required=False)

