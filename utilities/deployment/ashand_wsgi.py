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

os.environ['DJANGO_SETTINGS_MODULE'] = 'ashand.settings'

import django.core.handlers.wsgi
application = django.core.handlers.wsgi.WSGIHandler()
