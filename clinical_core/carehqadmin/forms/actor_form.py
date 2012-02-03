from couchdbkit.ext.django.forms import DocumentForm
from django.core.exceptions import ValidationError
from permissions.models import Actor


def get_actor_form(doc_class, includes=[], excludes=['actor_uuid', '_id', '_rev', 'base_type','doc_type']):
    class ActorForm(DocumentForm):


        def __init__(self, tenant, *args, **kwargs):
            super(ActorForm, self).__init__(*args, **kwargs)
            all_fields = doc_class._properties.keys()
            self.tenant = tenant

            for field in all_fields:
                if excludes.count(field) > 0:
                    try:
                        del self.fields[field]
                    except:
                        pass
                else:
                        continue
#
#        def clean(self):
#            actor_name = '%s-%s-%s_%s' % (self.tenant.prefix, doc_class.__name__, self.cleaned_data['first_name'], self.cleaned_data['last_name'])
#            #actor_name = '%s.%s.%s_%s.%s' % (tenant.prefix, self.__class__.__name__, self.last_name, self.first_name, self.get_hash()[0:10])
#            if Actor.objects.filter(name=actor_name).count() > 0:
#                raise ValidationError("Error, a provider of this name already exists")
#            return self.cleaned_data

        class Meta:
            document = doc_class
    return ActorForm

