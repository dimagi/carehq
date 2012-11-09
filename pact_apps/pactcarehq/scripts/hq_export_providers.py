
from permissions.models import Actor


all_keys = ['title', 'first_name', 'last_name', 'provider_title', 'email', 'facility_address', 'facility_name',   'phone_number', 'notes']
#provider_title => job title
#title => name prefix
ident_keys = ['doc_id', 'django_id', 'actor_type']
#doc_id, actor_uuid
#title and provider_title are kinda equivalent

def run():
    """
    Script to export all the providers/careteams in pact
    """
    actors = Actor.objects.all()

    #two passes, get all the fields and sort them.
    fields = set()
    for djactor in actors:
        actordoc = getattr(djactor, 'actordoc', None)
        if actordoc is not None and actordoc.doc_type == 'ProviderActor':
            row_start = [actordoc._id, djactor.id, actordoc.doc_type]
            row = []
            #print actordoc.items()
            items = dict(actordoc.items())
            #print items
            for k in all_keys:
                if items.has_key(k) and items[k] is not None:
                    row.append(items[k])
                else:
                    row.append('')
            print row
        else:
            continue

    print sorted(fields)
