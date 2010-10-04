from django.core import serializers
import sys
            
def run():
    filename = sys.argv[-1]
    
    fin = open(filename, 'r')
    strfile = fin.read()    
    fin.close()
    for obj in serializers.deserialize('json', strfile):               
        try:
            pass
            obj.save()
        except Exception, e:            
            print "%s Exception: %s" % (obj, e)