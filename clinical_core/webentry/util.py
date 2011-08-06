import urllib2

def shared_preloaders():
    """
    Shared preloaders.
    """
    return {"property": { "DeviceID": "touchforms"}}

def user_meta_preloaders(user):
    """
    Meta block preloaders for a user
    """
    return {"meta": {"UserID": '%d' % (user.id),
                     "UserName": user.username}}

def get_remote_form(xform_url):
    """
    Get a remote form from a url
    """
    url_resp = urllib2.urlopen(xform_url)
    return url_resp.read().decode('utf-8')
    