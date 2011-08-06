from couchdbkit.ext.django.forms import DocumentForm
from uni_form.helpers import FormHelper, Layout, Fieldset, Row
from actorpermission.models.actortypes import ProviderActor

class ProviderForm(DocumentForm):
    def __init__(self, *args, **kwargs):
        super(ProviderForm, self).__init__(*args, **kwargs)


    @property
    def helper(self):
        helper = FormHelper()
        helper.form_style="inline"
        # create the layout object
        layout = Layout(
            # first fieldset shows the company
            'name',
            'title',
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

    class Meta:
        document = ProviderActor
        exclude = ('actor_uuid', 'base_type', 'affiliation')
