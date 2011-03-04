from django import template
register = template.Library()

#http://squeeville.com/2009/01/27/django-templatetag-requestcontext-and-inclusion_tag/
@register.inclusion_tag('carehqapp/site_navigation_menu.html', takes_context=True)
def navigation_menu(context):
    newcontext = {}
    return context
