# django imports
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from django.contrib.sites.models import Site
from django.contrib.contenttypes.models import ContentType

# permissions imports
from carehqapp import constants
from permissions.models import Role, ObjectPermission, Permission
import permissions.utils
# inspired source from
# https://bitbucket.org/diefenbach/django-lfc/src/1529b35fb12e/lfc/management/commands/lfc_init.py
# An implementation of the permissions for a CMS framework.
from tenant.models import Tenant

class Command(BaseCommand):
    args = ''
    help = """Initializes PACT permissions

    This will create permissions for PACT
    """

    def handle(self, *args, **options):
        # Register roles
        role_suspended = permissions.utils.register_role(constants.role_suspended)
        role_caregiver = permissions.utils.register_role(constants.role_caregiver)
        role_primary_provider = permissions.utils.register_role(constants.role_primary_provider)
        role_provider = permissions.utils.register_role(constants.role_provider)
        role_admin_tenant = permissions.utils.register_role(constants.role_admin_tenant)

        # Registers permissions
        perm_noaccess = permissions.utils.register_permission(constants.perm_noaccess, constants.perm_noaccess)
        perm_patient_view = permissions.utils.register_permission(constants.perm_patient_view, constants.perm_patient_view)
        perm_patient_edit = permissions.utils.register_permission(constants.perm_patient_edit, constants.perm_patient_edit)
        perm_submit_patient_data = permissions.utils.register_permission(constants.perm_submit_patient_data, constants.perm_submit_patient_data)
        perm_edit_patient_data = permissions.utils.register_permission(constants.perm_edit_patient_data, constants.perm_edit_patient_data)
        perm_manage_tenant = permissions.utils.register_permission(constants.perm_manage_tenant, constants.perm_manage_tenant)

        ctype = ContentType.objects.get_for_model(Tenant)

        # Create domain
        tenant = Tenant.objects.get_or_create(name=constants.TENANT_NAME, prefix=constants.TENANT_PREFIX, full_name=constants.TENANT_FULL_NAME)[0]

        # Set permissions for tenant
        permissions.utils.grant_permission(tenant, role_caregiver, perm_patient_view)
        permissions.utils.grant_permission(tenant, role_caregiver, perm_patient_edit)
        permissions.utils.grant_permission(tenant, role_caregiver, perm_submit_patient_data)

        permissions.utils.grant_permission(tenant, role_primary_provider, perm_patient_view)
        permissions.utils.grant_permission(tenant, role_primary_provider, perm_patient_edit)
        permissions.utils.grant_permission(tenant, role_primary_provider, perm_submit_patient_data)
        permissions.utils.grant_permission(tenant, role_primary_provider, perm_edit_patient_data)

        permissions.utils.grant_permission(tenant, role_admin_tenant, perm_patient_view)
        permissions.utils.grant_permission(tenant, role_admin_tenant, perm_manage_tenant)

        permissions.utils.grant_permission(tenant, role_provider, perm_patient_view)
        permissions.utils.grant_permission(tenant, role_provider, perm_patient_edit)

