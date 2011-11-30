from django.forms import forms
from django.forms.fields import ChoiceField, IntegerField
from django.forms.models import ModelChoiceField
from shinelabels.models import ZebraPrinter

class PrinterModelChoiceField(ModelChoiceField):
    def label_from_instance(self, obj):
         return "%s: %s" % (obj.location, obj.name)


class PrintLabelForm(forms.Form):

    LABEL_CHOICES = (
        ('standard', 'Standard Labels'),
        ('narrow', 'Narrow Cryo Labels'),
    )

    printer = PrinterModelChoiceField(ZebraPrinter.objects.all())
    number = IntegerField(min_value=1, max_value=20)
    type = ChoiceField(choices=LABEL_CHOICES, required=True, initial='standard')
