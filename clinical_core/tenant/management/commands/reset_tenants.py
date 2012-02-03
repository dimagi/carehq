#warning DO NOT RUN THIS IN PRODUCTION

# django imports
from django.core.management.base import BaseCommand

# permissions imports
from permissions.models import Role, ObjectPermission, Permission
# inspired source from
# https://bitbucket.org/diefenbach/django-lfc/src/1529b35fb12e/lfc/management/commands/lfc_init.py
# An implementation of the permissions for a CMS framework.
from tenant.models import Tenant

class Command(BaseCommand):
    args = ''
    help = """
    Reinitialize ALL tenant permissions/settings
    """

    def handle(self, *args, **options):

        confirm = raw_input("""
You have requested a tenant reset.
This will IRREVERSIBLY DESTROY
ALL tenant configuratio in your database and permissions as well.
Are you sure you want to do this?

Type 'yes' to continue, or 'no' to cancel:
""")

        if confirm != 'yes':
            print "Reset cancelled."
            return

        Permission.objects.all().delete()
        Tenant.objects.all().delete()
        Role.objects.all().delete()
        ObjectPermission.objects.all().delete()
