from auditcare.models import AuditEvent
from couchforms.models import XFormInstance
from couchlog.models import ExceptionRecord
from pillowtop.listener import NetworkPillow, BasicPillow
import settings


class AuditcarePillow(NetworkPillow):
    endpoint_host = settings.LOGSTASH_HOST
    endpoint_port = settings.LOGSTASH_PORT
    couch_db = AuditEvent.get_db()
    couch_filter = 'filters/auditdocs'

class CouchlogPillow(NetworkPillow):
    endpoint_host = settings.LOGSTASH_HOST
    endpoint_port = settings.LOGSTASH_PORT
    couch_db = ExceptionRecord.get_db()
    couch_filter = 'filters/couchlogs'

class DevicelogPillow(NetworkPillow):
    endpoint_host = settings.LOGSTASH_HOST
    endpoint_port = settings.LOGSTASH_PORT
    couch_db = XFormInstance.get_db()
    couch_filter = 'filters/devicelogs'

