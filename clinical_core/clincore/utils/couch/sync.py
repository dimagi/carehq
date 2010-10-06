from django.conf import settings
from couchdbkit.client import Server
from bhoma import const
from bhoma.apps.locations.models import Location
import json


def pull_from_national_to_local(continuous=False):
    """ 
    Pull data from a remote nationally-configured database to a local one
    """ 
    server = Server(settings.BHOMA_COUCH_SERVER)
    
    source = _get_national_db_from_settings()
    # NEVER use the full URL for the local database just the name
    # otherwise couch gets confused
    target = settings.BHOMA_COUCH_DATABASE_NAME
    
    # This will fail if poorly configured.  That's fine, we want it to.
    current_site = Location.objects.get(slug__iexact=settings.BHOMA_CLINIC_ID)
    if current_site.type.slug == const.LOCATION_TYPE_NATIONAL or \
       current_site.type.slug == const.LOCATION_TYPE_PROVINCE:
        # for national or provincial sync (for now) we just do full bi-directional
        return replicate(server, source, target, continuous)
    elif current_site.type.slug == const.LOCATION_TYPE_DISTRICT:
        filter = const.FILTER_DISTRICT
        clinic_ids = list(Location.objects.filter(parent=current_site).\
                          values_list("slug", flat=True).distinct())
        
        clinic_ids.append(current_site.slug)
        clinic_id_param = "|".join(clinic_ids)
        query_params = { "clinic_ids": clinic_id_param }
    elif current_site.type.slug == const.LOCATION_TYPE_CLINIC:
        filter = const.FILTER_CLINIC
        query_params = { "clinic_id": settings.BHOMA_CLINIC_ID }
    else:
        raise Exception("can't sync from location type: %s! It is not a known type!" )
    return replicate(server, source, target, continuous, filter, query_params)

def push_from_local_to_national(continuous=False):
    """ 
    Push data from the local database to the nationally-configured one
    """
    # everything moves up so no options required here
    server = Server(settings.BHOMA_COUCH_SERVER)
    source = settings.BHOMA_COUCH_DATABASE_NAME
    target = _get_national_db_from_settings()
    return replicate(server, source, target, continuous)


def replicate(server, source, target, continuous=False, filter="", query_params={}):
    replication_params = {"source": source, 
                          "target": target,
                          "continuous": continuous,
                          "filter": filter,
                          "query_params": query_params
    }
    result = server.res.post('/_replicate', payload=replication_params)
    return result

def cancel_replication(server, source, target):
    replication_params = {"source": source, 
                          "target": target,
                          "continuous": True,
                          "cancel": True
    }
    result = server.res.post('/_replicate', payload=replication_params)
    return result

def _get_national_db_from_settings():
    # sync is really finicky with authentication urls so a little magic
    # is required to make this work smoothly in all cases.
    # for testing, if the national and local database are on the 
    # same (local) couch instance don't use the full URL in the target,
    # because it blows up.
    if settings.BHOMA_COUCH_SERVER == settings.BHOMA_NATIONAL_SERVER:
        return settings.BHOMA_NATIONAL_DATABASE_NAME
    else:
        return settings.BHOMA_NATIONAL_DATABASE    
    
