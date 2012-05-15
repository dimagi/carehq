from couchdbkit.ext.django.forms import DocumentForm
from django.core.exceptions import ValidationError
from django.forms.forms import Form
from django import forms
from django.forms.widgets import RadioSelect
from django.utils.safestring import mark_safe
from carehqapp.models import UsabilitySurvey, LIKERT_CHOICES

class HorizRadioRenderer(RadioSelect.renderer):
    """ this overrides widget method to put radio buttons horizontally
        instead of vertically.
    """
    def render(self):
        """Outputs radios"""
        #ret = []
        #ret.append('<table>')
        ret = mark_safe(u'\n'.join([u'%s\n' % w for w in self]))
        for w in self:
            print dir(w)
        return ret

class HorizRadioSelect(RadioSelect):
    renderer = HorizRadioRenderer

class SurveyForm(DocumentForm):
    patient_doc_id = forms.CharField(required=True, widget=forms.HiddenInput()) #integer
    survey_context = forms.CharField(required=True, widget=forms.HiddenInput()) #integer
    user = forms.CharField(required=True, widget=forms.HiddenInput()) #integer
    question_one = forms.ChoiceField(label="I would like to use this system frequently", choices=LIKERT_CHOICES, required=True)
    question_two = forms.ChoiceField(label="This system was unnecessarily complex", choices=LIKERT_CHOICES, required=True)
    question_three = forms.ChoiceField(label="This system was easy to use", choices=LIKERT_CHOICES, required=True)
    question_four = forms.ChoiceField(label="I would need help from someone to be able to use this system", choices=LIKERT_CHOICES, required=True)
    question_five = forms.ChoiceField(label="The various parts of this system fit together well", choices=LIKERT_CHOICES, required=True)
    question_six = forms.ChoiceField(label="There was to much inconsistency in this system", choices=LIKERT_CHOICES, required=True)
    question_seven = forms.ChoiceField(label="I believe that most people would learn how to use this system quickly", choices=LIKERT_CHOICES, required=True)
    question_eight = forms.ChoiceField(label="This system was very cumbersome to use", choices=LIKERT_CHOICES, required=True)
    question_nine = forms.ChoiceField(label="I felt confident while using this system", choices=LIKERT_CHOICES, required=True)
    question_ten = forms.ChoiceField(label="I needed to learn  lot about this system before I could start using it", choices=LIKERT_CHOICES, required=True)
    question_eleven = forms.ChoiceField(label="I believe this system would be useful for other cancer patients and their caregivers and healthcare providers", choices=LIKERT_CHOICES, required=True)
    question_twelve = forms.ChoiceField(label="This system would be useful to me", choices=LIKERT_CHOICES, required=True)

    def do_clean_question(self, question_num):
        if self.cleaned_data[question_num] == 'None':
            raise ValidationError("You must choose an answer for %s" % question_num)
        else:
            return int(self.cleaned_data[question_num])

    def clean_question_one(self):
        return self.do_clean_question("question_one")

    def clean_question_two(self):
        return self.do_clean_question("question_two")

    def clean_question_three(self):
        return self.do_clean_question("question_three")

    def clean_question_four(self):
        return self.do_clean_question("question_four")

    def clean_question_five(self):
        return self.do_clean_question("question_five")

    def clean_question_six(self):
        return self.do_clean_question("question_six")

    def clean_question_seven(self):
        return self.do_clean_question("question_seven")

    def clean_question_eight(self):
        return self.do_clean_question("question_eight")

    def clean_question_nine(self):
        return self.do_clean_question("question_nine")

    def clean_question_ten(self):
        return self.do_clean_question("question_ten")

    def clean_question_eleven(self):
        return self.do_clean_question("question_eleven")

    def clean_question_twelve(self):
        return self.do_clean_question("question_twelve")


    class Meta:
        exclude = ('survey_date',)
        document = UsabilitySurvey

