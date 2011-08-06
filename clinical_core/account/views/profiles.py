

#profile management for a given user
from django.contrib.auth.decorators import login_required


@login_required
def request_profile(request, template="account/request_profile.html"):
    pass