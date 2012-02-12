from couchdbkit.ext.django.forms import DocumentForm
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from uni_form.helpers import FormHelper, Layout, Submit
from actorpermission.models import  CaregiverActor
from permissions.models import Actor

from django import forms

class CaregiverForm(DocumentForm):
    new_user = forms.BooleanField(help_text="Create new user for this cargiver")
    username = forms.CharField(max_length=160)
    relation=forms.ChoiceField(choices=CaregiverActor.RELATIONSHIP_CHOICES)


    def __init__(self, tenant, *args, **kwargs):
        super(CaregiverForm, self).__init__(*args, **kwargs)
        self.tenant = tenant

    @property
    def helper(self):
        helper = FormHelper()
        helper.form_style="inline"
        # create the layout object
        layout = Layout(
            # first fieldset shows the company
            'first_name',
            'last_name',

            'new_user',
            'username',

            'email',
            'relation',
            'phone_number',
            'address',
            'notes',
            Submit(css_class="btn", name="Submit", value="Save"),
            )

        helper.add_layout(layout)
        return helper

    def clean(self):
        actor_name = '%s-%s-%s_%s' % (self.tenant.prefix, 'ProviderActor', self.cleaned_data['first_name'], self.cleaned_data['last_name'])
        do_check_name = False

        if self.instance and (self.instance.first_name != self.cleaned_data['first_name'] and self.instance.last_name != self.cleaned_data['last_name']):
            do_check_name = True

        elif self.instance is None:
            do_check_name=True

        if do_check_name:
            if Actor.objects.filter(name=actor_name).count() > 0:
                raise ValidationError("Error, a provider of this name already exists")

#        if self.cleaned_data.get('new_user', False):
#            if not self.cleaned_data.get('username', None):
#                raise ValidationError("Error, please enter a username if you're wanting to make a new user")
#            elif User.objects.filter(username=self.cleaned_data['username']).count() > 0:
#                raise ValidationError("Sorry, that username either is not valid or already exists")
        return self.cleaned_data

    def clean_username(self):
        if self.cleaned_data.get('new_user', False):
            if not self.cleaned_data.get('username', None):
                raise ValidationError("Error, please enter a username if you're wanting to make a new user")
            elif User.objects.filter(username=self.cleaned_data['username']).count() > 0:
                raise ValidationError("Sorry, that username either is not valid or already exists")
            return self.cleaned_data['username']
        return ''



    class Meta:
        document = CaregiverActor
        exclude = ('title','name','actor_uuid', 'base_type', 'affiliation')
