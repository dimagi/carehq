import permissions.utils
#todo hack: cross check these with localsetings hack_chw_username_phones
APP_PREFIX = 'carehq-'

#Tenant constants
TENANT_NAME = 'CAREHQ'
TENANT_PREFIX = 'carehq'
TENANT_FULL_NAME = "CareHQ Core"


### Role Constants
role_suspended = '%sSuspended' % APP_PREFIX

role_chw = '%sCHW' % APP_PREFIX
role_primary_chw = '%sPrimaryCHW' % APP_PREFIX
role_provider = '%sProvider' % APP_PREFIX
role_patient='%sPatient' % APP_PREFIX
role_caregiver='%sCaregiver' % APP_PREFIX
role_navigator='%sNavigator' % APP_PREFIX

role_admin_tenant = '%sAdminTenant' % APP_PREFIX #global admin for the entire operation

### Permission Constants
perm_noaccess = '%sNoAccess' % APP_PREFIX
perm_patient_view = '%sPatientView' % APP_PREFIX
perm_patient_edit = '%sPatientEdit' % APP_PREFIX

perm_chw_manage = '%sCHWManage' % APP_PREFIX
perm_report_view = '%sReportView' % APP_PREFIX
perm_report_run = '%sReportRun' % APP_PREFIX
perm_submit_patient_data = '%sSubmitPatientData' % APP_PREFIX
perm_edit_patient_data = '%sEditPatientData' % APP_PREFIX

perm_manage_tenant = '%sManageTenant' % APP_PREFIX

