from pactpatient.models import PactPatient
from patient.models import Patient
from patient.models.patientmodels import BasePatient

def run():
    """Help script to regenerate a django patient model when couch has replicated the patient docs"""




#warning DO NOT RUN THIS IN PRODUCTION

# django imports
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from django.contrib.sites.models import Site
from django.contrib.contenttypes.models import ContentType

# permissions imports
from pactconfig import constants
from permissions.models import Role, ObjectPermission, Permission
import permissions.utils
# inspired source from
# https://bitbucket.org/diefenbach/django-lfc/src/1529b35fb12e/lfc/management/commands/lfc_init.py
# An implementation of the permissions for a CMS framework.
from tenant.models import Tenant

class Command(BaseCommand):
    args = ''
    help = """
    Generate django patients from ones existing in couch.
    """

    def handle(self, *args, **options):
        pdocs = BasePatient.view('patient/all', include_docs=True).all()
        updated = False
        for pdoc in pdocs:
            try:
                pt = Patient.objects.get(doc_id=pdoc._id)
            except Patient.DoesNotExist:
                pt = Patient(id=pdoc.django_uuid, doc_id=pdoc._id)
                pt.save()
                updated=True
                print "Creating django patient from couchdoc %s:%s" % (pt.id, pt.doc_id)
        if not updated:
            print "All couch patients are in sync with django!!"


