from gevent.server import StreamServer
import logging


#do get printers from server via rest
#cache printers and their IPs
#when receiving event, then lookup then set data strucutre and push over

def zebra_alert_handler(socket, address):
    try:
        fileobj = socket.makefile()
        while True:
            line = fileobj.readline()
            if not line:
                print ("client disconnected")
                break
            fileobj.write(line)
            fileobj.flush()
            print ("received %s :: %s" % (line.strip(), address))
            break
    except Exception, ex:
        logging.error("Unknown exception, gobbling up: %s", ex)
server = StreamServer(('0.0.0.0',9111), zebra_alert_handler) # creates a new server
server.serve_forever() # start accepting new connections

