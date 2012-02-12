"""

modified, custom django-registration defaults.

URLconf for registration and activation, using django-registration's
default backend.

If the default behavior of these views is acceptable to you, simply
use a line like this in your root URLconf to set up the default URLs
for registration::

    (r'^accounts/', include('registration.backends.default.urls')),

This will also automatically set up the views in
``django.contrib.auth`` at sensible default locations.

If you'd like to customize the behavior (e.g., by passing extra
arguments to the various views) or split up the URLs, feel free to set
up your own URL patterns for these views instead.

"""


from django.conf.urls.defaults import *
from django.views.generic.simple import direct_to_template

from registration.views import activate
from registration.views import register
from django.contrib.auth import views as auth_views


urlpatterns = patterns('',
    url(r'^activate/complete/$',
        direct_to_template,
            {'template': 'registration/activation_complete.html'},
        name='registration_activation_complete'),
    # Activation keys get matched by \w+ instead of the more specific
    # [a-fA-F0-9]{40} because a bad activation key should still get to the view;
    # that way it can return a sensible "invalid key" message instead of a
    # confusing 404.
    url(r'^activate/(?P<activation_key>\w+)/$',
        activate,
            {'backend': 'registration.backends.default.DefaultBackend'},
        name='registration_activate'),
    url(r'^register/$',
        register,
            {'backend': 'registration.backends.default.DefaultBackend'},
        name='registration_register'),
    url(r'^register/complete/$',
        direct_to_template,
            {'template': 'registration/registration_complete.html'},
        name='registration_complete'),
    url(r'^register/closed/$',
        direct_to_template,
            {'template': 'registration/registration_closed.html'},
        name='registration_disallowed'),
    #(r'', include('registration.auth_urls')),
    #registration auth_urls put in here manually for customization
    url(r'^login/$',
        auth_views.login,
            {'template_name': 'registration/login.html'},
        name='auth_login'),
    url(r'^logout/$',
        auth_views.logout,
            {'template_name': 'registration/logout.html'},
        name='auth_logout'),
    url(r'^password/change/$',
        auth_views.password_change,
        {'template_name': 'registration/password_change.html'},
        name='auth_password_change'),
    url(r'^password/change/done/$',
        auth_views.password_change_done,
        name='auth_password_change_done'),
    url(r'^password/reset/$',
        auth_views.password_reset,
        {'template_name': 'registration/password_reset_form_carehq.html'},
        name='auth_password_reset'),
    url(r'^password/reset/confirm/(?P<uidb36>[0-9A-Za-z]+)-(?P<token>.+)/$',
        auth_views.password_reset_confirm,
        name='auth_password_reset_confirm'),
    url(r'^password/reset/complete/$',
        auth_views.password_reset_complete,
        name='auth_password_reset_complete'),
    url(r'^password/reset/done/$',
        auth_views.password_reset_done,
        name='auth_password_reset_done'),
)
