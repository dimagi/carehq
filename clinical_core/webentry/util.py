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
    source: http://stackoverflow.com/questions/1020892/urllib2-read-to-unicode
    """
    req = urllib2.urlopen(xform_url)
    #encoding = req.headers['content-type'].split('charset=')[-1]
    encoding = "windows-1251"
    content = req.read()
    ucontent = unicode(content, encoding)
#    return ucontent.encode('utf-8')

#    filename = xform_url.split('/')[-1]
#    fin = open('/home/dmyung/src/commcare-sets/shine/%s' % filename)
#    content = fin.read()
#    ucontent = unicode(content, 'windows-1251')
    return ucontent.encode('utf-8')
