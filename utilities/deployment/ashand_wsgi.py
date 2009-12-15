import os
import sys




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

#assuming that settings.py is the root where we are at.
os.environ['DJANGO_SETTINGS_MODULE'] = 'settings'

import django.core.handlers.wsgi
application = django.core.handlers.wsgi.WSGIHandler()
