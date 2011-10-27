"""
This is a Custom Storage System for Django with CouchDB backend.
Created by Christian Klein.

Modified for storage WITHIN a document
(c) Copyright 2009 HUDORA GmbH. All Rights Reserved.
"""
from django.core.urlresolvers import reverse
import os
from cStringIO import StringIO
from urlparse import urljoin
from urllib import quote_plus

from django.conf import settings
from django.core.files import File
from django.core.files.storage import Storage
from django.core.exceptions import ImproperlyConfigured

try:
    import couchdb
except ImportError:
    raise ImproperlyConfigured, "Could not load couchdb dependency.\
    \nSee http://code.google.com/p/couchdb-python/"

DEFAULT_SERVER= getattr(settings, 'COUCHDB_DEFAULT_SERVER', 'http://couchdb.local:5984')
STORAGE_OPTIONS= getattr(settings, 'COUCHDB_STORAGE_OPTIONS', {})

def _split_file(name):
    return tuple(name.split('/'))

class CouchDBDocStorage(Storage):
    """
    CouchDBDocStorage - a Django Storage class for CouchDB.

    The CouchDBStorage can be configured in settings.py, e.g.::

        COUCHDB_STORAGE_OPTIONS = {
            'server': "http://example.org",
            'database': 'database_name'
        }

    Alternatively, the configuration can be passed as a dictionary.
    """


    def __init__(self, **kwargs):
        kwargs.update(STORAGE_OPTIONS)
        self.base_url = kwargs.get('server', DEFAULT_SERVER)
        server = couchdb.client.Server(self.base_url)
        self.db = server[kwargs.get('database')]

    def _put_file(self, name, content):
        doc_id, attachment_key=_split_file(name)

        self.db[doc_id] = {'size': len(content)}
        self.db.put_attachment(self.db[doc_id], content, filename=attachment_key)
        return doc_id

    def get_document(self, doc_id):
        return self.db.get(doc_id)

    def _open(self, name, mode='rb'):
        doc_id, attachment_key=_split_file(name)
        couchdb_file = CouchDBAttachmentFile(doc_id, attachment_key, self, mode=mode)
        return couchdb_file

    def _save(self, name, content):
        doc_id, attachment_key=_split_file(name)
        content.open()
        if hasattr(content, 'chunks'):
            content_str = ''.join(chunk for chunk in content.chunks())
        else:
            content_str = content.read()
        #name = name.replace('/', '-')
        return self._put_file(doc_id, attachment_key, content_str)

    def exists(self, name):
        doc_id, attachment_key=_split_file(name)
        if doc_id in self.db:
            return self.db.get(doc_id)._attachments.has_key(attachment_key)
        else:
            return False

    def size(self, name):
        doc_id, attachment_key=_split_file(name)
        doc = self.get_document(doc_id)
        if doc:
            return doc._attachments[attachment_key]['length']
        return 0

    def url(self, name):
        doc_id, attachment_key=_split_file(name)
#        return urljoin(self.base_url,
#                       os.path.join(quote_plus(self.db.name),
#                       quote_plus(name),
#                       'content'))
        return reverse('slidesview.views.image_proxy', kwargs={'doc_id': doc_id, 'attachment_key': attachment_key})

    def delete(self, name):
        doc_id, attachment_key=_split_file(name)
        try:
            doc = self.get_document(doc_id)
            del doc._attachments[attachment_key]
        except Exception, ex:
            print "Ex: %s" % ex
            raise IOError("File not found: %s" % name)

    #def listdir(self, name):
    # _all_docs?
    #    pass


class CouchDBAttachmentFile(File):
    """
    An adaptation of CouchDBFile - a Django File-like class for CouchDB documents.


    Only treats a known attachment to a document
    """

    def __init__(self, doc_id, attachment_key, storage, mode):
        self._doc_id = doc_id
        self._attachment_filename = attachment_key
        self._storage = storage
        self._mode = mode
        self._is_dirty = False

        try:
            print doc_id
            self._doc = self._storage.get_document(doc_id)
            print attachment_key
            attachment = self._storage.db.get_attachment(self._doc, filename=attachment_key)
            print "gotting attachment"
            self.file = StringIO(attachment.read())
            print "stringio"
        except Exception, ex:
        #except couchdb.client.ResourceNotFound:
            print "Error init couchdb attachment file: %s " % (ex)
            if 'r' in self._mode:
                raise ValueError("The file cannot be reopened.")
            else:
                self.file = StringIO()
                self._is_dirty = True

    @property
    def size(self):
        return self._doc._attachments[self._attachment_filename]['length']

    def write(self, content):
        if 'w' not in self._mode:
            raise AttributeError("File was opened for read-only access.")
        self.file = StringIO(content)
        self._is_dirty = True

    def close(self):
        if self._is_dirty:
            self._storage._put_file('%s/%s' % (self._doc_id, self._attachment_filename), self.file.getvalue())
        self.file.close()

