from datetime import timedelta, datetime
from django.contrib.auth.models import User
from django.core.cache import cache
from django.http import HttpResponse
import simplejson
from celery.decorators import task
import tempfile
import zipfile
import csv
from pactcarehq.forms.weekly_schedule_form import hack_pact_usernames

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
    csv_writer.writerow(csv_keys)

    for user in users:
        username = user.username
        arr, patients, scheduled, visited = _get_schedule_tally(username, total_interval)
        for date, pt_visit in arr:
            if len(pt_visit) > 0:
                for cpt, v in pt_visit:
                    rowdata = [date.strftime('%Y-%m-%d'), username, cpt.pact_id]
                    if v != None:
                        if v.form['scheduled'] == 'yes':
                            rowdata.append('scheduled')
                        else:
                            rowdata.append('unscheduled')
                        rowdata.append(v.form['visit_type'])

                        rowdata.append(v.form['Meta']['username'])
                        if v.form['Meta']['username'] == username:
                            rowdata.append('assigned')
                        else:
                            rowdata.append('covered')
                        rowdata.append(v.get_id)
                    else:
                        rowdata.append('novisit')
                    #csvdata.append(','.join(rowdata))
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
