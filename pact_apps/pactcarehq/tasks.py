from datetime import timedelta, datetime
from celery.schedules import crontab
from django.contrib.auth.models import User
from django.core.cache import cache
from django.http import HttpResponse
import simplejson
from celery.decorators import task, periodic_task
import tempfile
import zipfile
import csv
from couchexport.export import export, Format
from pactcarehq.forms.weekly_schedule_form import hack_pact_usernames
from django.core.mail import send_mail

@task
def schema_export(namespace, download_id):
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


@task
def all_chw_submit_report(total_interval, download_id):
    from pactcarehq.views import _get_schedule_tally
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
    subject =  "CHW Scheduled submission report for %s" % (datetime.now().strftime("%A %B %d, %Y, %I:%M%p"))
    for user in users:
        ret, patients, total_scheduled, total_visited= _get_schedule_tally(user.username, total_interval)
        if total_scheduled > 0:
            scheduled.append("%s: %d/%d" % (user.username, total_visited, total_scheduled))
        else:
            unscheduled.append(user.username)


    body = '\n'.join([subject, '', 'Scheduled Today:\n', '\n'.join(scheduled), '\nNot Scheduled Today:\n', '\n'.join(unscheduled)])
    send_mail(subject, body, 'notifications@dimagi.com', ['dmyung@dimagi.com', 'CMCBEE@partners.org'], fail_silently=False)

