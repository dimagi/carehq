import permissions.utils
hack_pact_usernames = ['-- unassigned --', u'ac381', u'an907', u'ao970', u'cm326', u'cs783', u'godfrey', u'ink', u'ink2', u'isaac', u'lm723', u'lnb9', u'ma651', u'nc903', u'rachel', u'ss524','gj093']
APP_PREFIX = 'pact-'

#Tenant constants
TENANT_NAME = 'PACT'
TENANT_PREFIX = 'pact'
TENANT_FULL_NAME = "Prevention and Access to Care and Treatment"


### Role Constants
role_suspended = '%sSuspended' % (APP_PREFIX)

role_chw = '%sCHW' % (APP_PREFIX)
role_primary_chw = '%sPrimaryCHW' % (APP_PREFIX)
role_external_provider = '%sExternalProvider' % (APP_PREFIX)
role_admin_tenant = '%sAdminTenant' % (APP_PREFIX) #global admin for the entire operation

#role_chw_dot = '%sCHWDOT' % (APP_PREFIX)
#role_chw_hp = '%sCHWHP' % (APP_PREFIX)
#
#role_provider = '%sExternalProvider' % (APP_PREFIX)
#role_pact_provider = '%sPactProvider' % (APP_PREFIX)
#role_admin_dot = '%sAdminDot' % (APP_PREFIX)
#role_admin_hp = '%sAdminHP' % (APP_PREFIX)
#role_admin_data = '%sAdminData' % (APP_PREFIX)
#role_admin_domain = '%sAdminTenant' % (APP_PREFIX) #global admin for the entire operation

### Permission Constants
perm_noaccess = '%sNoAccess' % (APP_PREFIX)
perm_patient_view = '%sPatientView' % (APP_PREFIX)
perm_patient_edit = '%sPatientEdit' % (APP_PREFIX)


perm_chw_manage = '%sCHWManage' % (APP_PREFIX)
perm_report_view = '%sReportView' % (APP_PREFIX)
perm_report_run = '%sReportRun' % (APP_PREFIX)
perm_submit_patient_data = '%sSubmitPatientData' % (APP_PREFIX)
perm_edit_patient_data = '%sEditPatientData' % (APP_PREFIX)

perm_manage_tenant = '%sManageTenant' % (APP_PREFIX)

