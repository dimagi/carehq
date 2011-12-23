# django imports
from django.core.management.base import BaseCommand
from django.contrib.contenttypes.models import ContentType

# permissions imports
from carehq_core import carehq_constants
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
        role_suspended =    permissions.utils.register_role(carehq_constants.role_suspended,"Suspended")
        role_chw =          permissions.utils.register_role(carehq_constants.role_chw, 'CHW')
        role_primary_chw =  permissions.utils.register_role(carehq_constants.role_primary_chw, "Primary CHW")
        role_navigator =    permissions.utils.register_role(carehq_constants.role_navigator, "Navigator")
        role_provider =     permissions.utils.register_role(carehq_constants.role_provider, "Provider")
        role_external_provider =    permissions.utils.register_role(carehq_constants.role_external_provider, "External Provider")
        role_patient =              permissions.utils.register_role(carehq_constants.role_patient, "Patient")
        role_caregiver =            permissions.utils.register_role(carehq_constants.role_caregiver, "Caregiver")

        role_admin_tenant = permissions.utils.register_role(carehq_constants.role_admin_tenant, "CareHQ Tenant Admin")

        # Registers permissions
        perm_noaccess = permissions.utils.register_permission(carehq_constants.perm_noaccess, carehq_constants.perm_noaccess)
        perm_patient_view = permissions.utils.register_permission(carehq_constants.perm_patient_view, carehq_constants.perm_patient_view)
        perm_patient_edit = permissions.utils.register_permission(carehq_constants.perm_patient_edit, carehq_constants.perm_patient_edit)
        perm_chw_manage = permissions.utils.register_permission(carehq_constants.perm_chw_manage, carehq_constants.perm_chw_manage)
        perm_report_view = permissions.utils.register_permission(carehq_constants.perm_report_view, carehq_constants.perm_report_view)
        perm_report_run = permissions.utils.register_permission(carehq_constants.perm_report_run, carehq_constants.perm_report_run)
        perm_submit_patient_data = permissions.utils.register_permission(carehq_constants.perm_submit_patient_data, carehq_constants.perm_submit_patient_data)
        perm_edit_patient_data = permissions.utils.register_permission(carehq_constants.perm_edit_patient_data, carehq_constants.perm_edit_patient_data)
        perm_manage_tenant = permissions.utils.register_permission(carehq_constants.perm_manage_tenant, carehq_constants.perm_manage_tenant)

        ctype = ContentType.objects.get_for_model(Tenant)

        tenants = [
            ('PACT', 'pact', 'Prevention and Access to Care and Treatment'),
            ('ASHand', 'ASHand', 'CareHQ ASHand Study'),
            ('MEPI', 'mepi', 'UCSD MEPI Bacteremia')
        ]
        for tenant_name, prefix, full_name in tenants:
            # Create Tenant
            tenant = Tenant.objects.get_or_create(name=tenant_name, prefix=prefix, full_name=full_name)[0]

            # Set permissions for tenant
            permissions.utils.grant_permission(tenant, role_chw, perm_patient_view)
            permissions.utils.grant_permission(tenant, role_chw, perm_patient_edit)
            permissions.utils.grant_permission(tenant, role_chw, perm_report_view)
            permissions.utils.grant_permission(tenant, role_chw, perm_submit_patient_data)

            permissions.utils.grant_permission(tenant, role_primary_chw, perm_patient_view)
            permissions.utils.grant_permission(tenant, role_primary_chw, perm_patient_edit)
            permissions.utils.grant_permission(tenant, role_primary_chw, perm_report_view)
            permissions.utils.grant_permission(tenant, role_primary_chw, perm_submit_patient_data)
            permissions.utils.grant_permission(tenant, role_primary_chw, perm_edit_patient_data)

            permissions.utils.grant_permission(tenant, role_caregiver, perm_patient_view)
            permissions.utils.grant_permission(tenant, role_caregiver, perm_submit_patient_data)
            permissions.utils.grant_permission(tenant, role_caregiver, perm_patient_edit)

            permissions.utils.grant_permission(tenant, role_navigator, perm_patient_view)
            permissions.utils.grant_permission(tenant, role_navigator, perm_submit_patient_data)
            permissions.utils.grant_permission(tenant, role_navigator, perm_patient_edit)
            permissions.utils.grant_permission(tenant, role_navigator, perm_report_view)
            permissions.utils.grant_permission(tenant, role_navigator, perm_report_run)
            permissions.utils.grant_permission(tenant, role_navigator, perm_submit_patient_data)
            permissions.utils.grant_permission(tenant, role_navigator, perm_edit_patient_data)

            permissions.utils.grant_permission(tenant, role_provider, perm_patient_view)
            permissions.utils.grant_permission(tenant, role_provider, perm_patient_edit)
            permissions.utils.grant_permission(tenant, role_provider, perm_report_view)
            permissions.utils.grant_permission(tenant, role_provider, perm_report_run)
            permissions.utils.grant_permission(tenant, role_provider, perm_submit_patient_data)
            permissions.utils.grant_permission(tenant, role_provider, perm_edit_patient_data)

            permissions.utils.grant_permission(tenant, role_admin_tenant, perm_patient_view)
            permissions.utils.grant_permission(tenant, role_admin_tenant, perm_chw_manage)
            permissions.utils.grant_permission(tenant, role_admin_tenant, perm_report_view)
            permissions.utils.grant_permission(tenant, role_admin_tenant, perm_report_run)
            permissions.utils.grant_permission(tenant, role_admin_tenant, perm_manage_tenant)

            permissions.utils.grant_permission(tenant, role_external_provider, perm_patient_view)

