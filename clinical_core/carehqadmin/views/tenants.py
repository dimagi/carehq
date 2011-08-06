from django.shortcuts import render_to_response
from django.template.context import RequestContext
from patient.models.patientmodels import Patient
from permissions.models import ObjectPermission, Role, Permission, PrincipalRoleRelation
from tenant.models import Tenant, TenantActor
from pactconfig import constants as pactconstants

from django.contrib.contenttypes.models import ContentType

def manage_tenant(request, tenant_id, template="carehqadmin/tenants/manage_tenant.html"):
    """
    basic tenant manager
    """
    context = RequestContext(request)
    tenant = Tenant.objects.get(id=tenant_id)
    context['tenant'] = tenant

    ctype = ContentType.objects.get_for_model(tenant)

    operms = ObjectPermission.objects.filter(content_type=ctype, content_id=tenant_id)

    all_roles = Role.objects.all().filter(name__startswith=pactconstants.APP_PREFIX)
    all_permissions = Permission.objects.all().filter(codename__startswith=pactconstants.APP_PREFIX)

    role_permission_matrix = []
    for role in all_roles:
        perms = []
        for perm in all_permissions:
            if operms.filter(role=role, permission=perm).count() != 1:
                perms.append(None)
            else:
                perms.append(perm)
        role_permission_matrix.append((role, perms))

    context['role_permission_matrix'] = role_permission_matrix
    context['all_permissions'] = all_permissions

    actor_tenants = TenantActor.objects.all().filter(tenant=tenant)
    actor_roles = PrincipalRoleRelation.objects.all().filter(actor__in=actor_tenants.values_list('actor__id'))
    print actor_roles
    context['actor_roles'] = actor_roles

    for pt in Patient.objects.all():
        pass



    return render_to_response(template, context)
