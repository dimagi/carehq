import pdb
import isodate
from tastypie import fields
from tastypie.authorization import ReadOnlyAuthorization
from couchforms.models import XFormInstance
from dimagi.utils.couch.tastykit import CouchdbkitResource, CouchdbkitTastyPaginator, DataTablesMixin
from pactpatient.models import PactPatient


class PactXForm(XFormInstance):
    def _stringify_delta(self, td):
        #where it's 0:07:06 H:M:S
        presplits = str(td).split(',')

        splits = presplits[-1].split(':')
        hours = int(splits[0])
        mins = int(splits[1])
        secs = float(splits[2])
        if secs > 30:
            mins+= 1
            secs = 0
        if mins > 30:
            hours += 1
            mins = 0
        newsplit = []
        days = False
        if len(presplits) == 2 and presplits[0] != "-1 day":
            #there's a day here
            newsplit.append(presplits[0])
            days=True

        if hours > 0:
            newsplit.append("%d hr" % (hours))
        if mins > 0 and days == False:
            newsplit.append("%d min" % (mins))
        return ', '.join(newsplit)

    @property
    def get_patient(self):
        if not self.form.has_key('case'):
            return None
        if not self.form['case'].has_key('case_id'):
            return None
        case_id = self.form['case']['case_id']

        #for dev purposes this needs to be done for testing
        #case_id = _hack_get_old_caseid(case_id)
#        if not patient_case_id_cache.has_key(case_id):
        patient = PactPatient.view('pactpatient/by_case_id', key=case_id, include_docs=True).first()
        #patient_case_id_cache[case_id]= patient
#        patient = patient_case_id_cache[case_id]
        return patient

    @property
    def start_date(self):
        started = self.get_form['Meta']['TimeStart']
        if isinstance(started, unicode):
            started = isodate.parse_datetime("%sT%s" % (started.split(' ')[0], started.split(' ')[1]))
        return started


    @property
    def end_date(self):
        ended = self.get_form['Meta']['TimeEnd']
        if ended == '':
            #hack, touchforms doesn't seem to set a TimeEnd
            ended = self.received_on
        if isinstance(ended, unicode):
            ended = isodate.parse_datetime("%sT%s" % (ended.split(' ')[0], ended.split(' ')[1]))
        return ended
    @property
    def encounter_date(self):
        if self.xmlns == 'http://dev.commcarehq.org/pact/dots_form':
            return self.form['encounter_date']
        elif self.xmlns == "http://dev.commcarehq.org/pact/progress_note":
            return self.form['note']['encounter_date']
        else:
            return self.received_on

    def start_to_finish(self):
        start_end = self._stringify_delta(self.end_date - self.start_date)
        return start_end

    def finish_to_submit(self):
        received = self['received_on']
        end_received = self._stringify_delta(received - self.end_date)
        return end_received
    def formtype_display(self):
        if self.xmlns == 'http://dev.commcarehq.org/pact/dots_form':
            return "DOTS"
        elif self.xmlns == "http://dev.commcarehq.org/pact/progress_note":
            return "Progress Note"


class ParameterizedResource(CouchdbkitResource):
    def get_object_list(self, request):
        """
        Assumes that the document type and the view correspond
        """
        limit_option, skip_option = self._get_limit_skip(request)
        results = self._meta.doc_class.view(self._meta.view_name, include_docs=True, limit=limit_option, skip=skip_option).all()
        return results

    def obj_get_list(self, request=None, **kwargs):
        limit_option, skip_option = self._get_limit_skip(request)
        results = self._meta.doc_class.view(self._meta.view_name, include_docs=True, key=request.user.username,  skip=skip_option, limit=limit_option).all()
        return results

    def obj_get(self, request=None, **kwargs):
        """
        Assume a fully formed couchdbkit document.
        """
        document = self._doctype().get(kwargs['pk'])
        return document
    def get_list(self, request, **kwargs):
        """
        Returns a serialized list of resources.

        Calls ``obj_get_list`` to provide the data, then handles that result
        set and serializes it.

        Should return a HttpResponse (200 OK).
        """
        # TODO: Uncached for now. Invalidation that works for everyone may be
        #       impossible.
        objects = self.obj_get_list(request=request, **self.remove_api_resource_names(kwargs))
        sorted_objects = self.apply_sorting(objects, options=request.GET)

        paginator = self._meta.paginator_class(request.GET, sorted_objects, resource_uri=self.get_resource_list_uri(), limit=self._meta.limit)
        to_be_serialized = paginator.page()
        to_be_serialized['aaData'] = to_be_serialized['objects']
        del(to_be_serialized['objects'])

        # Dehydrate the bundles in preparation for serialization.
        bundles = [self.build_bundle(obj=obj, request=request) for obj in to_be_serialized['aaData']]
        to_be_serialized['aaData'] = [self.full_dehydrate(bundle) for bundle in bundles]
        to_be_serialized = self.alter_list_data_to_serialize(request, to_be_serialized)
        return self.create_response(request, to_be_serialized)




class UserSubmissionResource(ParameterizedResource):
    doc_id = fields.CharField(attribute='get_id')
    last_name = fields.CharField(attribute='get_patient__last_name')
    first_name = fields.CharField(attribute='get_patient__first_name')
    formtype_display = fields.CharField(attribute='formtype_display')
    start_time = fields.DateTimeField(attribute='start_date')
    end_time = fields.DateTimeField(attribute='end_date')
    finish_interval = fields.CharField(attribute='start_to_finish')
    submit_interval = fields.CharField(attribute='finish_to_submit')
    encounter_date = fields.CharField(attribute='encounter_date')
    pact_id = fields.CharField(attribute='get_patient__pact_id')
    class Meta:
        view_name = "pactcarehq/all_submits"
        doc_class = PactXForm
        resource_name = 'PactUserSubmissions'
        authorization = ReadOnlyAuthorization()
        paginator_class=CouchdbkitTastyPaginator
        #authentication = Authentication()