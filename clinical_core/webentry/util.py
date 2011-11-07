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
    punctuation = { 0x2018:0x27, 0x2019:0x27, 0x201C:0x22, 0x201D:0x22 }

    req = urllib2.urlopen(xform_url)
    encoding ='utf8'
    content = req.read()
    ucontent = unicode(content, encoding)
    return ucontent.translate(punctuation)
