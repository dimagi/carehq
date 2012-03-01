####### Couch Forms & Couch DB Kit Settings #######
def get_couch_server_url(server_root, username, password):
    if username and password:
        return "http://%(user)s:%(pass)s@%(server)s" %\
               {"user": username,
                "pass": password,
                "server": server_root }
    else:
        return "http://%(server)s" % {"server": server_root }

def make_couch_database_url(url, database_name):
    """
    Make the default couch database url for the entire project.
    """
    return "%(server)s/%(database)s" % {"server": url, "database": database_name }


def make_couchdb_tuple(app_label, couch_database_url):
    """
    Helper function to generate couchdb tuples for mapping app name to couch database URL.

    In this case, the helper will magically alter the URL for special core libraries.

    Namely, auditcare, and couchlog
    """

    if app_label == 'auditcare' or app_label == 'couchlog':
        return app_label, "%s__%s" % (couch_database_url, app_label)
    else:
        return app_label, couch_database_url

