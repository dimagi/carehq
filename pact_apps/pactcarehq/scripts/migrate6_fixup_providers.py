from django.contrib.auth.models import User
from django.core.management import call_command
from actorpermission.models import BaseActorDocument, ProviderActor, CHWActor
from carehq_core import carehq_constants, carehq_api
from pactconfig import pact_constants
from pactpatient.models import PactPatient
from patient.models import Patient
from permissions.models import Actor, PrincipalRoleRelation, Role
from nameparser import HumanName
import settings
from tenant.models import Tenant

def run():
    """
    Migration script to turn CHWs into full fledged Providers.

    Also converts existing providers to use the updated role/actor constants.
    This is a migration necessary for the merge of branch chwprovider to develop
    """
    print "Initializing carehq globals bootstrap"
    call_command('carehq_init')

    #change existing actor names using get_actor_djangoname
    #flip them to use the universal CareHQ constants, not pact specific ones.
    actors=Actor.objects.all()
    print "Iterating through actors:"
    tenant = Tenant.objects.get(name="PACT")
    for a in actors:
        print "\tActor: %s" % a.name
        django_doc = a.actordoc
        new_name = django_doc.get_actor_djangoname(tenant)
        print "\tSetting new name: %s->%s" % (a.name, new_name)
        a.name = new_name
        a.save()
        prrs = PrincipalRoleRelation.objects.filter(actor=a)
        for prr in prrs:
            print "\t\tRole: %s" % prr
            #rename existing roles from pact constants to use the carehq constants
            if prr.role.name == pact_constants.role_external_provider:
                new_role = Role.objects.get(name=carehq_constants.role_external_provider)
                print "\t\tFlipping role to CareHQ role"
                #etc etc
                prr.role = new_role
                prr.save()
            else:
                continue


