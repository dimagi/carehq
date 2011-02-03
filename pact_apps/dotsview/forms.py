from django import forms
from django.utils.safestring import mark_safe
from uni_form.helpers import FormHelper, Layout, Row
from dotsview.models.couchmodels import TIME_LABEL_LOOKUP

#source: https://wikis.utexas.edu/display/~bm6432/Django-Modifying+RadioSelect+Widget+to+have+horizontal+buttons
class HorizRadioRenderer(forms.RadioSelect.renderer):
    """ this overrides widget method to put radio buttons horizontally
        instead of vertically.
    """
    def render(self):
        """Outputs radios"""
        #return mark_safe('<div class="fg-buttonset">%s</div>' % u'\n'.join([u'%s\n' % w for w in self]))
        return mark_safe('\n'.join([u'%s\n' % w for w in self]))

class AddendumForm(forms.Form):
    DOSES_CHOICES = (
    ('all', 'All'),
    ('some', 'Some'),
    ('none', 'None'),
    ('unknown', 'Unknown'),
    )

    OBSERVATION_CHOICES = (
    ('direct', 'Direct'),
    ('pillbox', 'Pillbox'),
    ('check', 'Check'),
    ('self', 'Self')
    )


    DRUG_TYPE_CHOICES = (
    ('art', 'ART'),
    ('nonart', 'Non-ART'),
    )
    drug_type = forms.CharField(widget=forms.HiddenInput())
    dose_number = forms.IntegerField(widget=forms.HiddenInput())
    dose_total = forms.IntegerField(widget=forms.HiddenInput())

    doses_taken = forms.ChoiceField(choices=DOSES_CHOICES, required=True, widget=forms.RadioSelect(renderer=HorizRadioRenderer)) #, attrs={'class': 'fg-button ui-state-default ui-priority-primary'}))
    observation_type = forms.ChoiceField(choices=OBSERVATION_CHOICES, required=True, widget=forms.RadioSelect(renderer=HorizRadioRenderer)) #, attrs={'class': 'fg-button ui-state-default ui-priority-primary'}))

#    helper = FormHelper()
#
#    layout = Layout(
#
#        Row('doses_taken'),
#        Row('observation_type'),
#    )
#    helper.add_layout(layout)

#    def __init__(self, drug_type=None, dose_number=0, dose_total=0, *args, **kwargs):
#        super(AddendumForm, self).__init__(*args, **kwargs)
#        self.drug_type = drug_type
#        self.dose_number = dose_number
#        self.dose_total = dose_total

    def get_dose_display(self):
        print "get dose display"
        if self.initial['dose_number'] == 0 and self.initial['dose_total'] == 0:
            return "--null--"
        else:
            return TIME_LABEL_LOOKUP[self.initial['dose_total']][self.initial['dose_number']]