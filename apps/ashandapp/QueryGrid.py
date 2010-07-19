from django.http import HttpResponse,HttpResponseNotAllowed
import re
nonalpha_re = re.compile('[^A-Z]')

#from http://www.djangosnippets.org/snippets/437/
class QueryGridBase(object):
    def __init__(self, div_name, title, columns=None, json_view=None, template='ashandapp/cases/bare_query.html', *args, **kwargs):
        self.div_name = div_name
        self.title = title
        if columns:
            self.columns=columns
        else:
            self.columns = ['id','__unicode__']        
        if json_view:
            self.json = json_view
        else:
            self.json = self.div_name +"?json"
        
        self.template = template
        print "super init"
        print self.columns
        
    def __call__(self, request, *args, **kw):
        # try and find a handler for the given HTTP method
        method = request.META['REQUEST_METHOD'].upper()
        handler = getattr(self, 'handle_%s' % method, None)

        if handler is None:
            # compile a list of all our methods and return an HTTP 405
            methods = []
            for x in dir(self):
                if x.startswith('handle_'):
                    methods.append(x[7:])
            return HttpResponseNotAllowed(methods)

        return handler(request, *args, **kw)