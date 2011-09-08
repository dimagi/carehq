from datetime import timedelta, datetime
from celery.schedules import crontab
from django.contrib.auth.models import User
from django.core.cache import cache
from django.core.urlresolvers import reverse
from django.http import HttpResponse
import simplejson
from celery.decorators import task, periodic_task
import tempfile
import zipfile
import csv
import logging
from couchexport.export import export, Format
from couchforms.models import XFormInstance
from pactcarehq.forms.weekly_schedule_form import hack_pact_usernames
from django.core.mail import send_mail

hack_chw_username_phones = {
    'ss524': '6178168512@vtext.com',
    'lm723': '6175434561@vtext.com',
    'an907': '6178941127@vtext.com',
    'lnb9':  '6178944627@vtext.com',
    'ma651': '6176509230@vtext.com',
    'ac381': '6179218161@vtext.com',
    'cs783': '6178168506@vtext.com',
    'ao970': '6178168507@vtext.com',
    'nc903': '6173788671@vtext.com',
    'isaac': '6174597765@vtext.com',
    'ss192': '6175127114@vtext.com',
    #'clare': '6175298471@vtext.com',
    'asc30': '6175298471@vtext.com',
}



@task
def schema_export(namespace, download_id, email=None):
    cache_container = {}
    tmp = tempfile.NamedTemporaryFile(suffix='.xls', delete=False)
    if export(namespace, tmp, format=Format.XLS):
        cache_container['mimetype'] = 'application/vnd.ms-excel'
        cache_container['Content-Disposition'] = 'attachment; filename=%s.xls' % namespace
        cache_container['location'] = tmp.name
        tmp.close()
    else:
        cache_container = {}
        cache_container['mimetype'] = 'text/plain'
        cache_container['location'] = None
        cache_container['message'] = "No data due to an error generating the file"
    cache.set(download_id, simplejson.dumps(cache_container), 86400)

    if email != None:
        subject = "[CareHQ] Your requested file download is ready"
        url = "https://pact.dimagi.com" + reverse('retrieve_download', kwargs={'download_id': download_id})
        body = '\n'.join(['To retrieve your document log into CareHQ and visit the URL below.', url])
        send_mail(subject, body, 'notifications@dimagi.com', [email], fail_silently=True)


@task
def all_chw_submit_report(total_interval, download_id):
    from pactcarehq.views.schedule_views import _get_schedule_tally
    users = User.objects.all().filter(username__in=hack_pact_usernames)
    all_data = {}
    cache_container = {}
    cache_container['mimetype'] = 'application/zip'
    temp_csv = tempfile.TemporaryFile()
    csv_writer = csv.writer(temp_csv, dialect=csv.excel)

    csv_filename = "chw_schedule_report-%s-%d_days.csv" % (datetime.utcnow().strftime("%Y-%m-%d"), total_interval)
    csv_keys = ['visit_date','assigned_chw','scheduled_pact_id','is_scheduled','visit_type','submitted_by','visit_id']
    csv_keys = ['visit_date','assigned_chw','pact_id','is_scheduled','contact_type', 'visit_type','visit_kept', 'submitted_by','visit_id']
    csv_writer.writerow(csv_keys)

    for user in users:
        username = user.username
        arr, patients, scheduled, visited = _get_schedule_tally(username, total_interval)
        for date, pt_visit in arr:
            if len(pt_visit) > 0:
                for cpt, v in pt_visit:
                    rowdata = [date.strftime('%Y-%m-%d'), username, cpt.pact_id]
                    if v != None:
                        #is scheduled
                        if v.form['scheduled'] == 'yes':
                            rowdata.append('scheduled')
                        else:
                            rowdata.append('unscheduled')
                        #contact_type
                        rowdata.append(v.form['contact_type'])

                        #visit type
                        rowdata.append(v.form['visit_type'])

                        #visit kept
                        rowdata.append(v.form['visit_kept'])

                        rowdata.append(v.form['Meta']['username'])
                        if v.form['Meta']['username'] == username:
                            rowdata.append('assigned')
                        else:
                            rowdata.append('covered')
                        rowdata.append(v.get_id)
                    else:
                        rowdata.append('novisit')
                    csv_writer.writerow(rowdata)
            else:
                #csvdata.append(','.join([date.strftime('%Y-%m-%d'),'nopatients']))
                csv_writer.writerow([date.strftime('%Y-%m-%d'), username,'nopatients'])
    temp_csv.seek(0)
    temp_zip = tempfile.NamedTemporaryFile(suffix='.zip', delete=False)

    cache_container['location'] = temp_zip.name
    cache_container['Content-Disposition'] = 'attachment; filename=%s.zip' % (csv_filename)

    zip_file = zipfile.ZipFile(temp_zip, 'w', zipfile.ZIP_DEFLATED)
    zip_file.writestr(csv_filename, temp_csv.read())
    temp_csv.close()

    zip_file.close()
    temp_zip.close()
    cache.set(download_id, simplejson.dumps(cache_container), 86400)


@periodic_task(run_every=crontab(hour=23, minute=59))
def prime_views():
    """
    Cheater function to hit certain key views in pact so as to keep the view index refreshes low.
    """
    db = XFormInstance.get_db()
    schema_index = "http://dev.commcarehq.org/pact/progress_note"
    db.view("couchexport/schema_index", key=schema_index, include_docs=True, limit=5).all()
    logging.debug("Primed couchexport/schema_index")

    db.view("dotsview/dots_observations", limit=5).all()
    logging.debug("Primed dotsview/dots_observations")

    db.view("pactcarehq/all_dots", limit=5).all()
    logging.debug("Primed pactcarehq views")

    db.view("pactcarehq/all_dots", limit=5).all()
    logging.debug("Primed pactcarehq views")

    db.view("pactpatient/by_case_id", limit=5).all()
    logging.debug("Primed pactpatient views")

    db.view("pactpatient/by_case_id", limit=5).all()
    logging.debug("Primed pactpatient views")

    db.view("patient/all", limit=5).all()
    logging.debug("Primed patient views")

    db.view("case/by_last_date", limit=5).all()
    logging.debug("Primed case views")

    db.view("auditcare/by_date", limit=5).all()
    logging.debug("Primed auditcare views")




@periodic_task(run_every=crontab(minute=30, hour=15))
#@periodic_task(run_every=crontab(hour="*", minute="*", day_of_week="*"))
def schedule_coverage_tally_report():
    """scheduled tally for all CHWs sms'ed via email"""
    from pactcarehq.views import _get_schedule_tally
    #for each CHW
    #do a single date query for dateitme.today(), get the num actual vs. expected
    #ping chw with text message
    #then append to email message to clare

    users = sorted(filter(lambda x: x.username.count("_") == 0, User.objects.all().filter(is_active=True)), key=lambda x: x.username)
    total_interval = 1
    scheduled = []
    unscheduled = []
    subject =  "CHW consolidated submission report for %s" % (datetime.now().strftime("%A %B %d, %Y, %I:%M%p"))
    for user in users:
        ret, patients, total_scheduled, total_visited= _get_schedule_tally(user.username, total_interval)
        if total_scheduled > 0:
            scheduled.append("%s: %d/%d" % (user.username, total_visited, total_scheduled))
        else:
            unscheduled.append(user.username)


    body = '\n'.join([subject, '', 'Scheduled Today:\n', '\n'.join(scheduled), '\nNot Scheduled Today:\n', '\n'.join(unscheduled)])
    send_mail(subject, body, 'notifications@dimagi.com', ['pact-monitoring@dimagi.com'], fail_silently=True)


@periodic_task(run_every=crontab(minute=00, hour=15))
def schedule_coverage_tally_report_sms():
    """scheduled tally for all CHWs sms'ed via SMS email"""
    from pactcarehq.views import _get_schedule_tally
    #for each CHW
    #do a single date query for dateitme.today(), get the num actual vs. expected
    #ping chw with text message
    #then append to email message to clare

    users = sorted(filter(lambda x: x.username.count("_") == 0, User.objects.all().filter(is_active=True)), key=lambda x: x.username)
    total_interval = 1
    scheduled = []
    unscheduled = []
    for user in users:
        if user.username.lower() in hack_chw_username_phones:
            ret, patients, total_scheduled, total_visited= _get_schedule_tally(user.username, total_interval)
            if total_scheduled > 0:
                if total_visited == total_scheduled:
                    message_text = "You have submitted data for all %d of your patients today, great!" % (total_scheduled)
                    continue
                else:
                    message_text = "Today you have submitted %d of your %d scheduled patient visits." % (total_visited, total_scheduled)
                message_text += " To see your full schedule visit https://pact.dimagi.com/schedules/chw/%s" % (user.username.lower())
                send_mail('', message_text, 'notifications@dimagi.com', [hack_chw_username_phones[user.username.lower()]], fail_silently=True)

