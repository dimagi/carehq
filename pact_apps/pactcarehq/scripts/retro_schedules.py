from patient.models.djangomodels import Patient
from patient.models.couchmodels import CPatient, CDotWeeklySchedule
from datetime import datetime, timedelta

days_of_week = ['sunday','monday','tuesday','wednesday','thursday','friday','saturday']

def run():
    td = timedelta(days=365)
    for pt in Patient.objects.all():

        if len(pt.couchdoc.weekly_schedule) == 0:
            new_schedule = CDotWeeklySchedule()
            for sched in pt.couchdoc.dots_schedule:
                day_of_week = sched.day_of_week
                hp_username = sched.hp_username
                if hp_username != '':
                    new_schedule[day_of_week] = hp_username
            new_schedule.comment="Autogenerated retroactive 1 year from old schedule format."
            new_schedule.created_by='admin'
            new_schedule.edited_by='admin'
            new_schedule.started=datetime.now() - td
            pt.couchdoc.weekly_schedule.append(new_schedule)
            pt.couchdoc.save()

            print "Set retro schdule for %s" % (pt.couchdoc.pact_id)
