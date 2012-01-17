#nothing should be in here.
from django.conf.urls.defaults import include, patterns
from carehq_core.resources import ActorResource, IssueResource, PatientResource, IssueEventResource

issue_resource = IssueResource()
event_resource = IssueEventResource()
actor_resource = ActorResource()
patient_resource = PatientResource()

urlpatterns = patterns('',
    (r'^api/issue/', include(issue_resource.urls)),
    (r'^api/event/', include(event_resource.urls)),
    (r'^api/actor/', include(actor_resource.urls)),
    (r'^api/patient/', include(patient_resource.urls)),
)