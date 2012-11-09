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

from django.conf import settings
from couchforms.models import XFormInstance
from pillowtop.listener import ElasticPillow


class PactFormsPillow(ElasticPillow):
    couch_db = XFormInstance.get_db()
    couch_filter = "couchforms/xforms"
    es_host = settings.ELASTICSEARCH_HOST
    es_port = settings.ELASTICSEARCH_PORT
    es_index = "pactxforms"
    es_type = "xform"

    es_meta = {
        "mappings": {
            "xform": {
                "date_detection": False,
                "properties": {
                    "xmlns": {
                        "type": "multi_field",
                        "fields": {
                            "xmlns": {"type": "string", "index": "analyzed"},
                            "exact": {"type": "string", "index": "not_analyzed"}
                        }
                    },
                    "received_on": {
                        "format": "dateOptionalTime",
                        "type": "date"
                    },

#                    "encounter_date": {"type": "string", "index": "not_analyzed"},
                    'form': {
                        'properties': {
                            "encounter_date": {
                                "format": "dateOptionalTime",
                                "type": "date"
                            },
                            'meta': {
                                'properties': {
                                    "timeStart": {
                                        "format": "dateOptionalTime",
                                        "type": "date"
                                    },
                                    #                                    "timeEnd": {
                                    #                                        "format": "dateOptionalTime",
                                    #                                        "type": "date"
                                    #                                    },
                                    "userID": {"type": "string", "index": "not_analyzed"},
                                    "deviceID": {"type": "string", "index": "not_analyzed"},
                                    "instanceID": {"type": "string", "index": "not_analyzed"}
                                }}, }, },

                }}}}

    def change_transform(self, doc_dict):
        print "%s : %s" % (doc_dict['_id'], doc_dict['xmlns'])
        #        print doc_dict.get('form', {}).keys()

        keep_form_fields = [
            'meta', 'Meta', 'pact_id',
            'encounter_date',
            'notes',
            'scheduled',
            'visit_type',
            'visit_kept',
#            'question',
            'observed_art',
            'observed_non_art',
            'observed_non_art_dose',
            'contact_type'
        ]
        for k in doc_dict['form'].keys():
            if k not in keep_form_fields:
                del doc_dict['form'][k]

        if doc_dict.has_key('_attachments'):
            del doc_dict['_attachments']

        if doc_dict.has_key('pact_data'):
            del doc_dict['pact_data']

        #        if doc_dict.has_key('form'):
        #            for k in doc_dict['form'].keys():
        #                if k[0] == '@':
        #                    del doc_dict['form'][k]
#        print doc_dict
        return doc_dict
