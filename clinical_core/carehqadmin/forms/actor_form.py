from couchdbkit.ext.django.forms import DocumentForm


def get_actor_form(doc_class):

    includes = []
    excludes = ['actor_uuid', 'base_type', ]
    class ActorForm(DocumentForm):
        def __init__(self, *args, **kwargs):
            super(ActorForm, self).__init__(*args, **kwargs)
            all_fields = doc_class._properties.keys()

            for field in all_fields:
                if excludes.count(field) > 0:
                    try:
                        del self.fields[field]
                    except:
                        pass
                else:
                        continue

        class Meta:
            document = doc_class
    return ActorForm

