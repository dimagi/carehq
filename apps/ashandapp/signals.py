from datetime import datetime
import logging

from django.db.models.signals import post_save, pre_save
from django.db.models import Q
from django.contrib.auth.models import User

from models import CareTeam, ProviderLink, CaregiverLink
from casetracker.models import Case, Category, Priority, Status, CaseTag
from casetracker import constants


def make_system_case(user, patient, role, link_object):
    case = Case()
    case.category=Category.objects.get(category='System')
    case.description = "%s added as %s to %s's careteam" % (user.get_full_name(), role, patient.user.get_full_name())
    case.body = "You have accepted the invitation to join this care team."
    case.opened_by = User.objects.get(username='ashand-system')
    case.opened_date = datetime.utcnow()
    
    case.last_edit_by = User.objects.get(username='ashand-system')
    case.priority= Priority.objects.get(id=6)
    case.status = Status.objects.filter(category=case.category).filter(state_class=constants.CASE_STATE_OPEN)[0] #get the default opener - this is a bit sketchy
    case.assigned_to = user
    case.save()
    ctag = CaseTag(case=case, content_object=link_object)
    ctag.save()
    return case
    

def caregiver_added(sender, instance, created, **kwargs):
    if created:
        case = make_system_case(instance.user, instance.careteam.patient, "caregiver", instance)
        instance.careteam.add_case(case)
    

def provider_added(sender, instance, created, **kwargs):
    if created:
        case = make_system_case(instance.provider.user, instance.careteam.patient, "provider", instance)
        instance.careteam.add_case(case)

#post_save.connect(caregiver_added, sender=CaregiverLink)
#post_save.connect(provider_added, sender=ProviderLink)

