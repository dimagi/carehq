import os
import sys
import cherrypy
from cherrypy import wsgiserver
import logging

filedir = os.path.dirname(__file__)

rootpath = os.path.join(filedir, "..", "..") 
sys.path.append(os.path.join(rootpath))
sys.path.append(os.path.join(rootpath,'..'))
sys.path.append(os.path.join(rootpath,'apps'))
sys.path.append(os.path.join(rootpath,'lib'))
sys.path.append(os.path.join(rootpath,'rapidsms','apps'))

#rapidsms lib stuff
sys.path.append(os.path.join(rootpath,'rapidsms','lib'))
sys.path.append(os.path.join(rootpath,'rapidsms','lib','rapidsms'))
sys.path.append(os.path.join(rootpath,'rapidsms','lib','rapidsms','webui'))

os.environ['DJANGO_SETTINGS_MODULE'] = 'ashand.settings'


import django.core.handlers.wsgi
application = django.core.handlers.wsgi.WSGIHandler()

server = wsgiserver.CherryPyWSGIServer(
    ('0.0.0.0', 8000),  # Use '127.0.0.1' to only bind to the localhost
    django.core.handlers.wsgi.WSGIHandler()
)

try:        
    
    logging.info("Starting media runtime...")
    server.start()                        
except KeyboardInterrupt:
    logging.info("Keyboard interrupt, shutting down mediaserver")
    logging.info("Mediaserver shutdown successful")
