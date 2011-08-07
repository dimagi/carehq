import permissions.utils
APP_PREFIX = 'ashand-'

#Tenant constants
TENANT_NAME = 'ASHAND'
TENANT_PREFIX = 'ashand'
TENANT_FULL_NAME = "ASHAND Prototype 3"


### Role Constants
role_suspended = '%sSuspended' % (APP_PREFIX)

role_caregiver = '%sCaregiver' % (APP_PREFIX)
role_primary_provider = '%sPrimaryProvider' % (APP_PREFIX)
role_provider = '%sExternalProvider' % (APP_PREFIX)
role_admin_tenant = '%sAdminTenant' % (APP_PREFIX) #global admin for the entire operation

### Permission Constants
perm_noaccess = '%sNoAccess' % (APP_PREFIX)
perm_patient_view = '%sPatientView' % (APP_PREFIX)
perm_patient_edit = '%sPatientEdit' % (APP_PREFIX)

perm_submit_patient_data = '%sSubmitPatientData' % (APP_PREFIX)
perm_edit_patient_data = '%sEditPatientData' % (APP_PREFIX)

perm_manage_tenant = '%sManageTenant' % (APP_PREFIX)

