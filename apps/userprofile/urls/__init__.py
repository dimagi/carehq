from django.conf import settings
from django.conf.urls.defaults import *

if hasattr(settings, "I18N_URLS") and settings.I18N_URLS:
    try:
        module = __import__("userprofile.urls.%s" % (settings.LANGUAGE_CODE), \
                            {}, {}, "urlpatterns")
        globals().update({ "urlpatterns": module.__dict__["urlpatterns"] })
    except:
        module = __import__("userprofile.urls.en", {}, {}, "urlpatterns")
        globals().update({ "urlpatterns": module.__dict__["urlpatterns"] })
else:
    module = __import__("userprofile.urls.en", {}, {}, "urlpatterns")
    globals().update({ "urlpatterns": module.__dict__["urlpatterns"] })
