from django.db import models
#from userprofile.models import BaseProfile
from django.contrib.auth.models import User
from django.utils.translation import ugettext_lazy as _
from casetracker.models import  Filter


class FilterProfile(models.Model):
    """Proof of concept case/filter view stuff for user profile
    This will need to be replaced by a more sophisticated tracking (for login and sessions)
    as well as user profile management
    """
    user = models.ForeignKey(User, unique=True)
    last_filter = models.ForeignKey(Filter, null=True)
    last_login = models.DateTimeField()
    last_login_from = models.IPAddressField()



#We recognize this is a nasty practice to do an import, but we hate putting signal code
#at the bottom of models.py even more.
