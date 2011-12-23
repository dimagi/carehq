import permissions.utils
#todo hack: cross check these with localsetings hack_chw_username_phones
APP_NAMESPACE = 'carehq'

#Tenant constants
TENANT_NAME = 'CAREHQ'
TENANT_PREFIX = 'carehq'
TENANT_FULL_NAME = "CareHQ Core"

### Universal Role Constants
role_suspended = '.'.join([APP_NAMESPACE,'Suspended'])

role_chw = '.'.join([APP_NAMESPACE,'CHW'])
role_primary_chw = '.'.join([APP_NAMESPACE,'PrimaryCHW'])
role_provider = '.'.join([APP_NAMESPACE,'Provider'])
role_external_provider = '.'.join([APP_NAMESPACE, 'Provider','External'])
role_patient= '.'.join([APP_NAMESPACE,'Patient'])
role_caregiver= '.'.join([APP_NAMESPACE,'Caregiver'])
role_navigator= '.'.join([APP_NAMESPACE,'Navigator'])

role_admin_tenant = '.'.join([APP_NAMESPACE, 'AdminTenant'])  #global admin for the entire operation

### Permission Constants
perm_noaccess = '.'.join([APP_NAMESPACE, 'NoAccess'])
perm_patient_view = '.'.join([APP_NAMESPACE, 'Patient','View'])
perm_patient_edit = '.'.join([APP_NAMESPACE, 'Patient','Edit']) #edit patient data - address info, or careteam membership!

perm_chw_manage = '.'.join([APP_NAMESPACE, 'CHW','Manage'])
perm_report_view = '.'.join([APP_NAMESPACE, 'Report','View'])
perm_report_run = '.'.join([APP_NAMESPACE, 'Report','Run'])

perm_submit_patient_data = '.'.join([APP_NAMESPACE, 'PatientData','Submit'])
perm_edit_patient_data = '.'.join([APP_NAMESPACE, 'PatientData','Edit'])

perm_create_issue = '.'.join([APP_NAMESPACE,'Issue','Create'])
perm_edit_issue = '.'.join([APP_NAMESPACE,'Issue','Edit'])
perm_update_issue = '.'.join([APP_NAMESPACE,'Issue','Update'])
perm_resolve_issue = '.'.join([APP_NAMESPACE,'Issue','Resolve'])
perm_close_issue = '.'.join([APP_NAMESPACE,'Issue','Close'])

perm_manage_tenant = '.'.join([APP_NAMESPACE, 'Tenant','Manage'])

