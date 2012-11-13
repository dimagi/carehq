from actorpermission.models import *
from django.core.management import call_command
import simplejson
from StringIO import StringIO

def run():
    actors = Actor.objects.all()


    def get_case_map(actor):
        """django actor"""
        for prr in actor.principal_roles.all().exclude(content_id=None):
            if prr.content is not None:
                yield (prr.role.name, prr.content.couchdoc.case_id)


    print "outputting actors"
    with open('pact_actors_all.json', 'wb') as fout:
        output_json = []
        for a in actors:
            actordoc = getattr(a, 'actordoc', None)
            if actordoc is not None:
                actor_json = a.actordoc.to_json()
                actor_json['user_id'] = a.user_id
                if a.user is not None:
                    actor_json['username'] = a.user.username
                else:
                    actor_json['username'] = ""

                actor_json['case_id_map'] = list(get_case_map(a))
                output_json.append(actor_json)
        fout.write(simplejson.dumps(output_json))

    print "outputting users"
    content = StringIO()
    call_command('dumpdata', 'auth.User', indent=4,stdout=content)
    content.seek(0)
    with open('pact_users_all.json', 'wb') as fout:
        fout.write(content.read())

    print "Actor export complete"
