from django.core.exceptions import ObjectDoesNotExist
from django.conf.urls.defaults import url
from django.core.cache import cache
from django.core.urlresolvers import reverse
import isodate
from tastypie import fields
from tastypie.authentication import Authentication
from tastypie.authorization import ReadOnlyAuthorization
from tastypie.cache import SimpleCache
from tastypie.resources import Resource
from casexml.apps.case.models import CommCareCase
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
        if self.xmlns == "http://dev.commcarehq.org/pact/progress_note":
            if not self.form['note'].has_key('pact_id'):
                return '[no pact id]'
            elif self.form['note'].has_key('pact_id'):
                pact_id = self.form['note']['pact_id']
        else:
            if not self.form.has_key('pact_id'):
                return '[no pact id]'
            elif self.form.has_key('pact_id'):
                pact_id = self.form['pact_id']

        patient_doc = PactPatient.view('pactcarehq/patient_pact_ids', key=pact_id, include_docs=True).first()
        if patient_doc is None:
            return '[no patient with case]'
        return patient_doc


    @property
    def get_patient_name(self):
        patient_doc = self._get_patient_doc()
        if isinstance(patient_doc, str):
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
        started = self.get_form['meta']['timeStart']
        if isinstance(started, unicode) or isinstance(started, str):
            if len(started) == 0:
                return self.received_on
            started = isodate.parse_datetime("%sT%s" % (started.split(' ')[0], started.split(' ')[1]))
        return started


    @property
    def end_date(self):
        ended = self.get_form['meta']['timeEnd']
        if ended == '':
            #hack, touchforms doesn't seem to set a TimeEnd
            ended = self.received_on
        if isinstance(ended, unicode) or isinstance(ended, str):
            ended = isodate.parse_datetime("%sT%s" % (ended.split(' ')[0], ended.split(' ')[1]))
        return ended

    @property
    def encounter_date(self):
        date_string = ''

        if self.xmlns == 'http://dev.commcarehq.org/pact/dots_form':
            date_string = self.form['encounter_date']
        elif self.xmlns == "http://dev.commcarehq.org/pact/progress_note":
            date_string = self.form['note']['encounter_date']
        else:
            date_string = self.received_on
        return '%s <a href="%s">View</a>' % (date_string, reverse('show_submission', kwargs={'doc_id': self._id}))
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
        else:
            s = self.xmlns.split('/')
            return s[-1].replace('_', ' ').title()


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
            total_count =  self._meta.doc_class.view(self._meta.view_name, startkey=[kwargs['chw_username'], {}], endkey=[kwargs['chw_username'], None], descending=True).count()
        else:
            total_count =  self._meta.doc_class.view(self._meta.view_name).count()

        if cache.get('%s__%s' % (self._meta.resource_name, cache_key), None) is None:
            cache.set('%s__%s' % (self._meta.resource_name, cache_key), total_count, 300)
        return total_count

    def call_view(self, request, **kwargs):
        limit_option, skip_option = self._get_limit_skip(request)

        if request is not None and request.GET.get('username', None) is not None:
            startkey = [request.GET['username'], None]
            endkey = [request.GET['username'], {}]
            view = self._meta.doc_class.view(self._meta.view_name, include_docs=True, startkey=endkey, endkey=startkey, skip=skip_option, limit=limit_option, descending=True)
        else:
            view = self._meta.doc_class.view(self._meta.view_name, include_docs=True, skip=skip_option, limit=limit_option, descending=True)
        return view


    class Meta:
        view_name = "pactcarehq/all_submits_by_chw_date"
        doc_class = PactXForm
        resource_name = 'PactUserSubmissions'
        authorization = ReadOnlyAuthorization()
        paginator_class = CouchdbkitTastyPaginator
        authentication = Authentication()

