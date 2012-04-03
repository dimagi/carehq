from django.conf.urls.defaults import url
from django.core.cache import cache
from django.core.urlresolvers import reverse
import isodate
from tastypie import fields
from tastypie.authentication import Authentication
from tastypie.authorization import ReadOnlyAuthorization
from tastypie.cache import SimpleCache
from couchforms.models import XFormInstance
from dimagi.utils.couch.tastykit import  CouchdbkitTastyPaginator, CouchdbkitResource
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
            mins += 1
            secs = 0
        if mins > 30:
            hours += 1
            mins = 0
        newsplit = []
        days = False
        if len(presplits) == 2 and presplits[0] != "-1 day":
            #there's a day here
            newsplit.append(presplits[0])
            days = True

        if hours > 0:
            newsplit.append("%d hr" % (hours))
        if mins > 0 and days == False:
            newsplit.append("%d min" % (mins))
        return ', '.join(newsplit)


    def _get_patient_doc(self):
        print "_get_patient_doc"
        if not self.form.has_key('case'):
            print "no case block"
            return '[no case block]'
        if not self.form['case'].has_key('case_id'):
            print "no case id"
            return '[no case id]'
        case_id = self.form['case']['case_id']
        print "got case_id"

        #for dev purposes this needs to be done for testing
        #case_id = _hack_get_old_caseid(case_id)
        #        if not patient_case_id_cache.has_key(case_id):
        patient_doc = PactPatient.view('pactpatient/by_case_id', key=case_id, include_docs=True).first()
        if patient_doc is None:
            print "no patient with case"
            return '[no patient with case]'
        print "got patient doc"
        return patient_doc


    @property
    def get_patient_name(self):
        patient_doc = self._get_patient_doc()
        if isinstance(patient_doc, str):
            print "returning: %s" % patient_doc
            return patient_doc
        return '<a href="%s">%s, %s</a>' % (reverse('view_pactpatient', kwargs={"patient_guid": patient_doc.get_id, 'view_mode': ''}), patient_doc.last_name, patient_doc.first_name)


    @property
    def get_pact_id(self):
        patient_doc = self._get_patient_doc()
        if isinstance(patient_doc, str):
            return patient_doc
        return patient_doc.pact_id

    @property
    def start_date(self):
        started = self.get_form['Meta']['TimeStart']
        if isinstance(started, unicode) or isinstance(started, str):
            if len(started) == 0:
                return self.received_on
            started = isodate.parse_datetime("%sT%s" % (started.split(' ')[0], started.split(' ')[1]))
        return started


    @property
    def end_date(self):
        ended = self.get_form['Meta']['TimeEnd']
        if ended == '':
            #hack, touchforms doesn't seem to set a TimeEnd
            ended = self.received_on
        if isinstance(ended, unicode) or isinstance(ended, str):
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


class UserSubmissionResource(CouchdbkitResource):
    doc_id = fields.CharField(attribute='get_id')
    pact_id = fields.CharField(attribute='get_pact_id')
    patient = fields.CharField(attribute='get_patient_name')
    formtype_display = fields.CharField(attribute='formtype_display')
    start_date = fields.DateTimeField(attribute='start_date')
    end_time = fields.DateTimeField(attribute='end_date')
    finish_interval = fields.CharField(attribute='start_to_finish')
    submit_interval = fields.CharField(attribute='finish_to_submit')
    encounter_date = fields.CharField(attribute='encounter_date')
    received_on = fields.DateTimeField(attribute='received_on')
    #pact_id = fields.CharField(attribute='get_patient__pact_id')


    def override_urls(self):
        return [
            url(r'^(?P<resource_name>%s)/chw/(?P<chw_username>.*)/' % self._meta.resource_name, self.wrap_view('dispatch_list'), name='api_dispatch_chw_list'),
            #url(r"^(?P<resource_name>%s)/(?P<username>[\w\d_.-]+)/$" % self._meta.resource_name, self.wrap_view('dispatch_detail'), name="api_dispatch_detail"),

        ]

    def obj_get_list(self, request=None, **kwargs):
        """
        Assumes that the document type and the view correspond
        """
        #tune the limits for couch instead of grabbing everything

        results = self.call_view(request, **kwargs).all()
        return sorted(results, key=lambda x: x.received_on, reverse=True)


    def compute_totals(self, request, **kwargs):
        """
        """
        cache_key = self.generate_cache_key(**kwargs)

        if kwargs.get('chw_username', None) is not None:
            total_count =  self._meta.doc_class.view(self._meta.view_name, key=kwargs['chw_username'], reduce=True)
        else:
            total_count =  self._meta.doc_class.view(self._meta.view_name).count()

        if cache.get('%s__%s' % (self._meta.resource_name, cache_key), None) is None:
            cache.set('%s__%s' % (self._meta.resource_name, cache_key), total_count, 300)
        return total_count

    def call_view(self, request, **kwargs):
        limit_option, skip_option = self._get_limit_skip(request)

        if request is not None and request.GET.get('username', None) is not None:
            key = request.GET['username']
            view = self._meta.doc_class.view(self._meta.view_name, key=key, skip=skip_option, limit=limit_option, reduce=False)
        else:
            view = self._meta.doc_class.view(self._meta.view_name, skip=skip_option, reduce=False, limit=limit_option)
        return view


    class Meta:
        view_name = "pactcarehq/chw_dashboard"
        doc_class = PactXForm
        resource_name = 'PactUserSubmissions'
        authorization = ReadOnlyAuthorization()
        paginator_class = CouchdbkitTastyPaginator
        authentication = Authentication()
