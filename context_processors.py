from django.conf import settings
import sys

def base_template( request ):
    """This sticks the base_template variable defined in the settings
       into the request context, so that we don't have to do it in 
       our render_to_response override."""
    if hasattr(settings, "BASE_TEMPLATE"):
        return {"base_template" : settings.BASE_TEMPLATE}
    # we assume that anything using this is smart enough to set it  
    return {}
