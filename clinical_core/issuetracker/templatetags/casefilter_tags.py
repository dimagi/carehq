from django import template
from django.core.urlresolvers import reverse
from django.template.loader import render_to_string
from django.contrib.auth.models import User
from django.template import Context, Template

from issuetracker.models import Filter
from datetime import datetime

from django.db.models import Q

register = template.Library() 

@register.inclusion_tag('issuetracker/partials/issuefilter_menu.html')
def get_casefilters_for_user_ul(user):
    user_filters = Filter.objects.filter(Q(creator=user)).order_by('description')
    shared_filters = Filter.objects.filter(Q(shared=True)).order_by('description')
    return {'user_filters': user_filters, 'shared_filters': shared_filters}


