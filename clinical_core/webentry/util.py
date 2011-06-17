
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
