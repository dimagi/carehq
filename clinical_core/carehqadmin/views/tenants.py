from django.shortcuts import render_to_response
from django.template.context import RequestContext
from carehq_core import carehq_constants
from patient.models.patientmodels import Patient
from permissions.models import ObjectPermission, Role, Permission, PrincipalRoleRelation
from tenant.models import Tenant, TenantActor

from django.contrib.contenttypes.models import ContentType

def manage_tenant(request, tenant_id, template="carehqadmin/tenants/manage_tenant.html"):
    """
    basic tenant manager
    """
    context = RequestContext(request)
    tenant = Tenant.objects.get(id=tenant_id)
    context['tenant'] = tenant

    ctype = ContentType.objects.get_for_model(tenant)

    operms = ObjectPermission.objects.select_related('content_type').filter(content_type=ctype, content_id=tenant_id)

    all_roles = Role.objects.all().filter(name__startswith=carehq_constants.APP_NAMESPACE)
    all_permissions = Permission.objects.all().select_related().filter(codename__startswith=carehq_constants.APP_NAMESPACE)

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

    tenant_actors = TenantActor.objects.all().filter(tenant=tenant).select_related('actor', 'actor__principalrolerelation')
    actors = [x.actor for x in tenant_actors]
    #actor_roles = PrincipalRoleRelation.objects.all().filter(actor__in=tenant_actors.values_list('actor__id'))
    context['tenant_actors'] = actors

    for pt in Patient.objects.all():
        pass
    return render_to_response(template, context)



def manage_tenant_users(request, tenant_id, template="carehqadmin/tenants/manage_tenant_users.html"):
    context = RequestContext(request)
    tenant = Tenant.objects.get(id=tenant_id)
    context['tenant'] = tenant
    tenant_users = TenantActor.objects.filter(tenant=tenant).exclude(actor__user=None)
    context['tenant_users'] = [x.actor.user for x in tenant_users]

    return render_to_response(template, context)


