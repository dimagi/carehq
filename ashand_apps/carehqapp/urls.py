from django.conf.urls.defaults import *
from carehqapp.views.patient_views import CarehqPatientSingleView

urlpatterns = patterns('carehqapp.views',
        #url(r'^$', 'home.home_view', name='home'),


        (r'^uptime$', 'pingdom.uptime'),



        url(r'^$', 'dashboard.home_news', name='home'),
        url(r'^user/noprofile$', 'account.no_actor', name='no_actor_profile'),

        url(r'^issue/(?P<issue_id>[0-9a-z]{32})$', 'issues.manage_issue', name="manage-issue"),
        url(r'^issues/$', 'issues.issue_home', name='issue_home'),
        url(r'^issues/(?P<issue_filter>.*)/$', 'issues.issue_filter', name='issue_filter'),
        #url(r'^careplan/edit/(?P<user_id>.*)$', 'careplan.edit_careplan', name='edit_careplan'),
        #url(r'^careplan/(?P<user_id>.*)$', 'careplan.careplan', name='careplan'),
        url(r'^data/careinnovation/ccd.html$', 'ccdreceiver.receive_ccd'), #receive care innovation ccd

        url(r'^data/ccd/(?P<doc_id>[0-9a-z]{32})$', 'ccdreceiver.view_ccd', name="view_ccd"),
        url(r'^data/ccd/(?P<doc_id>[0-9a-z]{32})/recompute$', 'ccdreceiver.recompute_submission', name="recompute_submission"),


        url(r'^patient/view/(?P<patient_guid>[0-9a-fA-Z]{25,32})/(?P<view_mode>\w*)$', CarehqPatientSingleView.as_view(template_name='carehqapp/patient/carehq_patient_base.html'), name='patient_url'),
        url(r'^patient/api/(?P<patient_guid>[0-9a-fA-Z]{25,32})/actor/add$', 'actors.pt_new_or_link_actor', name='pt_new_or_link_actor'),
        url(r'^patient/api/(?P<patient_guid>[0-9a-fA-Z]{25,32})/files$', 'patient_views.upload_patient_attachment', name='pt_manage_files'),
        url(r'^home/mycare/', CarehqPatientSingleView.as_view(template_name='carehqapp/carehq_patient_base.html'), name='patient_home'),


        url(r'^network/$', 'network_views.my_network', name='my_network'),
        url(r'^network/mypatients/$', 'network_views.my_patients', name='my_patients'),
        url(r'^network/mycareteam/$', 'network_views.my_careteam', name='my_careteam'),

        #url(r'^pact/providers$', 'pactcarehq.views.providers.view_add_pact_provider', name="pact_providers"),
        #url(r'^carehq/api/provider/(?P<provider_guid>[0-9a-fA-Z]{25,32})/edit$', 'pactcarehq.views.providers.edit_provider', name='pact_edit_provider'),

        url(r'^issue/patient/(?P<patient_guid>[0-9a-fA-Z]{25,32})/new$', 'issues.new_issue_patient', name='new_carehq_patient_issue'),

        url(r'^patient/api/careteam/actor/rm$', 'actors.rm_actor_from_patient', name='rm_actor_from_patient'),
        url(r'^patient/api/careteam/actor/add$', 'actors.do_add_actor_to_patient', name='link_actor_to_patient'),
        url(r'^actor/api/rm$', 'actors.rm_actor', name='rm_ashand_actor'),

        url(r'^ashandadmin/$', 'ashand_admin.admin_study_landing'),
        url(r'^ashandadmin/ccds/$', 'ashand_admin.admin_ccd_submissions'),
        url(r'^ashandadmin/patients/$', 'ashand_admin.admin_patient_list'),
        url(r'^ashandadmin/user/activate/(?P<user_id>\d+)$', 'ashand_admin.admin_invite_activate_actor_user'),



#        url(r'^addProvider/?$', 'ashandui.addProvider', name='addProvider'),
#        url(r'^providerSearchAjax/?$', 'ashandui.providerSearchAjax', name='providerSearchAjax'),
#        url(r'^providerListQueryAjax/(?P<term>.*)$', 'ashandui.providerListQueryAjax', name='providerListQueryAjax'),
#        url(r'^providerSearch/?$', 'ashandui.providerSearch', name='providerSearch'),
#        url(r'^providerPatients/(?P<doctorId>[0-9a-f]{32})$', 'ashandui.providerPatients'),
#        url(r'^linkProvider/(?P<patientId>[0-9a-f]{32})?$', 'ashandui.editCareteam', name='linkProvider'),

        url(r'^actors/(?P<actor_doc_id>[0-9a-f]{32})/(?P<view_mode>\w*)$', 'actors.view_actor', name='view_actor'),
        url(r'^carehq/ajax/getpatientform/$', 'ajax.ajax_patient_form_get', name='ajax_patient_form_get'),
        url(r'^carehq/ajax/postpatientform/(?P<patient_guid>[0-9a-fA-Z]{25,32})/(?P<form_name>.*)/$', 'ajax.ajax_post_patient_form', name='ajax_post_patient_form'),
        url(r'^carehq/ajax/phone$', 'ajax.remove_phone', name='remove_phone'),
        url(r'^carehq/ajax/address$', 'ajax.remove_address', name='remove_address'),

        url(r'^carehq/ajax/getactorform/$', 'ajax.ajax_get_actor_form', name='ajax_get_actor_form'),
        url(r'^carehq/ajax/postactorform/(?P<doc_id>[0-9a-fA-Z]{25,32})/(?P<form_name>.*)/$', 'ajax.ajax_post_actor_form', name='ajax_post_actor_form'),






#
#    (r'^my_admin/jsi18n', 'django.views.i18n.javascript_catalog'),
#
#    #main navigation tabs
#    url(r'^$', 'ashandapp.views.filters.list_issues', name='list_issues'),
#    url(r'^tabbed/json/$', 'ashandapp.views.dashboard.get_json_for_paging', name='json_string'),
#
#    #generic json case queryset
#    url(r'^grid/issues/(?P<content_type_name>.*)/(?P<content_uuid>[0-9a-f]{32})$', 'ashandapp.views.issues.queries.grid_issues_for_object', name='issues-for-obj-view'),
#
#    #specific grid views by user login
#    url(r'^grid/issues/provider$', 'ashandapp.views.issues.queries.grid_provider_patient_issues', name='grid_provider_patient_issues'),
#    url(r'^grid/issues/triage$', 'ashandapp.views.issues.queries.grid_triage_issues', name='grid_triage_issues'),
#    url(r'^grid/issues/caregiver$', 'ashandapp.views.issues.queries.grid_caregiver_issues', name='grid_caregiver_issues'),
#    url(r'^grid/issues/recent$', 'ashandapp.views.issues.queries.grid_recent_activity', name='grid_recent_activity'),
#
#
#
#    url(r'^profile/$', 'ashandapp.views.users.my_profile', name="my_profile"),
#    url(r'^careteam/mine/$', 'ashandapp.views.careteam.network.my_careteam', name='my_careteam'),
#    url(r'^patients/mine/$', 'ashandapp.views.careteam.network.my_patients', name='my_patients'),
#    url(r'^recipients/$', 'ashandapp.views.careteam.network.my_care_recipients', name='my_care_recipients'),
#
#    url(r'^mobile/caselist$', 'ashandapp.views.mobile.issue_home', name='mobile_issue_list'),
#    url(r'^mobile/newprovider', 'ashandapp.views.mobile.new_provider', name='new_provider'),
#
#    url(r'^careteam/(?P<careteam_id>[0-9a-f]{32})/issues$', 'carehqapp.views.careteam.ajax.view_careteam_issues', name='careteam-issues-tabpage'),
#    url(r'^grid/careteam/(?P<careteam_id>[0-9a-f]{32})/issues$', 'ashandapp.views.issues.queries.grid_careteam_issues', name='careteam-issues-grid'),
#
#
#    #careteam specific links
#    url(r'^careteam/(?P<careteam_id>[0-9a-f]{32})$', 'carehqapp.views.careteam.single', name='view-careteam'),
#    url(r'^careteam/(?P<careteam_id>[0-9a-f]{32})/careplan$', 'carehqapp.views.careteam.single_template_careplan', name='view-careteam-careplan'),
#    url(r'^careteam/(?P<careteam_id>[0-9a-f]{32})/history$', 'carehqapp.views.careteam.single_history', name='view-careteam-history'),
#
#    (r'^careteam/(?P<careteam_id>[0-9a-f]{32})/new/question$', 'ashandapp.views.issues.create.new_question'),
#    (r'^careteam/(?P<careteam_id>[0-9a-f]{32})/new/issue$', 'ashandapp.views.issues.create.new_issue'),

)    
    
