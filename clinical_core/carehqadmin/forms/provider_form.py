from couchdbkit.ext.django.forms import DocumentForm
from django.core.exceptions import ValidationError
from uni_form.helpers import FormHelper, Layout, Fieldset, Row
from actorpermission.models.actortypes import ProviderActor
from permissions.models import Actor

class ProviderForm(DocumentForm):
    def __init__(self, tenant, *args, **kwargs):
        super(ProviderForm, self).__init__(*args, **kwargs)
        self.tenant = tenant


    @property
    def helper(self):
        helper = FormHelper()
        helper.form_style="inline"
        # create the layout object
        layout = Layout(
            # first fieldset shows the company
            'title',
            'first_name',
            'last_name',
            'provider_title',
            Row('phone_number', 'email',),
            Row('gender', 'birthdate', 'ssn'),

            Fieldset('Location Info',
                'facility_name',
                'facility_address',
                     ),
            'notes',
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
        return self.cleaned_data



    class Meta:
        document = ProviderActor
        exclude = ('actor_uuid', 'base_type', 'affiliation')
