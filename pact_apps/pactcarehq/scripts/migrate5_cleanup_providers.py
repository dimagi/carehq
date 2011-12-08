from actorpermission.models.actortypes import BaseActorDocument, ProviderActor
from permissions.models import Actor
from nameparser import HumanName
from tenant.models import Tenant

def run():
    """
    Script to split out providers title into a lastname, firstname, title, provider_title
    """

    #actors = Actor.objects.all()

    raw_docs = BaseActorDocument.view('actorpermission/all_actors', include_docs=True).all()
    pact_tenant = Tenant.objects.get(name="PACT")

    for r in raw_docs:
        try:
            actor_doc = BaseActorDocument.get_typed_from_id(r._id)
            raw_name = actor_doc.name
            parsed_name = HumanName(raw_name)
            #print parsed_name.title
            if isinstance(actor_doc, ProviderActor):
                #set the old title to the new provider_title
                actor_doc.provider_title = actor_doc.title

            print "%s: %s" % (raw_name, list(parsed_name))
            if len(parsed_name.title) > 0:
                print "\tTitles: %s" % parsed_name.title
                actor_doc.title=parsed_name.title


            print "\tFirst: %s" % parsed_name.first





            if len(parsed_name.middle) > 0:
                print "\tMiddle: %s" % parsed_name.middle
                actor_doc.first_name = "%s %s" % (parsed_name.first, parsed_name.middle.replace('.',''))
            else:
                actor_doc.first_name = parsed_name.first

            print "\tLast: %s" % parsed_name.last

            if len(parsed_name.suffix) > 0:
                print "\tSuffix: %s" % parsed_name.suffix
                actor_doc.last_name = "%s %s" % (parsed_name.last, parsed_name.suffix)
            else:
                actor_doc.last_name = parsed_name.last
            #print "%s: %s, %s\n" % (raw_name, parsed_name.last, parsed_name.first)
            delattr(actor_doc,'name')
            actor_doc.save(pact_tenant)
        except Exception, ex:
            print "Error: %s" % ex
